import os
import ast
import copy
import time
import threading
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import structlog

from ..config import settings

logger = structlog.get_logger()
HTTP_ROUTE_DECORATORS = {"get", "post", "put", "patch", "delete", "options", "head"}


class IntrospectionService:
    """
    Advanced Self-Discovery Service.
    Parses codebase using AST to build a dependency graph (Nodes + Edges).
    Adds cache + self-heal behavior so graph endpoints remain responsive and auto-populating.
    """

    def __init__(self, root_dir: Optional[str] = None, cache_ttl_seconds: int = 300):
        if not root_dir:
            self.root_dir = str(Path(__file__).parent.parent.absolute())
        else:
            self.root_dir = root_dir

        self.cache_ttl_seconds = max(30, int(cache_ttl_seconds))
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []
        self.stats = {
            "source_files": 0,
            "total_nodes": 0,
            "total_edges": 0,
            "lines_of_code": 0,
        }
        self.node_ids: Set[str] = set()

        self.last_scan_at: float = 0.0
        self.last_error: str = ""
        self.scan_failures: int = 0
        self.scan_in_progress: bool = False
        self.last_integrity_score: int = 0
        self._scan_lock = threading.Lock()

    def get_live_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics using psutil."""
        try:
            import psutil

            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()

            metrics = {
                "system": {
                    "cpu_percent": cpu,
                    "memory_percent": mem.percent,
                    "memory_used_gb": round(mem.used / (1024**3), 2),
                    "memory_total_gb": round(mem.total / (1024**3), 2),
                },
                "processes": {},
            }

            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    cmd = " ".join(proc.info["cmdline"] or [])

                    if "celery" in cmd and "worker" in cmd:
                        metrics["processes"]["celery"] = {
                            "cpu": round(proc.cpu_percent(interval=None), 1),
                            "mem": round(proc.memory_percent(), 1),
                        }
                    elif "uvicorn" in cmd:
                        metrics["processes"]["api"] = {
                            "cpu": round(proc.cpu_percent(interval=None), 1),
                            "mem": round(proc.memory_percent(), 1),
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            return metrics

        except ImportError:
            logger.warning("psutil not installed, cannot get live metrics")
            return {}
        except Exception as e:
            logger.error("error_getting_metrics", error=str(e))
            return {}

    def scan(self, root_dir: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
        """Perform AST scan with cache, auto-population, and self-healing fallback."""
        if root_dir:
            self.root_dir = root_dir

        if not force and self.nodes and not self._is_stale():
            return self._snapshot()

        with self._scan_lock:
            if not force and self.nodes and not self._is_stale():
                return self._snapshot()

            logger.info("introspection_scan_start", root=self.root_dir, force=force)
            self.scan_in_progress = True

            previous_nodes = copy.deepcopy(self.nodes)
            previous_edges = copy.deepcopy(self.edges)
            previous_stats = copy.deepcopy(self.stats)
            previous_ids = set(self.node_ids)
            previous_scan_at = self.last_scan_at

            try:
                self.nodes = []
                self.edges = []
                self.node_ids = set()
                self.stats = {
                    "source_files": 0,
                    "total_nodes": 0,
                    "total_edges": 0,
                    "lines_of_code": 0,
                }

                for root, dirs, files in os.walk(self.root_dir):
                    if "__pycache__" in root:
                        continue

                    for file in files:
                        if file.endswith(".py"):
                            full_path = Path(root) / file
                            self._process_file(full_path)

                self._auto_populate_nodes()
                self._prune_dangling_edges()

                self.stats["total_nodes"] = len(self.nodes)
                self.stats["total_edges"] = len(self.edges)
                self.last_scan_at = time.time()
                self.scan_failures = 0
                self.last_error = ""
                self.last_integrity_score = self._compute_integrity_score(self._snapshot())
                return self._snapshot()
            except Exception as e:
                self.scan_failures += 1
                self.last_error = str(e)
                logger.error("introspection_scan_failed", error=str(e), failures=self.scan_failures)

                # Serve last known good snapshot when possible.
                if previous_nodes:
                    self.nodes = previous_nodes
                    self.edges = previous_edges
                    self.stats = previous_stats
                    self.node_ids = previous_ids
                    self.last_scan_at = previous_scan_at
                    return self._snapshot()
                raise
            finally:
                self.scan_in_progress = False

    def get_health_status(self) -> Dict[str, Any]:
        age = None
        if self.last_scan_at > 0:
            age = int(time.time() - self.last_scan_at)
        return {
            "scan_in_progress": self.scan_in_progress,
            "last_scan_at_unix": int(self.last_scan_at) if self.last_scan_at else None,
            "last_scan_age_seconds": age,
            "stale": self._is_stale(),
            "scan_failures": self.scan_failures,
            "last_error": self.last_error or None,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "last_integrity_score": self.last_integrity_score,
            "graph_nodes": len(self.nodes),
            "graph_edges": len(self.edges),
        }

    def self_heal(self) -> Dict[str, Any]:
        """Rebuild stale graph cache and return repair summary."""
        actions: List[str] = []
        before = self.get_health_status()
        needs_refresh = self._is_stale() or not self.nodes or self.scan_failures > 0

        if needs_refresh:
            actions.append("forced_refresh")
            graph = self.scan(force=True)
        else:
            graph = self.scan(force=False)

        integrity_score = self._compute_integrity_score(graph)
        self.last_integrity_score = integrity_score
        after = self.get_health_status()
        return {
            "status": "self_healed" if needs_refresh else "healthy",
            "actions": actions,
            "integrity_score": integrity_score,
            "before": before,
            "after": after,
            "graph": graph,
        }

    def _process_file(self, file_path: Path):
        """Parse a single file to extract nodes and edge dependencies."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            self.stats["source_files"] += 1
            self.stats["lines_of_code"] += len(content.splitlines())

            rel_path = file_path.relative_to(self.root_dir).as_posix()
            module_id = f"module:{rel_path}"

            node_type = "module"
            if "routers/" in rel_path:
                node_type = "router"
            elif "services/" in rel_path:
                node_type = "service"
            elif "models" in rel_path:
                node_type = "model"
            elif "agents/" in rel_path:
                node_type = "agent"

            self._add_node(module_id, node_type, file_path.stem, str(file_path))

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        target = node.module.split(".")[-1]
                        self._add_edge_by_name(module_id, target, "import")

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        target = alias.name.split(".")[-1]
                        self._add_edge_by_name(module_id, target, "import")

                elif isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        target_name = node.value.id
                        self._add_edge_by_name(module_id, target_name, "call")

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_id = f"class:{node.name}"
                    self._add_node(class_id, "class", node.name)
                    self._add_edge(module_id, class_id, "contains")

                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == "Base":
                            self.nodes[-1]["type"] = "model"
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for decorator in node.decorator_list:
                        endpoint = self._extract_endpoint(decorator)
                        if not endpoint:
                            continue

                        method, route_path = endpoint
                        endpoint_id = f"endpoint:{rel_path}:{node.name}:{method}:{route_path}"
                        endpoint_label = f"{method} {route_path}"
                        self._add_node(endpoint_id, "endpoint", endpoint_label)
                        self._add_edge(module_id, endpoint_id, "contains")

        except Exception as e:
            logger.warning("introspection_file_parse_failed", file=str(file_path), error=str(e))

    def _add_node(self, node_id: str, node_type: str, label: str, file_path: str = ""):
        if node_id in self.node_ids:
            return
        self.node_ids.add(node_id)

        color_map = {
            "router": "#ff6b6b",
            "service": "#4ecdc4",
            "agent": "#ffe66d",
            "model": "#ff9f43",
            "endpoint": "#54a0ff",
            "module": "#a55eea",
            "class": "#ced6e0",
            "integration": "#2ed573",
            "config": "#f8c291",
            "external_api": "#70a1ff",
        }

        self.nodes.append(
            {
                "id": node_id,
                "type": node_type,
                "label": label,
                "color": color_map.get(node_type, "#ffffff"),
                "val": 5 if node_type == "module" else 10,
            }
        )

    def _add_edge_by_name(self, source_id: str, target_name: str, edge_type: str):
        """Try to find a node with label == target_name and link it."""
        for node in self.nodes:
            if node["label"] == target_name and node["id"] != source_id:
                self._add_edge(source_id, node["id"], edge_type)

    def _add_edge(self, source: str, target: str, type_str: str):
        if source == target:
            return

        for e in self.edges:
            if e["source"] == source and e["target"] == target:
                return

        self.edges.append(
            {
                "source": source,
                "target": target,
                "type": type_str,
            }
        )

    def _extract_endpoint(self, decorator: ast.expr) -> Optional[tuple[str, str]]:
        """Extract (METHOD, route_path) from FastAPI route decorators like @router.get('/x')."""
        if not isinstance(decorator, ast.Call):
            return None
        if not isinstance(decorator.func, ast.Attribute):
            return None
        if decorator.func.attr not in HTTP_ROUTE_DECORATORS:
            return None

        route_path = "/"
        if decorator.args:
            arg0 = decorator.args[0]
            if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                route_path = arg0.value

        return decorator.func.attr.upper(), route_path

    def _is_stale(self) -> bool:
        if self.last_scan_at <= 0:
            return True
        return (time.time() - self.last_scan_at) > self.cache_ttl_seconds

    def _snapshot(self) -> Dict[str, Any]:
        return {
            "nodes": copy.deepcopy(self.nodes),
            "edges": copy.deepcopy(self.edges),
            "stats": copy.deepcopy(self.stats),
        }

    def _prune_dangling_edges(self) -> None:
        valid = self.node_ids
        self.edges = [e for e in self.edges if e["source"] in valid and e["target"] in valid]

    def _auto_populate_nodes(self) -> None:
        """Add synthetic config/integration nodes so the graph reflects live capabilities."""
        runtime_nodes: List[tuple[str, str, str]] = []
        if settings.redis_url:
            runtime_nodes.append(("config:redis", "config", "Redis Broker"))
        if settings.database_url:
            runtime_nodes.append(("config:database", "config", "Primary Database"))
        if settings.r2_account_id and settings.r2_bucket_name:
            runtime_nodes.append(("integration:r2", "integration", "Cloudflare R2"))
        if settings.modal_token_id and settings.modal_token_secret:
            runtime_nodes.append(("integration:modal", "integration", "Modal GPU"))
        if settings.gemini_api_key:
            runtime_nodes.append(("external_api:gemini", "external_api", "Gemini API"))
        if settings.groq_api_key:
            runtime_nodes.append(("external_api:groq", "external_api", "Groq API"))
        if settings.openai_api_key:
            runtime_nodes.append(("external_api:openai", "external_api", "OpenAI API"))

        for node_id, node_type, label in runtime_nodes:
            self._add_node(node_id, node_type, label)

        main_module_id = "module:main.py"
        if main_module_id in self.node_ids:
            for node_id, _, _ in runtime_nodes:
                self._add_edge(main_module_id, node_id, "config")

        llm_agent_module = "module:agents/base.py"
        if llm_agent_module in self.node_ids:
            for node_id, _, _ in runtime_nodes:
                if node_id.startswith("external_api:"):
                    self._add_edge(llm_agent_module, node_id, "api_call")

    def _compute_integrity_score(self, graph: Dict[str, Any]) -> int:
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        node_ids = {n.get("id") for n in nodes}
        dangling = sum(
            1
            for e in edges
            if e.get("source") not in node_ids or e.get("target") not in node_ids
        )
        connected = set()
        for edge in edges:
            connected.add(edge.get("source"))
            connected.add(edge.get("target"))
        isolated = sum(1 for node in nodes if node.get("id") not in connected)
        penalty = (dangling * 15) + min(isolated, 25)
        return max(0, 100 - penalty)


# Global instance
introspection_service = IntrospectionService()
