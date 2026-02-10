import os
import json
import requests

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api")


def main() -> None:
    resp = requests.get(f"{API_BASE}/agents/health", timeout=10)
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent=2))


if __name__ == "__main__":
    main()
