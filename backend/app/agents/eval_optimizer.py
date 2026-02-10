"""
Eval Optimizer Agent - EVAL
Technical and aesthetic evaluation of the edit plan.
"""
from .base import run_agent_with_schema
from .schemas import EvalOutput

PROMPT = """You are **EVAL**, the Lead Optimization Engineer at Proedit Studios.

Your task is to conduct a multi-dimensional evaluation of the edit plan.

## Input Context:
- Technical Metadata: {media_intelligence}
- User Request: {user_request}
- Specialized Plans: (Hook: {hook_result}, Platform: {platform_result})
- Complete Edit Plan: (Cuts: {cuts}, Audio: {audio_tracks})

## REQUIRED OUTPUT FORMAT (JSON ONLY):
Return EXCLUSIVELY a JSON object. Do NOT nest it under an "evaluation" key.

{{
  "overall_score": 8,
  "scores": [
    {{
      "category": "Technical",
      "score": 9,
      "reason": "Timing is perfect."
    }}
  ],
  "approved": true,
  "verdict": "Ready for render.",
  "critical_issues": [],
  "optimization_suggestions": ["Slightly boost volume in intro."]
}}
"""

async def run(payload: dict, job_id: int = 0) -> EvalOutput:
    return await run_agent_with_schema(
        PROMPT, 
        payload, 
        schema=EvalOutput,
        agent_name="eval",
        job_id=job_id,
        task_type="qc"
    )
