import sys
import os
from pathlib import Path

def check_and_setup():
    print(f"Python: {sys.version}")
    
    try:
        import moviepy
        print(f"MoviePy Version: {moviepy.__version__}")
        if hasattr(moviepy, 'editor'):
            print("moviepy.editor found")
        else:
            print("moviepy.editor NOT found")
            print(dir(moviepy))
    except ImportError:
        print("MoviePy not installed")

    # Create directories
    base = Path("backend/app/graph")
    (base / "nodes").mkdir(parents=True, exist_ok=True)
    print(f"Created {base}/nodes")

if __name__ == "__main__":
    check_and_setup()
