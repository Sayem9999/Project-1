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
        last_error = None
        
        # Dynamic Model Discovery
        candidates = []
        try:
            # Add user requested model first
            candidates.append(model)
            
            # Fetch available models from API
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            # Sort to prefer 1.5, then Pro, then others. 
            # Note: list_models returns full names like 'models/gemini-1.5-flash'
            # We need to handle both short and long names.
            
            # Add discovered models to candidates
            candidates.extend(available_models)
            
            # Fallbacks just in case list_models fails or returns nothing useful
            candidates.extend(["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-pro"])
            
        except Exception as e:
            print(f"Error listing models: {e}")
            candidates = [model, "gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-pro"]

        # Deduplicate while preserving order
        seen = set()
        gemini_models = []
        for x in candidates:
            # Normalize name (strip 'models/' prefix for comparison)
            simple_name = x.replace("models/", "")
            if simple_name not in seen:
                seen.add(simple_name)
                # Prefer the version with 'models/' if it came from the API, otherwise use as is
                gemini_models.append(x)

        print(f"Attempting Gemini models: {gemini_models}")
        
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
                last_error = e
                continue # Try next model
        
        # If we get here, all Gemini models failed
        print(f"All Gemini models failed. Last error: {last_error}")
        if not settings.openai_api_key:
             # If no OpenAI key, we must raise the Gemini error to info the user
             raise RuntimeError(f"Gemini failed: {last_error}. OpenAI fallback unavailable.")

    # 2. Fallback to OpenAI
    if not openai_client:
        raise RuntimeError("No AI API keys configured (GEMINI_API_KEY or OPENAI_API_KEY).")

    response = await openai_client.chat.completions.create(
        model=model if model == "gpt-4o-mini" else "gpt-4o-mini", # Fallback model
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": str(payload)},
        ],
    )
    return {"raw_response": response.choices[0].message.content}
