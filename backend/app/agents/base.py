from openai import AsyncOpenAI
from google import genai
from google.genai import types
from groq import Groq
from ..config import settings

# OpenAI Client
openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

# Gemini Client (new unified SDK)
gemini_client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

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

    # 2. Try Gemini (Free Tier) - Using new google.genai SDK
    if gemini_client:
        gemini_models = [model, "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]
        
        for g_model in gemini_models:
            try:
                print(f"Attempting Gemini model: {g_model}")
                full_prompt = f"System: {system_prompt}\n\nUser Input: {str(payload)}"
                
                response = await gemini_client.aio.models.generate_content(
                    model=g_model,
                    contents=full_prompt,
                )
                
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
