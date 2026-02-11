import asyncio
import structlog
from typing import Dict, Any
from ..services.introspection import introspection_service
from .base import run_agent_prompt

logger = structlog.get_logger()

class ArchitectAgent:
    """
    The System Architect.
    Uses the system graph (AST-based) to provide context-aware answers to user queries.
    """

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        query = payload.get("query", "")
        if not query:
            return {"status": "error", "message": "Query required"}
            
        logger.info("architect_query_start", query=query)
        
        # 1. Get current system state - Offloaded to thread to avoid blocking event loop
        graph = await asyncio.to_thread(introspection_service.scan)
        
        # 2. Prepare Context (Flatten graph for prompt)
        # Limit to avoid token overflow? For now, assume graph fits.
        nodes_summary = "\n".join([f"- {n['id']} ({n['type']}): {n['label']}" for n in graph["nodes"]])
        edges_summary = "\n".join([f"- {e['source']} -> {e['target']} ({e['type']})" for e in graph["edges"]])
        
        system_prompt = f"""
        You are the Lead System Architect for this codebase.
        
        SYSTEM CONTEXT:
        The system is visualized as a graph of nodes (files, classes, services) and edges (dependencies).
        
        NODES:
        {nodes_summary}
        
        EDGES:
        {edges_summary}
        
        USER QUERY:
        {query}
        
        YOUR TASK:
        Analyze the query in the context of the system architecture.
        Provide a specific, technical plan or explanation.
        Reference existing specific file paths and class names from the graph.
        If the user asks to add a feature, tell them exactly which files to modify and what new files to create.
        """
        
        try:
            # Re-use run_agent_prompt helper (using 'analytical' for better provider routing)
            result = await run_agent_prompt(system_prompt, {"query": query}, task_type="analytical")
            return {
                "status": "success",
                "answer": result.get("raw_response", "No response generated")
            }
        except Exception as e:
            logger.error("architect_error", error=str(e))
            return {"status": "error", "message": str(e)}

architect_agent = ArchitectAgent()

async def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    return await architect_agent.run(payload)
