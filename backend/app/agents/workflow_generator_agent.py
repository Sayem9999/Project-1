import structlog
from typing import Dict, Any
from .base import run_agent_prompt

logger = structlog.get_logger()

class WorkflowGeneratorAgent:
    """
    The n8n Workflow Architect.
    Specializes in generating valid n8n JSON structures based on technical descriptions.
    """

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        description = payload.get("description", "")
        if not description:
            return {"status": "error", "message": "Description required"}

        logger.info("workflow_generation_start", description=description)

        system_prompt = """
        You are an expert n8n Workflow Engineer. 
        Your task is to generate a VALID, IMPORTABLE n8n JSON workflow based on the user's requirements.

        N8N SCHEMA RULES:
        1. The output MUST be a JSON object with two top-level keys: "nodes" (array) and "connections" (object).
        2. Every node must have: "parameters", "id", "name", "type", "typeVersion", "position".
        3. Position should be an array [x, y], e.g., [100, 200].
        4. "connections" keys should be node names, containing outputs ('main' array).

        COMMON NODES:
        - n8n-nodes-base.webhook (HTTP Trigger)
        - n8n-nodes-base.httpRequest (For API calls - USE THIS for Gemini/AI steps unless native nodes are specifically requested, as it's more compatible)
        - n8n-nodes-base.wait (Delay)
        - n8n-nodes-base.set (Variables)
        - n8n-nodes-base.executeCommand (For FFmpeg or local scripts)

        AI INTEGRATION (UNIVERSAL):
        When using Gemini via HTTP Request:
        - URL: https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={{$node["Config"].json["api_key"]}}
        - Method: POST
        - Body: {"contents": [{"parts": [{"text": "PROMPT_HERE"}]}]}

        CONTEXT:
        The workflow is for ProEdit, an AI video editor. It usually involves receiving a job_id, downloading media, running processing, and notifying a callback.

        USER REQUEST:
        {description}

        OUTPUT FORMAT:
        Return ONLY the valid JSON block. No markdown markers unless requested.
        """

        try:
            result = await run_agent_prompt(system_prompt, {"description": description}, task_type="creative")
            
            # Extract JSON from potential markdown wrapping
            raw_response = result.get("raw_response", "")
            json_str = raw_response
            if "```json" in raw_response:
                json_str = raw_response.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_response:
                json_str = raw_response.split("```")[1].split("```")[0].strip()

            return {
                "status": "success",
                "workflow_json": json_str,
                "explanation": "Generated n8n workflow based on your requirements."
            }
        except Exception as e:
            logger.error("workflow_generator_error", error=str(e))
            return {"status": "error", "message": str(e)}

workflow_generator_agent = WorkflowGeneratorAgent()

async def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    return await workflow_generator_agent.run(payload)
