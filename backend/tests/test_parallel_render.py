import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.rendering_orchestrator import rendering_orchestrator
from app.config import settings

async def test_parallel_render():
    print("--- Starting Parallel Render Test ---")
    
    # Use a real file if possible, or we might need to generate a small test file
    source_path = "storage/temp/test_source.mp4"
    if not os.path.exists(source_path):
        print(f"Generating test source at {source_path}...")
        Path("storage/temp").mkdir(parents=True, exist_ok=True)
        # Create a 10s test video with audio
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=duration=10:size=1280x720:rate=24",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=10",
            "-c:v", "libx264", "-c:a", "aac", source_path
        ]
        proc = await asyncio.create_subprocess_exec(*cmd)
        await proc.communicate()

    output_path = "storage/outputs/test_parallel_output.mp4"
    cuts = [
        {"start": 0, "end": 2, "reason": "intro"},
        {"start": 4, "end": 6, "reason": "mid"},
        {"start": 8, "end": 10, "reason": "outro"}
    ]
    
    print(f"Rendering {len(cuts)} cuts in parallel...")
    success = await rendering_orchestrator.render_parallel(
        job_id=999,
        source_path=source_path,
        cuts=cuts,
        output_path=output_path,
        crf=23,
        preset="ultrafast"
    )
    
    if success and os.path.exists(output_path):
        print(f"SUCCESS: Rendered video at {output_path}")
        # Check duration (should be ~6s)
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", output_path]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        duration = float(stdout.decode().strip())
        print(f"Final duration: {duration}s (expected ~6s)")
        if 5.8 <= duration <= 6.2:
            print("Duration check PASSED")
        else:
            print("Duration check FAILED")
    else:
        print("FAILED: Parallel rendering failed.")

if __name__ == "__main__":
    asyncio.run(test_parallel_render())
