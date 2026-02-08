from openai import AsyncOpenAI
import google.generativeai as genai
from ..config import settings

# OpenAI Client
openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

# Gemini Configuration
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)


async def run_agent_prompt(system_prompt: str, payload: dict, model: str = "gpt-4o-mini") -> dict:
    # 1. Try Gemini First (Free Tier)
    if settings.gemini_api_key:
        try:
            # Gemini doesn't use system prompts the same way, but we can prepend it
            full_prompt = f"{system_prompt}\n\nInput Data:\n{str(payload)}"
            gemini_model = genai.GenerativeModel("gemini-1.5-flash")
            response = await gemini_model.generate_content_async(full_prompt)
            return {"raw_response": response.text}
        except Exception as e:
            print(f"Gemini Error: {e}")
            # Fallback to OpenAI if available
            if not openai_client:
                raise e

    # 2. Fallback to OpenAI
    if not openai_client:
        raise RuntimeError("No AI API keys configured (GEMINI_API_KEY or OPENAI_API_KEY).")

    response = await openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": str(payload)},
        ],
    )
    return {"raw_response": response.choices[0].message.content}
