import asyncio
import asyncio.subprocess
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
from ..agents.base import parse_json_response
from .memory.hybrid_memory import hybrid_memory

# Redis for progress publishing (optional)
REDIS_URL = os.getenv("REDIS_URL")


def detect_gpu_encoder() -> str:
    """
    Detect available GPU encoder for FFmpeg.
    Returns encoder name or 'libx264' as fallback.
    """
    # Check for NVIDIA GPU (NVENC)
    try:
        result = subprocess.run(
            ["ffmpeg", "-hide_banner", "-encoders"],
            capture_output=True, text=True, timeout=5
        )
        if "h264_nvenc" in result.stdout:
            # Verify NVENC actually works
            test = subprocess.run(
                ["ffmpeg", "-hide_banner", "-f", "lavfi", "-i", "nullsrc=s=256x256:d=0.1", 
                 "-c:v", "h264_nvenc", "-f", "null", "-"],
                capture_output=True, timeout=10
            )
            if test.returncode == 0:
                print("[GPU] NVIDIA NVENC detected and working!")
                return "h264_nvenc"
    except:
        pass
    
    # Check for AMD/Intel VAAPI
    try:
        if os.path.exists("/dev/dri/renderD128"):
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-f", "lavfi", "-i", "nullsrc=s=256x256:d=0.1",
                 "-vaapi_device", "/dev/dri/renderD128", "-vf", "hwupload,scale_vaapi=256:256",
                 "-c:v", "h264_vaapi", "-f", "null", "-"],
                capture_output=True, timeout=10
            )
            if result.returncode == 0:
                print("[GPU] VAAPI detected and working!")
                return "h264_vaapi"
    except:
        pass
    
    print("[GPU] No GPU encoder available, using CPU (libx264)")
    return "libx264"


def publish_progress(job_id: int, status: str, message: str, progress: int = 0):
    """Publish progress to Redis for WebSocket streaming (if available)."""
    if not REDIS_URL:
        return
    try:
        import redis
        # Handle SSL for Upstash (rediss://)
        r = redis.from_url(REDIS_URL, decode_responses=True)
        data = json.dumps({
            "job_id": job_id,
            "status": status,
            "message": message,
            "progress": progress
        })
        r.publish(f"job:{job_id}:progress", data)
        r.setex(f"job:{job_id}:latest", 3600, data)
    except Exception as e:
        print(f"[Redis] Progress publish error: {e}")


def parse_json_safe(raw: str) -> dict:
    try:
        return parse_json_response(raw)
    except Exception:
        return {}


def normalize_agent_result(result: object) -> dict:
    """Convert agent output into a plain dict safely."""
    if not result:
        return {}
    if hasattr(result, "model_dump"):
        try:
            return result.model_dump()  # type: ignore[no-any-return]
        except Exception:
            return {}
    if isinstance(result, dict):
        if "raw_response" in result:
            return parse_json_safe(result.get("raw_response", "{}"))
        return result
    return {}


async def process_job(job_id: int, source_path: str, pacing: str = "medium", mood: str = "professional", ratio: str = "16:9", tier: str = "pro", platform: str = "youtube", brand_safety: str = "standard"):
    """
    Master Workflow Router
    """
    if tier == "pro":
        await process_job_pro(job_id, source_path, pacing, mood, ratio, platform, brand_safety)
    else:
        await process_job_standard(job_id, source_path, pacing, mood, ratio, platform, brand_safety)


