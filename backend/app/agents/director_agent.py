from .base import run_agent_prompt

PROMPT = """You are the Director Agent for edit.ai.
Your goal is to output JSON directives for video editing based on the user's requested THEME.
If no theme is provided, default to 'professional'.

Analyze the request and directives to match the style, pacing, and vibe of the theme (e.g., 'viral' = fast cuts, 'cinematic' = slow, 'professional' = standard).
Return strictly JSON."""


async def run(payload: dict) -> dict:
    return await run_agent_prompt(PROMPT, payload, model="gpt-4o" if "director" in ["director","qc"] else "gpt-4o-mini")
