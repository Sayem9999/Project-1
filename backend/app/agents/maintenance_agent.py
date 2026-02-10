import structlog
from typing import List, Dict, Any, Optional
from .introspection import introspection_service
from ..agents.base import BaseAgent
from ..config import settings

logger = structlog.get_logger()

class MaintenanceAgent(BaseAgent):
    """
    The 'Self-Healing' Agent.
    Monitors the system graph, detects anomalies, and auto-populates missing components.
    """
    
    def __init__(self):
        super().__init__(
            name="Maintenance",
            role="System Architect & Repair Specialist",
            goal="Maintain 100% codebase integrity and auto-scale features.",
            backstory="You are a meta-agent that lives inside the code. You see the project as a living graph."
        )

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution loop for maintenance tasks.
        payload: { "task": "heal" | "populate" | "audit", "context": ... }
        """
        task = payload.get("task", "audit")
        logger.info("maintenance_task_start", task=task)
        
        # 1. Get current system state
        graph = introspection_service.scan("backend/app")
        
        if task == "audit":
            return self._audit_codebase(graph)
        elif task == "heal":
            return await self._heal_error(payload.get("error_trace", ""), graph)
        elif task == "populate":
            return await self._populate_feature(payload.get("feature_request", ""), graph)
            
        return {"status": "unknown_task"}

    def _audit_codebase(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Find 'empty' or 'disconnected' nodes in the system."""
        issues = []
        
        # Example check: models without routers
        models = [n for n in graph["nodes"] if n["type"] == "model"]
        endpoints = [n for n in graph["nodes"] if n["type"] == "endpoint"]
        
        for model in models:
            model_name = model["label"].lower()
            matching = [e for e in endpoints if model_name in e["label"].lower()]
            if not matching:
                issues.append({
                    "type": "missing_router",
                    "target": model["id"],
                    "severity": "low",
                    "suggestion": f"Create CRUD endpoints for {model['label']}"
                })
                
        return {
            "graph": graph,
            "issues": issues,
            "integrity_score": max(0, 100 - len(issues) * 5)
        }

    async def _heal_error(self, error_trace: str, graph: Dict[str, Any]) -> Dict[str, Any]:
        """LLM-driven repair of a crash or bug."""
        from .base import run_agent_prompt
        
        system_prompt = f"""
        You are the ProEdit Maintenance Agent. Your goal is to HEAL a system error based on a stack trace and codebase map.
        
        SYSTEM CONTEXT:
        - Nodes: {len(graph['nodes'])}
        - Stats: {graph['stats']}
        
        Return a JSON object with:
        "analysis": "Short explanation of the root cause",
        "patch": "The full code for the fix",
        "target_file": "Path to the file to modify"
        """
        
        try:
            result = await run_agent_prompt(system_prompt, {"error_trace": error_trace}, task_type="complex")
            # In a real self-healing scenario, we would parse and apply this patch.
            # For this demo, we'll return the suggested fix.
            return {
                "status": "healing_analyzed",
                "recommendation": result.get("raw_response")
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _populate_feature(self, feature_request: str, graph: Dict[str, Any]) -> Dict[str, Any]:
        """LLM-driven feature scaffolding."""
        from .base import run_agent_prompt
        
        system_prompt = f"""
        You are the ProEdit Maintenance Agent. Your goal is to AUTO-POPULATE a new service or component based on a user request.
        
        SYSTEM CONTEXT:
        - Nodes: {len(graph['nodes'])}
        - Stats: {graph['stats']}
        
        Create a new Python file that integrates perfectly with the existing 'app' structure.
        Return a JSON object with:
        "filename": "Path to the new file (e.g., app/services/analytics.py)",
        "content": "The full source code of the new component"
        """
        
        try:
            result = await run_agent_prompt(system_prompt, {"feature_request": feature_request}, task_type="creative")
            # For safety in this demo, we return the plan instead of writing immediately
            return {
                "status": "population_scaffolded",
                "scaffold": result.get("raw_response")
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Global instance
maintenance_agent = MaintenanceAgent()
