from openai import AsyncOpenAI
from ..config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


async def run_agent_prompt(system_prompt: str, payload: dict, model: str = "gpt-4o-mini") -> dict:
    if not client:
        raise RuntimeError("OPENAI_API_KEY is required for agent execution.")

    response = await client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": str(payload)},
        ],
    )
    return {"raw_response": response.output_text}
