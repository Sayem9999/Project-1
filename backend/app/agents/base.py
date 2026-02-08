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
        # Prioritize 1.5 Flash (Fast & Free) -> 1.5 Pro -> Legacy Pro
        # Note: 404 errors usually mean the library version is old or model name is wrong.
        gemini_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        
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
            except Exception as e:
                print(f"Gemini {g_model} failed: {e}")
                continue # Try next model
        
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
