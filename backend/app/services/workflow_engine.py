import asyncio
import json
import subprocess
import shutil
import os
from pathlib import Path
from sqlalchemy import select
from ..db import AsyncSession, engine
from ..models import Job
from ..config import settings
from ..agents import (
    director_agent, cutter_agent, subtitle_agent, audio_agent, 
    color_agent, qc_agent, metadata_agent, transition_agent,
    vfx_agent, keyframe_agent, thumbnail_agent, script_agent
)
from .memory_service import memory_service


async def process_job(job_id: int, source_path: str, pacing: str = "medium", mood: str = "professional", ratio: str = "16:9"):
    """
    Advanced Agentic Workflow Engine v2.0
    Features:
    - 10 AI Agents with specialized roles
    - Keyframe-based analysis
    - Visual effects & transitions
    - Thumbnail generation
    - QC Feedback Loop
    - Studio Memory
    """
    def parse_json_safe(raw: str) -> dict:
        try:
            clean = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except:
            return {}

    print(f"[Workflow v2] Starting job {job_id}")
    
    async with AsyncSession(engine) as session:
        job = await session.get(Job, job_id)
        if not job: return
        job.status = "processing"
        job.progress_message = "Initializing AI Studio..."
        await session.commit()

    try:
        # === PHASE 1: Analysis ===
        await update_status(job_id, "processing", "[FRAME] Analyzing keyframes...")
        memory_context = memory_service.get_context()
        
        # Keyframe Analysis (NEW)
        keyframe_payload = {"source_path": source_path, "pacing": pacing}
        keyframe_resp = await keyframe_agent.run(keyframe_payload)
        keyframe_data = parse_json_safe(keyframe_resp.get("raw_response", "{}"))
        print(f"[Workflow] Keyframe Analysis: {keyframe_data.get('scene_count', 'N/A')} scenes detected")
        
        # === PHASE 2: Director Planning ===
        max_retries = 1
        attempt = 0
        final_output_path = None
        current_feedback = ""
        director_plan = {}

        while attempt <= max_retries:
            attempt += 1
            status_prefix = f"[Take {attempt}]" if attempt > 1 else "[MAX]"
            await update_status(job_id, "processing", f"{status_prefix} Director planning strategy...")
            
            director_payload = {
                "source_path": source_path,
                "pacing": pacing,
                "mood": mood, 
                "ratio": ratio,
                "keyframe_analysis": keyframe_data,
                "memory_context": memory_context,
                "feedback": current_feedback
            }
            
            director_resp = await director_agent.run(director_payload)
            director_plan = parse_json_safe(director_resp.get("raw_response", "{}"))
            print(f"[Workflow] Director Plan (Take {attempt}): {director_plan.get('strategy', 'No strategy')}")

            # === PHASE 3: Parallel Specialists ===
            await update_status(job_id, "processing", f"{status_prefix} Specialists working in parallel...")
            
            # Run 6 agents in parallel
            specialist_tasks = [
                cutter_agent.run({"plan": director_plan}),
                color_agent.run({"plan": director_plan, "mood": mood}),
                audio_agent.run({"plan": director_plan}),
                transition_agent.run({"plan": director_plan, "keyframes": keyframe_data}),
                vfx_agent.run({"plan": director_plan, "mood": mood}),
                script_agent.run({"source_path": source_path}),
            ]
            
            results = await asyncio.gather(*specialist_tasks, return_exceptions=True)
            
            # Parse results
            cutter_res = parse_json_safe(results[0].get("raw_response", "{}")) if isinstance(results[0], dict) else {}
            color_res = parse_json_safe(results[1].get("raw_response", "{}")) if isinstance(results[1], dict) else {}
            audio_res = parse_json_safe(results[2].get("raw_response", "{}")) if isinstance(results[2], dict) else {}
            transition_res = parse_json_safe(results[3].get("raw_response", "{}")) if isinstance(results[3], dict) else {}
            vfx_res = parse_json_safe(results[4].get("raw_response", "{}")) if isinstance(results[4], dict) else {}
            script_res = parse_json_safe(results[5].get("raw_response", "{}")) if isinstance(results[5], dict) else {}
            
            print(f"[Workflow] Transitions: {transition_res.get('style_note', 'None')}")
            print(f"[Workflow] VFX: {vfx_res.get('style_note', 'None')}")

            # === PHASE 4: Render ===
            await update_status(job_id, "processing", f"{status_prefix} Rendering video...")
            
            output_filename = f"job-{job_id}-take{attempt}.mp4"
            output_abs = Path(settings.storage_root) / "outputs" / output_filename
            output_abs.parent.mkdir(parents=True, exist_ok=True)
            
            src = Path(source_path)
            if not src.exists(): src = Path(".") / source_path
            
            # Build FFmpeg filter chain
            vf_filters = ["scale=1280:720:force_original_aspect_ratio=decrease", "pad=1280:720:(ow-iw)/2:(oh-ih)/2"]
            
            # Add VFX filters if suggested
            if vfx_res.get("effects"):
                for effect in vfx_res.get("effects", [])[:2]:  # Max 2 effects
                    if "filter" in effect:
                        vf_filters.append(effect["filter"])
            
            # Add watermark for free tier users (no user tier check yet, always add for now)
            # TODO: Check user tier from database and skip watermark for paid users
            watermark_text = "Proedit.ai"
            vf_filters.append(f"drawtext=text='{watermark_text}':fontsize=24:fontcolor=white@0.5:x=w-tw-20:y=h-th-20")
            
            vf = ",".join(vf_filters)
            af = "loudnorm=I=-16:TP=-1.5:LRA=11"
            
            cmd = ["ffmpeg", "-y", "-i", str(src), "-threads", "2", "-preset", "fast", "-vf", vf, "-af", af, "-c:v", "libx264", "-crf", "23", str(output_abs)]
            
            if os.path.exists("./tools/ffmpeg"): cmd[0] = "./tools/ffmpeg"

            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()
            
            if proc.returncode != 0 or not output_abs.exists():
                shutil.copy(src, output_abs)

            final_output_path = f"storage/outputs/{output_filename}"

            # === PHASE 5: QC Review ===
            if attempt <= max_retries:
                await update_status(job_id, "processing", f"[THE PRODUCER] Reviewing Take {attempt}...")
                qc_payload = {"user_request": {"pacing": pacing, "mood": mood}, "director_plan": director_plan}
                qc_resp = await qc_agent.run(qc_payload)
                qc_data = parse_json_safe(qc_resp.get("raw_response", "{}"))
                
                if qc_data.get("approved", True):
                    print("[Workflow] QC Approved!")
                    break
                else:
                    current_feedback = qc_data.get("feedback", "Improvements needed.")
                    print(f"[Workflow] QC Rejected: {current_feedback}")
                    memory_service.add_feedback(current_feedback)
                    continue 

        # === PHASE 6: Post-Production ===
        await update_status(job_id, "processing", "[THUMB] Generating thumbnail...")
        
        # Thumbnail & Metadata in parallel
        thumb_task = thumbnail_agent.run({"source_path": source_path, "mood": mood})
        meta_task = metadata_agent.run({"plan": director_plan})
        
        post_results = await asyncio.gather(thumb_task, meta_task, return_exceptions=True)
        
        thumb_data = parse_json_safe(post_results[0].get("raw_response", "{}")) if isinstance(post_results[0], dict) else {}
        meta_data = parse_json_safe(post_results[1].get("raw_response", "{}")) if isinstance(post_results[1], dict) else {}
        
        # Extract thumbnail frame
        if thumb_data.get("best_timestamp"):
            thumb_path = Path(settings.storage_root) / "outputs" / f"job-{job_id}-thumb.jpg"
            thumb_cmd = ["ffmpeg", "-y", "-ss", str(thumb_data["best_timestamp"]), "-i", str(src), "-vframes", "1", "-q:v", "2", str(thumb_path)]
            thumb_proc = await asyncio.create_subprocess_exec(*thumb_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await thumb_proc.communicate()
            print(f"[Workflow] Thumbnail generated at {thumb_data['best_timestamp']}s")
        
        # Subtitles
        try:
            sub_resp = await subtitle_agent.run({"source_path": source_path})
            srt_content = sub_resp.get("raw_response", "") if isinstance(sub_resp, dict) else ""
            if srt_content:
                srt_path = Path(settings.storage_root) / "outputs" / f"job-{job_id}.srt"
                with open(srt_path, "w", encoding="utf-8") as f: f.write(srt_content)
        except: pass

        # Final output
        final_rel_path = f"storage/outputs/job-{job_id}.mp4"
        final_abs_path = Path(settings.storage_root) / "outputs" / f"job-{job_id}.mp4"
        take_path = Path(settings.storage_root) / "outputs" / f"job-{job_id}-take{attempt}.mp4"
        if take_path.exists():
            shutil.move(take_path, final_abs_path)
        
        # Completion
        completion_msg = "🎬 Your video is ready!"
        if meta_data.get("title"):
            completion_msg = f"🎬 {meta_data['title']} is ready!"
            
        await update_status(job_id, "complete", completion_msg, final_rel_path)
        print(f"[Workflow] Job {job_id} complete! Metadata: {meta_data}")

    except Exception as e:
        print(f"[Workflow] Job {job_id} failed: {e}")
        import traceback
        traceback.print_exc()
        await update_status(job_id, "failed", f"Processing failed: {str(e)[:100]}")


async def update_status(job_id: int, status: str, message: str, output_path: str = None):
    async with AsyncSession(engine) as session:
        job = await session.get(Job, job_id)
        if job:
            job.status = status
            job.progress_message = message
            if output_path:
                job.output_path = output_path
            await session.commit()
