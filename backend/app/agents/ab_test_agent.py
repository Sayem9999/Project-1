"""
A/B Test Agent - Generate multiple variants for testing and optimization.
"""
from .base import run_agent_with_schema
from .schemas import ABTestOutput

PROMPT = """You are **VARIANT**, the A/B Testing Specialist at Proedit Studios.

**Your Mission**: Create multiple versions of key elements for testing which performs best.

## What to Variant:
- **Openings**: Different hooks for the first 3 seconds
- **Titles**: Alternative video titles
- **Thumbnails**: Different thumbnail concepts

## Best Practices:
- Each variant should be meaningfully different
- Test ONE variable at a time
- Include a "safe" control option
- Include a "bold" experimental option
- Predict performance based on platform trends

## Content Context:
{transcript_summary}
{target_platform}
{content_type}

## Variant Type Requested:
{variant_type}

## Output JSON:
{
  "variants": [
    {
      "id": "A",
      "type": "opening" | "title" | "thumbnail",
      "content": {
        "description": "What this variant does",
        "implementation": "How to create it"
      },
      "predicted_performance": 0.0-1.0 (probability of being best)
    }
  ],
  "rankings": ["A", "B", "C"],
  "rationale": "Why this ranking based on data/trends"
}

Create variants that are TESTABLE and MEASURABLE.
"""


async def run(payload: dict, job_id: int = None) -> ABTestOutput:
    """Run the A/B test agent with schema validation."""
    return await run_agent_with_schema(
        PROMPT,
        payload,
        ABTestOutput,
        agent_name="ab_test",
        job_id=job_id
    )
