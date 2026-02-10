import os
import re
import ast
from typing import List, Dict, Any, Optional
from pathlib import Path
import structlog

logger = structlog.get_logger()

class IntrospectionService:
    """
    Self-discovery service that maps the codebase into a graph of nodes and edges.
    Powers the 'self-healing' and 'auto-populating' engine.
    """
    
    def __init__(self, root_dir: str = "app"):
        self.root_dir = root_dir
        self.nodes = []
        self.edges = []
        self.stats = {
            "source_files": 0,
            "total_nodes": 0,
            "total_edges": 0,
            "lines_of_code": 0
        }

    def scan(self, root_dir: Optional[str] = None) -> Dict[str, Any]:
        """Perform full scan of the codebase."""
        if root_dir:
            self.root_dir = root_dir
        logger.info("introspection_scan_start", root=self.root_dir)
        
        self.nodes = []
        self.edges = []
        self.stats = {"source_files": 0, "total_nodes": 0, "total_edges": 0, "lines_of_code": 0}
        
        # 1. Map Routers (Endpoints)
        self._map_routers()
        
        # 2. Map Models (Database Tables)
        self._map_models()
        
        # 3. Map Services
        self._map_services()
        
        # 4. Map Agents
        self._map_agents()
        
        # Update stats
        self.stats["total_nodes"] = len(self.nodes)
        self.stats["total_edges"] = len(self.edges)
        
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "stats": self.stats
        }

    def _map_routers(self):
        router_path = Path(self.root_dir) / "routers"
        if not router_path.exists(): return
        
        for file in router_path.glob("*.py"):
            if file.name == "__init__.py": continue
            self.stats["source_files"] += 1
            
            content = file.read_text(encoding="utf-8")
            self.stats["lines_of_code"] += len(content.splitlines())
            
            # Find routes
            matches = re.finditer(r'@router\.(get|post|put|delete|patch)\("([^"]+)"', content)
            for match in matches:
                method = match.group(1).upper()
                path = match.group(2)
                node_id = f"endpoint:{method}:{path}"
                
                self.nodes.append({
                    "id": node_id,
                    "type": "endpoint",
                    "label": f"{method} {path}",
                    "file": str(file)
                })
                
                # Look for DB interactions in this endpoint block
                # (Simple heuristic: look for 'session' calls in the function following the decorator)
                if "session." in content:
                    # Logic to find which function this belongs to and link to models
                    pass

    def _map_models(self):
        models_file = Path(self.root_dir) / "models.py"
        if not models_file.exists(): return
        
        content = models_file.read_text(encoding="utf-8")
        self.stats["lines_of_code"] += len(content.splitlines())
        self.stats["source_files"] += 1
        
        # Find SQLAlchemy classes
        matches = re.finditer(r'class (\w+)\(Base\):', content)
        for match in matches:
            model_name = match.group(1)
            node_id = f"model:{model_name}"
            
            self.nodes.append({
                "id": node_id,
                "type": "model",
                "label": model_name,
                "file": str(models_file)
            })

    def _map_services(self):
        services_dir = Path(self.root_dir) / "services"
        if not services_dir.exists(): return
        
        for file in services_dir.glob("*.py"):
            if file.name == "__init__.py": continue
            self.stats["source_files"] += 1
            content = file.read_text(encoding="utf-8")
            self.stats["lines_of_code"] += len(content.splitlines())
            
            # Find classes that look like services
            matches = re.finditer(r'class (\w+):', content)
            for match in matches:
                service_name = match.group(1)
                self.nodes.append({
                    "id": f"service:{service_name}",
                    "type": "service",
                    "label": service_name,
                    "file": str(file)
                })

    def _map_agents(self):
        agents_dir = Path(self.root_dir) / "agents"
        if not agents_dir.exists(): return
        
        for file in agents_dir.glob("*.py"):
            if file.name == "__init__.py": continue
            self.stats["source_files"] += 1
            content = file.read_text(encoding="utf-8")
            self.stats["lines_of_code"] += len(content.splitlines())
            
            # Logic for mapping agents
            self.nodes.append({
                "id": f"agent:{file.stem}",
                "type": "agent",
                "label": file.stem.replace("_", " ").title(),
                "file": str(file)
            })

# Global instance
introspection_service = IntrospectionService()
