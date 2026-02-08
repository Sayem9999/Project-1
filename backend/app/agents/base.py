from openai import AsyncOpenAI
import google.generativeai as genai
from groq import Groq
from ..config import settings

# OpenAI Client
openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

# Gemini Configuration
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

# Groq Client
groq_client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None


async def run_agent_prompt(system_prompt: str, payload: dict, model: str = "gemini-1.5-flash") -> dict:
    last_error = None
    
    # 1. Try Groq First (Most Reliable Free Tier)
    if groq_client:
        try:
            print("Attempting Groq API...")
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": str(payload)},
                ],
                model="llama-3.3-70b-versatile",  # Best free model on Groq
            )
            if chat_completion.choices[0].message.content:
                print("Groq success!")
                return {"raw_response": chat_completion.choices[0].message.content}
        except Exception as e:
            print(f"Groq error: {e}")
            last_error = e

    # 2. Try Gemini (Free Tier)
    if settings.gemini_api_key:
        # Dynamic Model Discovery
        candidates = []
        try:
            candidates.append(model)
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            candidates.extend(available_models)
            candidates.extend(["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"])
        except Exception as e:
            print(f"Error listing Gemini models: {e}")
            candidates = [model, "gemini-1.5-flash", "gemini-1.5-pro"]

        seen = set()
        gemini_models = []
        for x in candidates:
            simple_name = x.replace("models/", "")
            if simple_name not in seen:
                seen.add(simple_name)
                gemini_models.append(x)

        print(f"Attempting Gemini models: {gemini_models}")
        
        for g_model in gemini_models:
            try:
                full_prompt = f"System: {system_prompt}\n\nUser Input: {str(payload)}"
                model_instance = genai.GenerativeModel(g_model)
                response = await model_instance.generate_content_async(full_prompt)
                if response.text:
                    print(f"Gemini {g_model} success!")
                    return {"raw_response": response.text}
            except Exception as e:
                print(f"Gemini {g_model} error: {e}")
                last_error = e
                continue
        
        print(f"All Gemini models failed. Last error: {last_error}")

    # 3. Fallback to OpenAI
    if openai_client:
        try:
            print("Attempting OpenAI fallback...")
            response = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": str(payload)},
                ],
            )
            return {"raw_response": response.choices[0].message.content}
        except Exception as e:
            print(f"OpenAI error: {e}")
            last_error = e

    # No API worked
    raise RuntimeError(f"All AI APIs failed. Last error: {last_error}. Configure GROQ_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY.")
