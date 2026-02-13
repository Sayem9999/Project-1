
import asyncio
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.agents.base import run_agent_prompt
from app.config import settings

async def test_ollama():
    print("--- Ollama Integration Diagnostic ---")
    print(f"Base URL: {settings.ollama_base_url}")
    print(f"Model: {settings.ollama_model}")
    print("Attempting to run agent prompt through Ollama...")
    
    system_prompt = "You are a helpful assistant. Respond with ONLY the word 'SUCCESS' if you hear this."
    payload = {"message": "Can you hear me?"}
    
    try:
        # Forcing Ollama for this diagnostic
        settings.llm_primary_provider = "ollama"
        settings.ollama_enabled = True
        
        print(f"Forced Primary Provider: {settings.llm_primary_provider}")
        print(f"Model: {settings.ollama_model}")
        
        result = await run_agent_prompt(
            system_prompt,
            payload,
            task_type="fast", 
            agent_name="OllamaDiagnostic"
        )
        
        print("\n--- Response Received ---")
        print(f"Provider: {result.get('provider')}")
        print(f"Model: {result.get('model')}")
        print(f"Raw Text: {result.get('raw_response')}")
        
    except Exception as e:
        print(f"\n[!] Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_ollama())
