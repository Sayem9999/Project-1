import structlog
from typing import Dict, Any
from .base import run_agent_prompt

logger = structlog.get_logger()

class FrontendAgent:
    """
    The Frontend Specialist.
    Expert in Next.js, React 19, TailwindCSS, and UI/UX Design.
    """

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        query = payload.get("query", "")
        context = payload.get("context", "")
        
        system_prompt = """
        You are the ProEdit Frontend Agent. You are an expert in:
        - Next.js (App Router)
        - React 19 (Server Components, Hooks)
        - TailwindCSS (Styling, Responsive Design)
        - Lucide React (Icons)
        - UI/UX Best Practices (Glassmorphism, Dark Mode)

        Your goal is to provide high-quality frontend code, debugging advice, or UI verification.
        
        GUIDELINES:
        1. Always use functional components with TypeScript interfaces.
        2. Prefer 'use client' only when interactivity is needed.
        3. Use Tailwind utility classes for styling.
        4. Ensure accessibility (ARIA attributes).
        """

        try:
            full_messages = f"Context: {context}\n\nQuery: {query}"
            result = await run_agent_prompt(system_prompt, {"content": full_messages}, task_type="creative", agent_name="frontend_agent")
            
            return {
                "status": "success",
                "response": result.get("raw_response"),
                "model": result.get("model")
            }
        except Exception as e:
            logger.error("frontend_agent_failed", error=str(e))
            return {"status": "error", "message": str(e)}

frontend_agent = FrontendAgent()
