import structlog
from typing import Dict, Any
from .base import run_agent_prompt

logger = structlog.get_logger()

class BackendAgent:
    """
    The Backend Specialist.
    Expert in Python, FastAPI, SQLAlchemy, Celery, and System Architecture.
    """

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        query = payload.get("query", "")
        context = payload.get("context", "")
        
        system_prompt = """
        You are the ProEdit Backend Agent. You are an expert in:
        - Python 3.11+ (AsyncIO, Typing)
        - FastAPI (Routing, Dependencies, Pydantic)
        - SQLAlchemy (Async ORM, Alembic Migrations)
        - Celery (Background Tasks, Redis)
        - OpenAI/LLM Integration

        Your goal is to provide robust backend logic, API designs, or database schemas.
        
        GUIDELINES:
        1. Ensure all I/O is async.
        2. Use Pydantic schemas for data validation.
        3. Follow RESTful API design principles.
        4. Handle exceptions gracefully and log errors.
        """

        try:
            full_messages = f"Context: {context}\n\nQuery: {query}"
            result = await run_agent_prompt(system_prompt, {"content": full_messages}, task_type="complex", agent_name="backend_agent")
            
            return {
                "status": "success",
                "response": result.get("raw_response"),
                "model": result.get("model")
            }
        except Exception as e:
            logger.error("backend_agent_failed", error=str(e))
            return {"status": "error", "message": str(e)}

backend_agent = BackendAgent()
