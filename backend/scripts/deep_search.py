import os

search_dir = r"C:\Users\Sayem\Downloads\New folder\Project-1-1"
targets = ["Void_Config", "Cache Orchestrator", "CacheOrchestrator"]

print(f"🔍 Searching for {targets} in {search_dir}")

for root, dirs, files in os.walk(search_dir):
    if any(x in root for x in [".git", ".venv", "node_modules", "__pycache__"]):
        continue
    for file in files:
        path = os.path.join(root, file)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for target in targets:
                    if target in content:
                        print(f"✅ FOUND '{target}' in: {path}")
        except Exception:
            pass
print("🏁 Search finished.")
