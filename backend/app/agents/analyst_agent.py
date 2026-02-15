import structlog
from typing import Dict, Any
from .base import run_agent_prompt

logger = structlog.get_logger()

class AnalystAgent:
    """
    The Systems Analyst.
    Expert in Requirements Analysis, Schema Design, Data Modeling, and Workflow Optimization.
    """

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        query = payload.get("query", "")
        context = payload.get("context", "")
        
        system_prompt = """
        You are the ProEdit Analyst Agent. You are an expert in:
        - Systems Analysis & Architecture
        - Database Schema Design (Relational Models)
        - Workflow Optimization
        - Requirement Gathering & Breakdown
        - Data Consistency & integrity

        Your goal is to analyze specific problems, propose structural solutions, or critique existing designs.
        
        GUIDELINES:
        1. Focus on scalability and maintainability.
        2. Identify edge cases and potential bottlenecks.
        3. Propose clear, actionable steps or specifications.
        """

        try:
            full_messages = f"Context: {context}\n\nQuery: {query}"
            result = await run_agent_prompt(system_prompt, {"content": full_messages}, task_type="reasoning", agent_name="analyst_agent")
            
            return {
                "status": "success",
                "response": result.get("raw_response"),
                "model": result.get("model")
            }
        except Exception as e:
            logger.error("analyst_agent_failed", error=str(e))
            return {"status": "error", "message": str(e)}

analyst_agent = AnalystAgent()
