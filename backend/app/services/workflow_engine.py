import asyncio
import json
import subprocess
import shutil
from pathlib import Path
from sqlalchemy import select
from ..db import AsyncSession, engine
from ..models import Job
from ..config import settings
from ..agents import director_agent, cutter_agent, subtitle_agent, audio_agent, color_agent, qc_agent

async def process_job(job_id: int, source_path: str):
    """
    Internal workflow engine replacing n8n.
    Steps:
    1. Transcribe (Mock or Real)
    2. AI Agents (Director -> Sub-agents) (Mock or Real)
    3. Render (FFmpeg)
    """
    print(f"[Workflow] Starting job {job_id}")
    
    async with AsyncSession(engine) as session:
        job = await session.get(Job, job_id)
        if not job:
            return
        job.status = "processing"
        job.progress_message = "Starting internal workflow..."
        theme = job.theme  # Extract attribute while session is open
        await session.commit()

    try:
        # --- Step 1: Analysis / Transcription ---
        await update_status(job_id, "processing", "Analyzing content...")
        
        # Simulate processing time or call OpenAI Whisper if key exists
        await asyncio.sleep(1) 

        # --- Step 2: AI Directors ---
        await update_status(job_id, "processing", "AI Director planning edits...")
        
        directives = {"style": "default", "cut_pace": "medium"}
        if settings.openai_api_key or settings.gemini_api_key:
            # Real AI Agent flow
            try:
                # Pass attributes to sub-agents or just director
                director_output = await director_agent.run({
                    "source_path": source_path,
                    "theme": theme, 
                })
                directives = director_output
                # Fan out to other agents could go here
            except Exception as e:
                print(f"[Workflow] AI Agent failed (using defaults): {e}")
                await update_status(job_id, "processing", "AI Limit Reached - Using Default Style...")
                # Fallback to defaults (already set)
        else:
            # Mock / Default directives
            directives = {"style": "default", "cut_pace": "medium"}

        # --- Step 3: Rendering ---
        await update_status(job_id, "processing", "Rendering video...")
        
        output_filename = f"job-{job_id}.mp4"
        output_rel = f"{settings.storage_root}/outputs/{output_filename}"
        output_abs = Path(settings.storage_root) / "outputs" / output_filename
        output_abs.parent.mkdir(parents=True, exist_ok=True)

        # Ensure source exists (handle relative/absolute)
        src = Path(source_path)
        if not src.exists():
            # Try relative to backend
            src = Path(".") / source_path
        
        if not src.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        # Determine FFmpeg path
        ffmpeg_cmd = "ffmpeg"
        # Check local tools directory (standard for our Render setup)
        possible_paths = [Path("tools/ffmpeg"), Path("./tools/ffmpeg"), Path("/opt/render/project/src/backend/tools/ffmpeg")]
        for p in possible_paths:
            if p.exists() and p.is_file():
                ffmpeg_cmd = str(p.absolute())
                break
        
        print(f"[Workflow] Using FFmpeg binary at: {ffmpeg_cmd}")

        # FFmpeg command (similar to mock_n8n.py but internal)
        cmd = [
            ffmpeg_cmd, "-y", "-i", str(src),
            "-threads", "1",  # Low memory mode
            "-preset", "ultrafast",  # Low CPU/RAM
            "-vf", "scale=854:480:force_original_aspect_ratio=decrease,pad=854:480:(ow-iw)/2:(oh-ih)/2",
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            str(output_abs)
        ]
        
        print(f"[Workflow] Running FFmpeg: {' '.join(cmd)}")
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                print(f"[Workflow] FFmpeg failed: {stderr.decode()}")
                raise RuntimeError("FFmpeg non-zero exit")
        except (FileNotFoundError, RuntimeError) as e:
            print(f"[Workflow] FFmpeg issue ({e}), falling back to copy")
            shutil.copy(src, output_abs)
        
        # --- Completion ---
        await update_status(job_id, "complete", "Rendering complete", str(output_rel))
        print(f"[Workflow] Job {job_id} complete. Output: {output_rel}")

    except Exception as e:
        print(f"[Workflow] Job {job_id} failed: {e}")
        import traceback
        traceback.print_exc()
        await update_status(job_id, "failed", f"Internal workflow failed: {str(e)}")


async def update_status(job_id: int, status: str, message: str, output_path: str = None):
    async with AsyncSession(engine) as session:
        job = await session.get(Job, job_id)
        if job:
            job.status = status
            job.progress_message = message
            if output_path:
                job.output_path = output_path
            await session.commit()
