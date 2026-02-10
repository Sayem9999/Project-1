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
    """Parse JSON from model response, handling markdown code blocks and conversational filler."""
    text = text.strip()
    
    # Try to find JSON block using regex if basic stripping fails
    import re
    
    # Look for content between triple backticks
    code_block = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if code_block:
        text = code_block.group(1)
    else:
        # Fallback: look for the first '{' and last '}'
        json_match = re.search(r"(\{.*\})", text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
    
    return json.loads(text.strip())


from .routing_policy import provider_router, RoutingPolicy, TaskType
from .telemetry import AgentSpan

async def run_agent_with_schema(
    system_prompt: str,
    payload: dict,
    schema: Type[T],
    agent_name: str = "unknown",
    job_id: Optional[int] = None,
    max_retries: int = 2,
    task_type: TaskType = "simple"
) -> T:
    """
    Run an agent prompt and validate output against a Pydantic schema.
    Auto-retries on validation failure with repair prompt.
    
    Returns validated Pydantic model instance.
    """
    last_error = None
    
    for attempt in range(max_retries + 1):
        with AgentSpan(agent_name, job_id=job_id, attempt=attempt + 1) as span:
            try:
                # Get raw response using routing policy
                result = await run_agent_prompt(
                    system_prompt, 
                    payload, 
                    task_type=task_type,
                    agent_name=agent_name,
                    job_id=job_id
                )
                
                raw_text = result.get("raw_response", "")
                model_used = result.get("model", "unknown")
                span.model = model_used
                
                # Parse JSON
                try:
                    parsed = parse_json_response(raw_text)
                except json.JSONDecodeError as e:
                    logger.warning(
                        "agent_json_parse_failed",
                        agent=agent_name,
                        job_id=job_id,
                        error=str(e),
                        raw_text=raw_text[:500] # Log first 500 chars
                    )
                    if attempt < max_retries:
                        payload["_repair_request"] = f"Your last response was not valid JSON. Error: {e}. Please return ONLY valid JSON."
                        continue
                    raise
                
                # Validate against schema
                try:
                    validated = schema.model_validate(parsed)
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
                if attempt >= max_retries:
                    raise
    
    raise RuntimeError(f"Agent {agent_name} failed after {max_retries + 1} attempts. Last error: {last_error}")


async def run_agent_prompt(
    system_prompt: str, 
    payload: dict, 
    task_type: TaskType = "simple",
    agent_name: str = "unknown",
    job_id: Optional[int] = None
) -> dict:
    """
    Run an agent prompt and return raw response.
    Uses ProviderRouter for policy-driven selection.
    """
    policy = RoutingPolicy(task_type=task_type)
    provider = provider_router.select_provider(policy)
    
    if not provider:
        raise RuntimeError(f"No healthy provider found for task {task_type}")

    last_error = None
    start_time = time.time()
    
    # Try the selected provider and its models
    for model in provider.models:
        try:
            logger.debug("agent_api_attempt", provider=provider.name, model=model, agent=agent_name)
            
            response_text = ""
            
            payload_json = json.dumps(payload, indent=2)
            
            if provider.name == "groq" and groq_client:
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": payload_json},
                    ],
                    model=model,
                )
                response_text = chat_completion.choices[0].message.content
                
            elif provider.name == "gemini" and gemini_client:
                full_prompt = f"System: {system_prompt}\n\nUser Input: {payload_json}"
                response = await gemini_client.aio.models.generate_content(
                    model=model,
                    contents=full_prompt,
                )
                response_text = response.text
                
            elif provider.name == "openai" and openai_client:
                response = await openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": payload_json},
                    ],
                )
                response_text = response.choices[0].message.content

            if response_text:
                latency_ms = (time.time() - start_time) * 1000
                provider_router.record_success(provider.name, int(latency_ms))
                return {
                    "raw_response": response_text,
                    "model": model,
                    "provider": provider.name
                }
                
        except Exception as e:
            logger.warning("agent_api_failed", provider=provider.name, model=model, error=str(e))
            last_error = e
            provider_router.record_failure(provider.name, str(e))
            continue

    # Fallback if selected provider failed
    logger.warning("agent_provider_fallback", old_provider=provider.name, agent=agent_name)
    
    # Simple hardcoded fallback to Gemini
    if provider.name != "gemini" and gemini_client:
        try:
            response = await gemini_client.aio.models.generate_content(
                model="gemini-1.5-flash",
                contents=f"System: {system_prompt}\n\nUser Input: {str(payload)}",
            )
            if response.text:
                return {"raw_response": response.text, "model": "gemini-1.5-flash", "provider": "gemini"}
        except:
            pass

    raise RuntimeError(f"All attempts failed for agent {agent_name}. Last error: {last_error}")
