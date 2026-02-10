import os
import re
import ast
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import structlog

logger = structlog.get_logger()

class IntrospectionService:
    """
    Advanced Self-Discovery Service.
    Parses codebase using AST to build a dependency graph (Nodes + Edges).
    """
    
    def __init__(self, root_dir: Optional[str] = None):
        if not root_dir:
            self.root_dir = str(Path(__file__).parent.parent.absolute())
        else:
            self.root_dir = root_dir
            
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []
        self.stats = {
            "source_files": 0,
            "total_nodes": 0,
            "total_edges": 0,
            "lines_of_code": 0
        }
        self.node_ids: Set[str] = set()

    def scan(self, root_dir: Optional[str] = None) -> Dict[str, Any]:
        """Perform full AST scan of the codebase."""
        if root_dir:
            self.root_dir = root_dir
        
        logger.info("introspection_scan_start", root=self.root_dir)
        
        # Reset
        self.nodes = []
        self.edges = []
        self.node_ids = set()
        self.stats = {"source_files": 0, "total_nodes": 0, "total_edges": 0, "lines_of_code": 0}
        
        # 1. Scan all Python files
        for root, dirs, files in os.walk(self.root_dir):
            if "__pycache__" in root: continue
            
            for file in files:
                if file.endswith(".py"):
                    full_path = Path(root) / file
                    self._process_file(full_path)

        # Update stats
        self.stats["total_nodes"] = len(self.nodes)
        self.stats["total_edges"] = len(self.edges)
        
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "stats": self.stats
        }

    def _process_file(self, file_path: Path):
        """Parse a single file to extract nodes and edge dependencies."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            self.stats["source_files"] += 1
            self.stats["lines_of_code"] += len(content.splitlines())
            
            # Identify "Module" Node (The File itself)
            rel_path = file_path.relative_to(self.root_dir).as_posix()
            module_id = f"module:{rel_path}"
            
            # Determine type based on folder
            node_type = "module"
            if "routers/" in rel_path: node_type = "router"
            elif "services/" in rel_path: node_type = "service"
            elif "models" in rel_path: node_type = "model"
            elif "agents/" in rel_path: node_type = "agent"
            
            self._add_node(module_id, node_type, file_path.stem, str(file_path))
            
            # AST Parsing
            tree = ast.parse(content)
            
            # 1. Imports -> Dependencies (Edges)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        # "from app.services.audio_service import ..."
                        target = node.module.split(".")[-1]
                        # Heuristic: connect to any node that matches this name
                        self._add_edge_by_name(module_id, target, "import")

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        target = alias.name.split(".")[-1]
                        self._add_edge_by_name(module_id, target, "import")
                        
                # 2. Function calls / Class usage (Heuristic)
                # If code says "audio_service.process()", link to audio_service
                elif isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        target_name = node.value.id
                        self._add_edge_by_name(module_id, target_name, "call")
                        
            # 3. Detect Classes (Sub-nodes)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_id = f"class:{node.name}"
                    self._add_node(class_id, "class", node.name)
                    self._add_edge(module_id, class_id, "contains")
                    
                    # Special: SQLAlchemy Models
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == "Base":
                             self.nodes[-1]["type"] = "model" # Update last node

        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")

    def _add_node(self, node_id: str, node_type: str, label: str, file_path: str = ""):
        if node_id in self.node_ids: return
        self.node_ids.add(node_id)
        
        # Color mapper
        color_map = {
            "router": "#ff6b6b",   # Red
            "service": "#4ecdc4",  # Cyan
            "agent": "#ffe66d",    # Yellow
            "model": "#ff9f43",    # Orange
            "module": "#a55eea",   # Purple
            "class": "#ced6e0"     # Gray
        }
        
        self.nodes.append({
            "id": node_id,
            "type": node_type,
            "label": label,
            "color": color_map.get(node_type, "#ffffff"),
            "val": 5 if node_type == "module" else 10 # Size
        })

    def _add_edge_by_name(self, source_id: str, target_name: str, edge_type: str):
        """Try to find a node with 'label' == target_name and link it."""
        for node in self.nodes:
            if node["label"] == target_name and node["id"] != source_id:
                self._add_edge(source_id, node["id"], edge_type)

    def _add_edge(self, source: str, target: str, type_str: str):
        # Prevent self-loops
        if source == target: return
        
        # Check duplicate
        for e in self.edges:
            if e["source"] == source and e["target"] == target:
                return
                
        self.edges.append({
            "source": source,
            "target": target,
            "type": type_str
        })

# Global instance
introspection_service = IntrospectionService()
