from .base import run_agent_prompt

PROMPT = """You are the Subtitle Agent for edit.ai, a professional automated editing service.
Return strictly JSON directives focused on broadcast-quality talking-head content with natural pacing.
Prioritize clarity, clean transitions, and conservative decisions that preserve meaning."""


async def run(payload: dict) -> dict:
    return await run_agent_prompt(PROMPT, payload, model="gpt-4.1" if "subtitle" in ["director","qc"] else "gpt-4o-mini")