async def process_job_standard(job_id: int, source_path: str, pacing: str = "medium", mood: str = "professional", ratio: str = "16:9", platform: str = "youtube", brand_safety: str = "standard"):
    """
    [v3.0] Standard Parallel Workflow (Free Tier)
    Fast, efficient, but loose synchronization.
    """
    print(f"[Workflow v3] Starting Standard job {job_id}")
    publish_progress(job_id, "processing", "Initializing Standard Workflow...", 5)
    
    # Detect GPU encoder once at start
    video_encoder = detect_gpu_encoder()
    
    async with AsyncSession(engine) as session:
        job = await session.get(Job, job_id)
        if not job: return
        job.status = "processing"
        job.progress_message = "Initializing Standard Workflow..."
        user_id = job.user_id
        await session.commit()

    try:
        # === PHASE 1: Analysis (10%) ===
        await update_status(job_id, "processing", "[FRAME] Analyzing keyframes...")
        publish_progress(job_id, "processing", "Analyzing video keyframes...", 10)
        memory_context = await hybrid_memory.get_agent_context(user_id)
        
        keyframe_payload = {"source_path": source_path, "pacing": pacing}
        keyframe_resp = await keyframe_agent.run(keyframe_payload)
        keyframe_data = parse_json_safe(keyframe_resp.get("raw_response", "{}"))
        print(f"[Workflow] Keyframe Analysis: {keyframe_data.get('scene_count', 'N/A')} scenes")
        
        # === PHASE 2: Director Planning (20%) ===
        max_retries = 1
        attempt = 0
        final_output_path = None
        current_feedback = ""
        director_plan = {}

        while attempt <= max_retries:
            attempt += 1
            status_prefix = f"[Take {attempt}]" if attempt > 1 else "[MAX]"
            await update_status(job_id, "processing", f"{status_prefix} Director planning...")
            publish_progress(job_id, "processing", f"Director planning strategy (Take {attempt})...", 20)
            
            director_payload = {
                "source_path": source_path,
                "pacing": pacing,
                "mood": mood, 
                "ratio": ratio,
                "keyframe_analysis": keyframe_data,
                "memory_context": memory_context,
                "feedback": current_feedback
            }
            
            plan = await director_agent.run(director_payload)
            director_plan = normalize_agent_result(plan)
            print(f"[Workflow] Director Plan: {director_plan.get('strategy', 'No strategy')}")

            # === PHASE 3: Parallel Specialists (30-60%) ===
            await update_status(job_id, "processing", f"{status_prefix} Specialists working...")
            publish_progress(job_id, "processing", "6 AI agents working in parallel...", 35)
            
            # Run 6 agents in parallel using asyncio.gather()
            specialist_tasks = [
                cutter_agent.run({"plan": director_plan}),
                color_agent.run({"plan": director_plan, "mood": mood}),
                audio_agent.run({"plan": director_plan}),
                transition_agent.run({"plan": director_plan, "keyframes": keyframe_data}),
                vfx_agent.run({"plan": director_plan, "mood": mood}),
                script_agent.run({"source_path": source_path}),
            ]
            
            results = await asyncio.gather(*specialist_tasks, return_exceptions=True)
            publish_progress(job_id, "processing", "Specialist analysis complete!", 55)
            
            cutter_data = results[0] if not isinstance(results[0], Exception) else None
            color_data = results[1] if not isinstance(results[1], Exception) else None
            audio_data = results[2] if not isinstance(results[2], Exception) else None
            transition_data = results[3] if not isinstance(results[3], Exception) else None
            vfx_data = results[4] if not isinstance(results[4], Exception) else None
            script_data = results[5] if not isinstance(results[5], Exception) else None
            
            # Normalize agent outputs (can be Pydantic or raw dict)
            vfx_res = normalize_agent_result(vfx_data)
            transition_res = normalize_agent_result(transition_data)
            
            print(f"[Workflow] Transitions: {transition_res.get('style_note', 'None')}")
            print(f"[Workflow] VFX: {vfx_res.get('style_note', 'None')}")

            # === PHASE 4: Render (60-80%) ===
            await update_status(job_id, "processing", f"{status_prefix} Rendering video...")
            publish_progress(job_id, "processing", f"Rendering with {video_encoder}...", 65)
            
            output_filename = f"job-{job_id}-take{attempt}.mp4"
            output_abs = Path(settings.storage_root) / "outputs" / output_filename
            output_abs.parent.mkdir(parents=True, exist_ok=True)
            
            src = Path(source_path)
            if not src.exists(): src = Path(".") / source_path
            
            # Build FFmpeg filter chain
            vf_filters = ["scale=1280:720:force_original_aspect_ratio=decrease", "pad=1280:720:(ow-iw)/2:(oh-ih)/2"]
            
            # Add VFX filters
            for effect in vfx_res.get("effects", []):
                if isinstance(effect, dict) and "filter" in effect:
                    vf_filters.append(effect["filter"])
            
            # Watermark for free tier
            watermark_text = "Proedit.ai (Free)"
            vf_filters.append(f"drawtext=text='{watermark_text}':fontsize=24:fontcolor=white@0.5:x=w-tw-20:y=h-th-20")
            
            vf = ",".join(vf_filters)
            af = "loudnorm=I=-16:TP=-1.5:LRA=11"
            
            # Build FFmpeg command with GPU acceleration if available
            ffmpeg_path = "./tools/ffmpeg-8.0.1-essentials_build/bin/ffmpeg.exe" if os.path.exists("./tools/ffmpeg-8.0.1-essentials_build/bin/ffmpeg.exe") else "ffmpeg"
            cmd = [ffmpeg_path, "-y", "-i", str(src)]
            
            if video_encoder == "h264_nvenc":
                # NVIDIA GPU encoding
                cmd += ["-c:v", "h264_nvenc", "-preset", "p4", "-cq", "23"]
            elif video_encoder == "h264_vaapi":
                # AMD/Intel GPU encoding
                cmd += ["-vaapi_device", "/dev/dri/renderD128", "-c:v", "h264_vaapi", "-qp", "23"]
            else:
                # CPU fallback
                cmd += ["-c:v", "libx264", "-preset", "fast", "-crf", "23"]
            
            cmd += ["-vf", vf, "-af", af, "-threads", "4", str(output_abs)]
            
            # Path handled above

            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()
            
            publish_progress(job_id, "processing", "Render complete!", 80)
            
            if proc.returncode != 0 or not output_abs.exists():
                shutil.copy(src, output_abs)

            final_output_path = f"storage/outputs/{output_filename}"

            # === PHASE 5: QC Review (85%) ===
            if attempt <= max_retries:
                await update_status(job_id, "processing", f"[THE PRODUCER] Reviewing...")
                publish_progress(job_id, "processing", "Quality control review...", 85)
                
                qc_payload = {"user_request": {"pacing": pacing, "mood": mood}, "director_plan": director_plan}
                qc_data = await qc_agent.run(qc_payload)
                
                if qc_data.approved:
                    print("[Workflow] QC Approved!")
                    break
                else:
                    current_feedback = qc_data.feedback or "Improvements needed."
                    print(f"[Workflow] QC Rejected: {current_feedback}")
                    await hybrid_memory.record_feedback(user_id, current_feedback)
                    continue 

        # === PHASE 6: Post-Production (90-100%) ===
        await update_status(job_id, "processing", "[THUMB] Generating thumbnail...")
        publish_progress(job_id, "processing", "Generating thumbnail & metadata...", 90)
        
        # Parallel post-production
        thumb_task = thumbnail_agent.run({"source_path": source_path, "mood": mood})
        meta_task = metadata_agent.run({"plan": director_plan})
        
        post_results = await asyncio.gather(thumb_task, meta_task, return_exceptions=True)
        
        thumb_data = parse_json_safe(post_results[0].get("raw_response", "{}")) if isinstance(post_results[0], dict) else {}
        meta_data = parse_json_safe(post_results[1].get("raw_response", "{}")) if isinstance(post_results[1], dict) else {}
        
        # Extract thumbnail
        final_thumb_rel_path = None
        if thumb_data.get("best_timestamp"):
            thumb_path = Path(settings.storage_root) / "outputs" / f"job-{job_id}-thumb.jpg"
            thumb_cmd = ["ffmpeg", "-y", "-ss", str(thumb_data["best_timestamp"]), "-i", str(src), "-vframes", "1", "-q:v", "2", str(thumb_path)]
            thumb_proc = await asyncio.create_subprocess_exec(*thumb_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await thumb_proc.communicate()
            if thumb_path.exists():
                final_thumb_rel_path = f"storage/outputs/job-{job_id}-thumb.jpg"
        
        # Subtitles (Use existing logic)
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
            
        await update_status(job_id, "complete", completion_msg, final_rel_path, final_thumb_rel_path)
        publish_progress(job_id, "complete", completion_msg, 100)
        print(f"[Workflow] Job {job_id} complete!")

    except Exception as e:
        print(f"[Workflow v3] Job {job_id} failed: {e}")
        import traceback
        traceback.print_exc()
        await update_status(job_id, "failed", f"Processing failed: {str(e)[:100]}")
        publish_progress(job_id, "failed", f"Processing failed: {str(e)[:100]}", 0)


async def process_job_pro(job_id: int, source_path: str, pacing: str = "medium", mood: str = "professional", ratio: str = "16:9", platform: str = "youtube", brand_safety: str = "standard"):
    """
    [v4.0] Hollywood Pipeline (Pro Tier) - LangGraph + MoviePy
    Hierarchical: Director -> Cutter -> (Visuals/Audio) -> Compiler
    """
    print(f"[Workflow v4] Starting Pro job {job_id} (LangGraph)")
    publish_progress(job_id, "processing", "Initializing Hollywood Pipeline (LangGraph)...", 5)
    
    async with AsyncSession(engine) as session:
        job = await session.get(Job, job_id)
        if not job: return
        job.status = "processing"
        job.progress_message = "Initializing Hollywood Pipeline..."
        await session.commit()

    try:
        from ..graph.workflow import app as graph_app
        
        # Initial State
        initial_state = {
            "job_id": job_id,
            "source_path": source_path,
            "user_request": {"pacing": pacing, "mood": mood, "ratio": ratio, "platform": platform, "brand_safety": brand_safety},
            "tier": "pro",
            "errors": []
        }
        
        # Run Graph
        print("[Graph] Streaming workflow (with checkpointing)...")
        config = {"configurable": {"thread_id": str(job_id)}}
        final_state: dict = {}
        async for event in graph_app.astream(initial_state, config=config):
            for node_name, state in event.items():
                # astream yields partial updates; merge to preserve prior keys like output_path
                if isinstance(state, dict):
                    final_state.update(state)
                else:
                    final_state = state
                
                # Create a human-readable status message and percentage from node name
                node_to_info = {
                    "director": {"msg": "Director Planning...", "p": 15},
                    "brand_safety": {"msg": "Guardian: Brand Safety Check...", "p": 25},
                    "ab_test": {"msg": "Variant: A/B Test Optimization...", "p": 35},
                    "cutter": {"msg": "AI Smart Cutting...", "p": 50},
                    "audio": {"msg": "Audio Mastery...", "p": 65},
                    "visuals": {"msg": "Visual Enhancement...", "p": 80},
                    "validator": {"msg": "Quality Review...", "p": 90},
                    "compiler": {"msg": "Final Rendering...", "p": 95},
                }
                
                info = node_to_info.get(node_name, {"msg": f"Stage: {node_name}", "p": 50})
                msg = info["msg"]
                progress_p = info["p"]
                
                # Update DB and Publish
                await update_status(job_id, "processing", f"[AI] {msg}")
                publish_progress(job_id, "processing", msg, progress_p)
        
        if final_state.get("errors"):
            raise Exception(f"Graph Errors: {final_state['errors']}")
            
        output_rel_path = final_state.get("output_path")
        if not output_rel_path:
            raise Exception("No output path returned from Graph.")
            
        # Success
        completion_msg = "🎬 Pro Edit Ready!"
        
        # Extract metadata
        media_intelligence = final_state.get("media_intelligence")
        qc_result = final_state.get("qc_result")
        director_plan = final_state.get("director_plan")
        brand_safety_result = final_state.get("brand_safety_result")
        ab_test_result = final_state.get("ab_test_result")
        
        await update_status(
            job_id, 
            "complete", 
            completion_msg, 
            output_rel_path, 
            media_intelligence=media_intelligence,
            qc_result=qc_result,
            director_plan=director_plan,
            brand_safety_result=brand_safety_result,
            ab_test_result=ab_test_result
        )
        publish_progress(job_id, "complete", completion_msg, 100)
        print(f"[Workflow v4] Job {job_id} complete!")

    except Exception as e:
        print(f"[Workflow v4] Job {job_id} failed: {e}")
        import traceback
        traceback.print_exc()
        await update_status(job_id, "failed", f"Processing failed: {str(e)[:100]}")
        publish_progress(job_id, "failed", f"Processing failed: {str(e)[:100]}", 0)


async def update_status(
    job_id: int, 
    status: str, 
    message: str, 
    output_path: str | None = None, 
    thumbnail_path: str | None = None,
    media_intelligence: dict | None = None,
    qc_result: dict | None = None,
    director_plan: dict | None = None,
    brand_safety_result: dict | None = None,
    ab_test_result: dict | None = None
):
    async with AsyncSession(engine) as session:
        job = await session.get(Job, job_id)
        if job:
            if job.cancel_requested:
                return
            job.status = status
            job.progress_message = message
            if output_path:
                job.output_path = output_path
            if thumbnail_path:
                job.thumbnail_path = thumbnail_path
                
            # Update Phase 5 fields if provided
            if media_intelligence:
                job.media_intelligence = media_intelligence
            if qc_result:
                job.qc_result = qc_result
            if director_plan:
                job.director_plan = director_plan
            if brand_safety_result:
                job.brand_safety_result = brand_safety_result
            if ab_test_result:
                job.ab_test_result = ab_test_result
                
            await session.commit()
