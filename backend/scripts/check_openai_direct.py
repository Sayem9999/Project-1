import os
import sys
from pathlib import Path

# Add backend to sys.path
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from app.config import settings
from openai import OpenAI

def main():
    print(f"Checking OpenAI direct connectivity...")
    key = settings.openai_api_key
    print(f"Key present: {bool(key)}")
    if not key:
        print("Skipping - no key")
        return

    client = OpenAI(api_key=key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("Response received:")
        print(response.choices[0].message.content)
        print("[SUCCESS] OpenAI is reachable.")
    except Exception as e:
        print(f"[FAILURE] OpenAI Error: {e}")

if __name__ == "__main__":
    main()
