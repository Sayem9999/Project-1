from openai import AsyncOpenAI
import google.generativeai as genai
from ..config import settings

# OpenAI Client
openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

# Gemini Configuration
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)


async def run_agent_prompt(system_prompt: str, payload: dict, model: str = "gemini-1.5-flash") -> dict:
    # 1. Try Gemini First (Free Tier)
    if settings.gemini_api_key:
        # Prioirtize the requested model, then fallbacks
        candidates = [model, "gemini-1.5-flash", "gemini-pro"]
        # Deduplicate
        seen = set()
        gemini_models = [x for x in candidates if not (x in seen or seen.add(x))]
        
        for g_model in gemini_models:
            try:
                # Prepend system prompt to user prompt for Gemini
                full_prompt = f"System: {system_prompt}\n\nUser Input: {str(payload)}"
                model_instance = genai.GenerativeModel(g_model)
                response = await model_instance.generate_content_async(full_prompt)
                
                if response.text:
                    return {"raw_response": response.text}
            except Exception as e:
                print(f"Gemini {g_model} error: {e}")
                continue # Try next model

        print("All Gemini models failed. Falling back to OpenAI...")

    # 2. Fallback to OpenAI
    if not openai_client:
        raise RuntimeError("No AI API keys configured (GEMINI_API_KEY or OPENAI_API_KEY).")

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini", # Fallback model
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": str(payload)},
        ],
    )
    return {"raw_response": response.choices[0].message.content}
        
        print("All Gemini models failed. Falling back to OpenAI...")

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
