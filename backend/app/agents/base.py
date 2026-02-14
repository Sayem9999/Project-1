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

# Type variable for Pydantic model validation
T = TypeVar("T", bound=BaseModel)

logger = structlog.get_logger()

# OpenAI Client
openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

# Gemini Client (Unified SDK)
gemini_client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

# Groq Client
groq_client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None

# OpenRouter Client (OpenAI-compatible)
openrouter_client = AsyncOpenAI(
    api_key=settings.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1"
) if settings.openrouter_api_key else None


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


from .routing_policy import provider_router, RoutingPolicy, TaskType, PROVIDERS
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
                    import asyncio
                    import random
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
                        # Exponential backoff for validation retries
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        await asyncio.sleep(wait_time)
                        payload["_repair_request"] = f"Your response did not match the required schema. Errors: {e}. Please fix and return valid JSON."
                        continue
                    raise
                    
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    import asyncio
                    import random
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(wait_time)
                    continue
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

    last_error = None

    async def attempt_provider(provider_name: str, model: str) -> Optional[dict]:
        payload_json = json.dumps(payload, indent=2)
        attempt_start = time.time()
        response_text = ""

        if provider_name == "groq" and groq_client:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": payload_json},
                ],
                model=model,
            )
            response_text = chat_completion.choices[0].message.content

        elif provider_name == "gemini" and gemini_client:
            full_prompt = f"System: {system_prompt}\n\nUser Input: {payload_json}"
            response = await gemini_client.aio.models.generate_content(
                model=model,
                contents=full_prompt,
            )
            response_text = response.text

        elif provider_name == "openai" and openai_client:
            response = await openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": payload_json},
                ],
            )
            response_text = response.choices[0].message.content

        elif provider_name == "ollama":
            import httpx
            # Ollama standard chat endpoint
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"{settings.ollama_base_url}/api/chat",
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": payload_json}
                        ],
                        "stream": False,
                        "format": "json" if PROVIDERS["ollama"].supports_json else None
                    }
                )
                resp.raise_for_status()
                data = resp.json()
                response_text = data.get("message", {}).get("content", "")

        elif provider_name == "openrouter" and openrouter_client:
            response = await openrouter_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": payload_json},
                ],
                extra_headers={
                    "HTTP-Referer": "https://proedit.ai",
                    "X-Title": "ProEdit Studio",
                }
            )
            response_text = response.choices[0].message.content

        if response_text:
            latency_ms = (time.time() - attempt_start) * 1000
            provider_router.record_success(provider_name, int(latency_ms))
            return {
                "raw_response": response_text,
                "model": model,
                "provider": provider_name
            }
        return None

    if not provider:
        logger.warning("provider_emergency_mode", task_type=task_type, agent=agent_name)
        emergency_order: list[str] = []
        for name in [
            settings.llm_fallback_provider,
            settings.llm_primary_provider,
            "gemini",
            "groq",
            "openai",
        ]:
            if not name:
                continue
            normalized = name.lower()
            if normalized not in emergency_order:
                emergency_order.append(normalized)

        for provider_name in emergency_order:
            if provider_name == "gemini" and not gemini_client:
                continue
            if provider_name == "groq" and not groq_client:
                continue
            if provider_name == "openai" and not openai_client:
                continue
            provider_cfg = PROVIDERS.get(provider_name)
            if not provider_cfg:
                continue
            for model in provider_cfg.models:
                try:
                    logger.debug(
                        "agent_api_attempt_emergency",
                        provider=provider_name,
                        model=model,
                        agent=agent_name,
                    )
                    result = await attempt_provider(provider_name, model)
                    if result:
                        return result
                except Exception as e:
                    logger.warning("agent_api_failed", provider=provider_name, model=model, error=str(e))
                    last_error = e
                    provider_router.record_failure(provider_name, str(e))
                    provider_router.handle_provider_error(provider_name, model, str(e))
                    continue
        raise RuntimeError(f"No provider available for task {task_type}. Last error: {last_error}")

    # Try the selected provider and its models
    for model in provider.models:
        try:
            logger.debug("agent_api_attempt", provider=provider.name, model=model, agent=agent_name)
            result = await attempt_provider(provider.name, model)
            if result:
                return result
        except Exception as e:
            logger.warning("agent_api_failed", provider=provider.name, model=model, error=str(e))
            last_error = e
            provider_router.record_failure(provider.name, str(e))
            provider_router.handle_provider_error(provider.name, model, str(e))
            
            # Short sleep before trying next model of the SAME provider
            import asyncio
            await asyncio.sleep(0.5)
            continue

    # Fallback if selected provider failed
    logger.warning("agent_provider_fallback", old_provider=provider.name, agent=agent_name)

    fallback_order: list[str] = []
    for name in [
        settings.llm_fallback_provider,
        settings.llm_primary_provider,
        "gemini",
        "groq",
        "openai",
    ]:
        if not name:
            continue
        normalized = name.lower()
        if normalized not in fallback_order:
            fallback_order.append(normalized)

    for fallback_name in fallback_order:
        if fallback_name == provider.name:
            continue
        if fallback_name == "gemini" and not gemini_client:
            continue
        if fallback_name == "groq" and not groq_client:
            continue
        if fallback_name == "openai" and not openai_client:
            continue
        fallback_config = PROVIDERS.get(fallback_name)
        if not fallback_config:
            continue
            try:
                logger.debug("agent_api_attempt", provider=fallback_name, model=model, agent=agent_name)
                result = await attempt_provider(fallback_name, model)
                if result:
                    return result
            except Exception as e:
                logger.warning("agent_api_failed", provider=fallback_name, model=model, error=str(e))
                last_error = e
                provider_router.record_failure(fallback_name, str(e))
                provider_router.handle_provider_error(fallback_name, model, str(e))
                
                # Add a small yield/delay before switching models or providers to ease rate limits
                import asyncio
                await asyncio.sleep(0.5)
                continue

    raise RuntimeError(f"All attempts failed for agent {agent_name}. Last error: {last_error}")
