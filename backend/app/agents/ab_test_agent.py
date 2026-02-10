"""
A/B Test Agent - Generate multiple variants for testing and optimization.
"""
from typing import Optional
from .base import run_agent_with_schema
from .schemas import ABTestOutput

PROMPT = """You are **VARIANT**, the A/B Testing Specialist at Proedit Studios.

**Your Mission**: Create multiple versions of key elements (Hooks, Titles, or Thumbnails) for optimization.

## Content Context:
TRANSCRIPT SUMMARY: {transcript_summary}
TARGET PLATFORM: {target_platform}
CONTENT TYPE: {content_type}
VARIANT TYPE REQUESTED: {variant_type}

## REQUIRED OUTPUT FORMAT (JSON ONLY):
Return EXCLUSIVELY a JSON object following this exact structure.

{{
  "variants": [
    {{
      "id": "A",
      "type": "opening" | "title" | "thumbnail" | "hook",
      "content": {{
        "description": "What this variant does",
        "implementation": "How to create it"
      }},
      "predicted_performance": 0.85
    }}
  ],
  "rankings": ["A", "B", "C"],
  "rationale": "Data-driven explanation for the ranking."
}}

Note: If "{variant_type}" is "hook", use "hook" or "opening" for the type.
Predict performance as a probability (0.0 to 1.0).
"""


async def run(payload: dict, job_id: Optional[int] = None) -> ABTestOutput:
    """Run the A/B test agent with schema validation."""
    return await run_agent_with_schema(
        PROMPT,
        payload,
        ABTestOutput,
        agent_name="ab_test",
        task_type="creative",
        job_id=job_id
    )
