import sys
import os
from pathlib import Path

# Add backend and backend/app to path
backend_path = Path("backend").absolute()
sys.path.append(str(backend_path))

try:
    from app.services.introspection import introspection_service
    print(f"Root dir detected: {introspection_service.root_dir}")
    data = introspection_service.scan()
    print(f"Stats: {data['stats']}")
    print(f"Nodes found: {len(data['nodes'])}")
    if len(data['nodes']) > 0:
        print("SUCCESS: Codebase nodes detected.")
        # Print a few nodes for verification
        for node in data['nodes'][:5]:
            print(f" - {node['type']}: {node['label']}")
    else:
        print("FAILURE: No nodes detected.")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
