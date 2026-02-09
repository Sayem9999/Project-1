"""
Agent Base Module - Core AI API integration with structured output validation.
Supports Groq, Gemini, and OpenAI with automatic fallback.
"""
import json
import time
import structlog
from typing import TypeVar, Type, Optional
from pydantic import BaseModel, ValidationError
from openai import AsyncOpenAI
from google import genai
from groq import Groq
from ..config import settings

logger = structlog.get_logger()

# Type variable for schema validation
T = TypeVar("T", bound=BaseModel)

# OpenAI Client
openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

# Gemini Client (new unified SDK)
gemini_client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

# Groq Client
groq_client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None


def parse_json_response(text: str) -> dict:
    """Parse JSON from model response, handling markdown code blocks."""
    text = text.strip()
    
    # Remove markdown code blocks if present
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    
    return json.loads(text.strip())


async def run_agent_with_schema(
    system_prompt: str,
    payload: dict,
    schema: Type[T],
    agent_name: str = "unknown",
    job_id: Optional[int] = None,
    max_retries: int = 2,
    model: str = "gemini-1.5-flash"
) -> T:
    """
    Run an agent prompt and validate output against a Pydantic schema.
    Auto-retries on validation failure with repair prompt.
    
    Returns validated Pydantic model instance.
    """
    last_error = None
    
    for attempt in range(max_retries + 1):
        start_time = time.time()
        
        logger.info(
            "agent_attempt",
            agent=agent_name,
            job_id=job_id,
            attempt=attempt + 1,
            max_retries=max_retries
        )
        
        try:
            # Get raw response
            result = await run_agent_prompt(
                system_prompt, 
                payload, 
                model=model,
                agent_name=agent_name,
                job_id=job_id
            )
            
            raw_text = result.get("raw_response", "")
            
            # Parse JSON
            try:
                parsed = parse_json_response(raw_text)
            except json.JSONDecodeError as e:
                logger.warning(
                    "agent_json_parse_failed",
                    agent=agent_name,
                    job_id=job_id,
                    error=str(e)
                )
                if attempt < max_retries:
                    # Add repair instruction to payload for retry
                    payload["_repair_request"] = f"Your last response was not valid JSON. Error: {e}. Please return ONLY valid JSON."
                    continue
                raise
            
            # Validate against schema
            try:
                validated = schema.model_validate(parsed)
                latency_ms = (time.time() - start_time) * 1000
                
                logger.info(
                    "agent_success",
                    agent=agent_name,
                    job_id=job_id,
                    latency_ms=round(latency_ms, 2),
                    attempt=attempt + 1
                )
                
                return validated
                
            except ValidationError as e:
                logger.warning(
                    "agent_validation_failed",
                    agent=agent_name,
                    job_id=job_id,
                    errors=e.error_count(),
                    details=str(e)
                )
                if attempt < max_retries:
                    payload["_repair_request"] = f"Your response did not match the required schema. Errors: {e}. Please fix and return valid JSON."
                    continue
                raise
                
        except Exception as e:
            last_error = e
            logger.error(
                "agent_error",
                agent=agent_name,
                job_id=job_id,
                attempt=attempt + 1,
                error=str(e)
            )
            if attempt >= max_retries:
                raise
    
    raise RuntimeError(f"Agent {agent_name} failed after {max_retries + 1} attempts. Last error: {last_error}")


async def run_agent_prompt(
    system_prompt: str, 
    payload: dict, 
    model: str = "gemini-1.5-flash",
    agent_name: str = "unknown",
    job_id: Optional[int] = None
) -> dict:
    """
    Run an agent prompt and return raw response.
    Tries Groq -> Gemini -> OpenAI with automatic fallback.
    """
    last_error = None
    
    # 1. Try Groq First (Most Reliable Free Tier)
    if groq_client:
        try:
            logger.debug("agent_api_attempt", api="groq", agent=agent_name, job_id=job_id)
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": str(payload)},
                ],
                model="llama-3.3-70b-versatile",
            )
            if chat_completion.choices[0].message.content:
                logger.debug("agent_api_success", api="groq", agent=agent_name)
                return {"raw_response": chat_completion.choices[0].message.content}
        except Exception as e:
            logger.warning("agent_api_failed", api="groq", agent=agent_name, error=str(e))
            last_error = e

    # 2. Try Gemini (Free Tier) - Using new google.genai SDK
    if gemini_client:
        gemini_models = [model, "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]
        
        for g_model in gemini_models:
            try:
                logger.debug("agent_api_attempt", api="gemini", model=g_model, agent=agent_name)
                full_prompt = f"System: {system_prompt}\n\nUser Input: {str(payload)}"
                
                response = await gemini_client.aio.models.generate_content(
                    model=g_model,
                    contents=full_prompt,
                )
                
                if response.text:
                    logger.debug("agent_api_success", api="gemini", model=g_model, agent=agent_name)
                    return {"raw_response": response.text}
            except Exception as e:
                logger.warning("agent_api_failed", api="gemini", model=g_model, error=str(e))
                last_error = e
                continue
        
        logger.warning("agent_all_gemini_failed", agent=agent_name, last_error=str(last_error))

    # 3. Fallback to OpenAI
    if openai_client:
        try:
            logger.debug("agent_api_attempt", api="openai", agent=agent_name)
            response = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": str(payload)},
                ],
            )
            logger.debug("agent_api_success", api="openai", agent=agent_name)
            return {"raw_response": response.choices[0].message.content}
        except Exception as e:
            logger.warning("agent_api_failed", api="openai", error=str(e))
            last_error = e

    # No API worked
    raise RuntimeError(f"All AI APIs failed. Last error: {last_error}. Configure GROQ_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY.")
