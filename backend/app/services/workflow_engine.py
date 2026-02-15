import asyncio
import asyncio.subprocess
import json
import subprocess
import shutil
import os
import copy
from pathlib import Path
import structlog
from sqlalchemy import select
from ..db import SessionLocal, engine
from ..models import Job
from ..config import settings
from ..agents import (
    director_agent, cutter_agent, subtitle_agent, audio_agent, 
    color_agent, qc_agent, metadata_agent, transition_agent,
    vfx_agent, keyframe_agent, thumbnail_agent, script_agent
)
from ..agents.base import parse_json_response
from .memory.hybrid_memory import hybrid_memory
from .concurrency import limits
from .metrics_service import metrics_service
from .n8n_service import n8n_service
from .post_production_depth import build_audio_post_filter, build_subtitle_filter

# Redis for progress publishing (optional)
REDIS_URL = os.getenv("REDIS_URL")
logger = structlog.get_logger()


def _resolve_tool_path(tool_name: str) -> str:
    """Resolve bundled FFmpeg tools first, then fallback to PATH."""
    ext = ".exe" if os.name == "nt" else ""
    repo_root = Path(__file__).resolve().parents[3]
    bundled = repo_root / "tools" / "ffmpeg-8.0.1-essentials_build" / "bin" / f"{tool_name}{ext}"
    if bundled.exists():
        return str(bundled)
    on_path = shutil.which(tool_name)
    if on_path:
        return on_path
    if tool_name == "ffmpeg":
        try:
            import imageio_ffmpeg

            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass
    return tool_name


def detect_gpu_encoder() -> str:
    """
    Detect available GPU encoder for FFmpeg.
    Returns encoder name or 'libx264' as fallback.
    """
    # Check for NVIDIA GPU (NVENC)
    try:
        ffmpeg_bin = _resolve_tool_path("ffmpeg")
        result = subprocess.run(
            [ffmpeg_bin, "-hide_banner", "-encoders"],
            capture_output=True, text=True, timeout=5
        )
        if "h264_nvenc" in result.stdout:
            # Verify NVENC actually works
            test = subprocess.run(
                [ffmpeg_bin, "-hide_banner", "-f", "lavfi", "-i", "nullsrc=s=256x256:d=0.1", 
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
            ffmpeg_bin = _resolve_tool_path("ffmpeg")
            result = subprocess.run(
                [ffmpeg_bin, "-hide_banner", "-f", "lavfi", "-i", "nullsrc=s=256x256:d=0.1",
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


def publish_progress(job_id: int, status: str, message: str, progress: int = 0, user_id: int | None = None):
    """Publish progress to Redis for WebSocket streaming (if available)."""
    if not REDIS_URL:
        return
    try:
        import redis
        # Handle SSL for Upstash (rediss://)
        r = redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=2, socket_connect_timeout=2)
        data = json.dumps({
            "job_id": job_id,
            "status": status,
            "message": message,
            "progress": progress
        })
        # Publish to job channel (legacy)
        r.publish(f"job:{job_id}:progress", data)
        r.setex(f"job:{job_id}:latest", 3600, data)
        
        # Publish to user channel (new)
        if user_id:
            r.publish(f"user:{user_id}:jobs", data)
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


def _coerce_duration(value: object, fallback: float = 30.0) -> float:
    try:
        duration = float(value)  # type: ignore[arg-type]
        if duration > 0:
            return duration
    except Exception:
        pass
    return fallback


def _coerce_float_bounded(value: object, fallback: float, minimum: float, maximum: float) -> float:
    try:
        parsed = float(value)  # type: ignore[arg-type]
    except Exception:
        parsed = fallback
    return min(max(parsed, minimum), maximum)


def _build_highlight_cuts(duration: float, pacing: str) -> list[dict]:
    """Create deterministic highlight windows so output is not pass-through."""
    pace = (pacing or "medium").lower()
    target_ratio = {
        "slow": 0.8,
        "medium": 0.6,
        "fast": 0.45,
    }.get(pace, 0.6)
    clip_len = {
        "slow": 5.0,
        "medium": 3.5,
        "fast": 2.2,
    }.get(pace, 3.5)

    target_total = max(8.0, min(duration * target_ratio, duration))
    parts = max(2, int(round(target_total / clip_len)))
    gap = duration / (parts + 1)
    cuts: list[dict] = []
    for i in range(parts):
        center = gap * (i + 1)
        start = max(0.0, center - (clip_len / 2))
        end = min(duration, start + clip_len)
        if end - start >= 0.8:
            cuts.append({"start": round(start, 3), "end": round(end, 3), "reason": "auto-highlight"})
    return cuts


def ensure_editing_cuts(cuts: list[dict], duration: float, pacing: str, min_change_ratio: float = 0.9) -> list[dict]:
    """
    Normalize AI cuts and enforce visible edits.
    If cuts are missing or nearly pass-through, generate highlight cuts.
    """
    valid: list[dict] = []
    for cut in cuts or []:
        try:
            start = max(0.0, float(cut.get("start", 0)))
            end = min(duration, float(cut.get("end", 0)))
        except Exception:
            continue
        if end - start >= 0.2:
            valid.append({"start": start, "end": end, "reason": cut.get("reason", "ai-cut")})

    if not valid:
        return _build_highlight_cuts(duration, pacing)

    selected = sum(max(0.0, c["end"] - c["start"]) for c in valid)
    if duration >= 15.0 and selected >= duration * min_change_ratio:
        return _build_highlight_cuts(duration, pacing)
    return valid


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
    tracker = metrics_service.get_tracker(job_id)
    tracker.start_phase("total_workflow")
    print(f"[Workflow v3] Starting Standard job {job_id}")
    user_id = None
    # Detect GPU encoder once at start
    video_encoder = detect_gpu_encoder()
    
    media_intelligence = None
    post_settings = {}
    async with SessionLocal() as session:
        job = await session.get(Job, job_id)
        if not job: return
        job.status = "processing"
        job.progress_message = "Initializing Standard Workflow..."
        user_id = job.user_id
        media_intelligence = copy.deepcopy(job.media_intelligence) if job.media_intelligence else None
        post_settings = copy.deepcopy(job.post_settings) if job.post_settings else {}
        await session.commit()

    publish_progress(job_id, "processing", "Initializing Standard Workflow...", 5, user_id=user_id)

    try:
        # === PHASE 1: Analysis (10%) ===
        tracker.start_phase("analysis")
        await update_status(job_id, "processing", "[FRAME] Analyzing keyframes...")
        publish_progress(job_id, "processing", "Analyzing video keyframes...", 10, user_id=user_id)
        memory_context = await hybrid_memory.get_agent_context(user_id)
        
        # Holy Grail: Use client-provided intelligence if available
        if media_intelligence and media_intelligence.get("visual", {}).get("scenes"):
            print(f"[Workflow] Using client-provided intelligence for Standard job {job_id}")
            visual_data = media_intelligence["visual"]
            keyframe_data = {
                "scene_count": len(visual_data["scenes"]),
                "scenes": visual_data["scenes"],
                "duration": visual_data.get("metadata", {}).get("duration", 0),
                "source": "client"
            }
        else:
            keyframe_payload = {"source_path": source_path, "pacing": pacing}
            keyframe_resp = await keyframe_agent.run(keyframe_payload)
            keyframe_data = parse_json_safe(keyframe_resp.get("raw_response", "{}"))
        
        print(f"[Workflow] Keyframe Analysis: {keyframe_data.get('scene_count', 'N/A')} scenes")
        tracker.end_phase("analysis")
        
        # === PHASE 2: Director Planning (20%) ===
        tracker.start_phase("planning")
        max_retries = 1
        attempt = 0
        final_output_path = None
        current_feedback = ""
        director_plan = {}

        while attempt <= max_retries:
            attempt += 1
            status_prefix = f"[Take {attempt}]" if attempt > 1 else "[MAX]"
            await update_status(job_id, "processing", f"{status_prefix} Director planning...")
            publish_progress(job_id, "processing", f"Director planning strategy (Take {attempt})...", 20, user_id=user_id)
            
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
            tracker.end_phase("planning")

            # === PHASE 3: Parallel Specialists (30-60%) ===
            tracker.start_phase("specialists")
            await update_status(job_id, "processing", f"{status_prefix} Specialists working...")
            publish_progress(job_id, "processing", "6 AI agents working in parallel...", 35, user_id=user_id)
            
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
            publish_progress(job_id, "processing", "Specialist analysis complete!", 55, user_id=user_id)
            
            cutter_data = results[0] if not isinstance(results[0], Exception) else None
            color_data = results[1] if not isinstance(results[1], Exception) else None
            audio_data = results[2] if not isinstance(results[2], Exception) else None
            transition_data = results[3] if not isinstance(results[3], Exception) else None
            vfx_data = results[4] if not isinstance(results[4], Exception) else None
            script_data = results[5] if not isinstance(results[5], Exception) else None
            
            # --- PHASE 3.5: Subtitles (New) ---
            srt_path = None
            try:
                sub_resp = await subtitle_agent.run({"source_path": source_path})
                srt_content = sub_resp.get("raw_response", "") if isinstance(sub_resp, dict) else ""
                if srt_content:
                    srt_tmp = Path(settings.storage_root) / "outputs" / f"job-{job_id}.srt"
                    srt_tmp.parent.mkdir(parents=True, exist_ok=True)
                    with open(srt_tmp, "w", encoding="utf-8") as f:
                        f.write(srt_content)
                    srt_path = srt_tmp
            except Exception as se:
                print(f"[Workflow] Subtitle generation failed: {se}")

            # Normalize agent outputs (can be Pydantic or raw dict)
            vfx_res = normalize_agent_result(vfx_data)
            transition_res = normalize_agent_result(transition_data)
            color_res = normalize_agent_result(color_data)
            
            print(f"[Workflow] Transitions: {transition_res.get('style_note', 'None')}")
            print(f"[Workflow] VFX: {vfx_res.get('style_note', 'None')}")
            print(f"[Workflow] Color: {color_res.get('color_mood', 'None')}")
            tracker.end_phase("specialists")

            # === PHASE 4: Render (60-80%) ===
            tracker.start_phase("rendering")
            await update_status(job_id, "processing", f"{status_prefix} Rendering video...")
            
            src = Path(source_path)
            if not src.exists(): src = Path(".") / source_path
            
            output_filename = f"job-{job_id}-take{attempt}.mp4"
            output_abs = Path(settings.storage_root) / "outputs" / output_filename
            output_abs.parent.mkdir(parents=True, exist_ok=True)
            
            # Build FFmpeg filter chain
            vf_filters = ["scale=1280:720:force_original_aspect_ratio=decrease", "pad=1280:720:(ow-iw)/2:(oh-ih)/2"]
            
            # Color Filters
            if color_res.get("ffmpeg_color_filter"):
                vf_filters.append(color_res["ffmpeg_color_filter"])
            
            # VFX Filters
            if vfx_res.get("effects"):
                for effect in vfx_res["effects"]:
                    if isinstance(effect, dict) and "filter" in effect:
                        vf_filters.append(effect["filter"])
            elif vfx_res.get("ffmpeg_filter"):
                vf_filters.append(vfx_res["ffmpeg_filter"].replace('-vf "', '').replace('"', '').strip())
            
            if srt_path:
                vf_filters.append(build_subtitle_filter(str(srt_path), platform))
            
            watermark_text = "Proedit.ai (Free)"
            vf_filters.append(f"drawtext=text='{watermark_text}':fontsize=24:fontcolor=white@0.5:x=w-tw-20:y=h-th-20")
            
            vf = ",".join(vf_filters)
            af = "loudnorm=I=-16:TP=-1.5:LRA=11"
            
            # 1. Attempt Modal Offloading (GPU Cluster)
            from .modal_service import modal_service
            modal_output = None
            if modal_service.enabled:
                publish_progress(job_id, "processing", "Offloading to GPU Cluster (Modal)...", 65, user_id=user_id)
                modal_output = await modal_service.render_video(
                    job_id=job_id,
                    source_path=source_path,
                    cuts=cutter_data.get("cuts", []) if isinstance(cutter_data, dict) else [],
                    fps=24,
                    crf=23,
                    vf_filters=",".join(vf_filters),
                    af_filters=af
                )
                if modal_output:
                    print(f"[Workflow] Modal Rendering Success for job {job_id}")
                    final_output_path = modal_output
                    publish_progress(job_id, "processing", "Modal render complete!", 80, user_id=user_id)
                else:
                    print(f"[Workflow] Modal Rendering Failed for job {job_id}, falling back...")

            if not modal_output:
                # 2. Local Parallel Render
                from .rendering_orchestrator import rendering_orchestrator
                
                publish_progress(job_id, "processing", f"Rendering scenes in parallel...", 65, user_id=user_id)
                
                # Standard workflow often has 'cuts' in cutter_data
                raw_cuts = cutter_data.get("cuts", []) if isinstance(cutter_data, dict) else []
                duration = _coerce_duration(keyframe_data.get("duration", 30.0), fallback=30.0)
                cuts = ensure_editing_cuts(raw_cuts, duration=duration, pacing=pacing)
                speed_profile = str(post_settings.get("speed_profile", "balanced")).lower()
                speed = {"slow": 0.94, "balanced": 1.04, "fast": 1.10}.get(speed_profile, 1.04)
                transition_style = post_settings.get(
                    "transition_style",
                    director_plan.get("transition_style", "cut" if pacing == "fast" else "dissolve"),
                )
                transition_duration = _coerce_float_bounded(
                    post_settings.get(
                        "transition_duration",
                        director_plan.get("transition_duration", 0.2 if pacing == "fast" else 0.3),
                    ),
                    fallback=0.25,
                    minimum=0.1,
                    maximum=1.5,
                )
                cuts = [{**c, "speed": speed} for c in cuts]

                success = await rendering_orchestrator.render_parallel(
                    job_id=job_id,
                    source_path=source_path,
                    cuts=cuts,
                    output_path=str(output_abs),
                    vf_filters=",".join(vf_filters) if vf_filters else None,
                    af_filters=build_audio_post_filter(
                        {"ducking_segments": []},
                        platform=platform,
                        mood=mood,
                    ) or af,
                    transition_style=transition_style,
                    transition_duration=transition_duration,
                    user_id=user_id
                )
                
                if success:
                    final_output_path = f"storage/outputs/{output_filename}"
                else:
                    print(f"[Workflow] Parallel Render Failed for job {job_id}, falling back to raw copy")
                    shutil.copy(src, output_abs)
                    final_output_path = f"storage/outputs/{output_filename}"
                    await update_status(job_id, "complete", "Edit finished with degraded quality (fallback applied due to render failure).", final_output_path)

            # === PHASE 5: QC Review (85%) ===
            if attempt <= max_retries:
                await update_status(job_id, "processing", f"[THE PRODUCER] Reviewing...")
                publish_progress(job_id, "processing", "Quality control review...", 85, user_id=user_id)
                
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
        publish_progress(job_id, "processing", "Generating thumbnail & metadata...", 90, user_id=user_id)
        
        # Parallel post-production
        thumb_task = thumbnail_agent.run({"source_path": source_path, "mood": mood})
        meta_task = metadata_agent.run({"plan": director_plan})
        
        post_results = await asyncio.gather(thumb_task, meta_task, return_exceptions=True)
        
        thumb_data = parse_json_safe(post_results[0].get("raw_response", "{}")) if isinstance(post_results[0], dict) else {}
        meta_data = parse_json_safe(post_results[1].get("raw_response", "{}")) if isinstance(post_results[1], dict) else {}
        
        # Extract thumbnail
        final_thumb_rel_path = None
        if thumb_data.get("best_timestamp"):
            ffmpeg_bin = _resolve_tool_path("ffmpeg")
            thumb_path = Path(settings.storage_root) / "outputs" / f"job-{job_id}-thumb.jpg"
            thumb_cmd = [ffmpeg_bin, "-y", "-ss", str(thumb_data["best_timestamp"]), "-i", str(src), "-vframes", "1", "-q:v", "2", str(thumb_path)]
            thumb_proc = await asyncio.create_subprocess_exec(*thumb_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await thumb_proc.communicate()
            if thumb_path.exists():
                final_thumb_rel_path = f"storage/outputs/job-{job_id}-thumb.jpg"
        
        # Post-Production Logic Removed (Subtitles handled in Phase 3.5/4)

        # Final output
        final_rel_path = f"storage/outputs/job-{job_id}.mp4"
        final_abs_path = Path(settings.storage_root) / "outputs" / f"job-{job_id}.mp4"
        take_path = Path(settings.storage_root) / "outputs" / f"job-{job_id}-take{attempt}.mp4"
        if take_path.exists():
            shutil.move(take_path, final_abs_path)
        
        # Completion
        completion_msg = "Your video is ready!"
        if meta_data.get("title"):
            completion_msg = f"{meta_data['title']} is ready!"
            
        tracker.end_phase("total_workflow")
        performance_metrics = metrics_service.finalize(job_id)
            
        await update_status(job_id, "complete", completion_msg, final_rel_path, final_thumb_rel_path, performance_metrics=performance_metrics)
        publish_progress(job_id, "complete", completion_msg, 100, user_id=user_id)
        print(f"[Workflow] Job {job_id} complete!")

    except Exception as e:
        print(f"[Workflow v3] Job {job_id} failed: {e}")
        import traceback
        traceback.print_exc()
        await update_status(job_id, "failed", f"Processing failed: {str(e)[:100]}")
        publish_progress(job_id, "failed", f"Processing failed: {str(e)[:100]}", 0, user_id=user_id)


async def process_job_pro(job_id: int, source_path: str, pacing: str = "medium", mood: str = "professional", ratio: str = "16:9", platform: str = "youtube", brand_safety: str = "standard"):
    """
    [v4.0] Hollywood Pipeline (Pro Tier) - LangGraph + MoviePy
    Hierarchical: Director -> Cutter -> (Visuals/Audio) -> Compiler
    """
    tracker = metrics_service.get_tracker(job_id)
    tracker.start_phase("total_workflow")
    print(f"[Workflow v4] Starting Pro job {job_id} (LangGraph)")
    user_id = None
    media_intelligence = None
    post_settings = {}
    async with SessionLocal() as session:
        job = await session.get(Job, job_id)
        if not job: return
        job.status = "processing"
        job.progress_message = "Initializing Hollywood Pipeline..."
        user_id = job.user_id
        media_intelligence = copy.deepcopy(job.media_intelligence) if job.media_intelligence else None
        post_settings = copy.deepcopy(job.post_settings) if job.post_settings else {}
        await session.commit()

    publish_progress(job_id, "processing", "Initializing Hollywood Pipeline (LangGraph)...", 5, user_id=user_id)

    try:
        from ..graph.workflow import app as graph_app
        
        # Initial State
        initial_state = {
            "job_id": job_id,
            "source_path": source_path,
            "user_request": {
                "pacing": pacing,
                "mood": mood,
                "ratio": ratio,
                "platform": platform,
                "brand_safety": brand_safety,
                "transition_style": post_settings.get("transition_style", "dissolve"),
                "transition_duration": _coerce_float_bounded(
                    post_settings.get("transition_duration", 0.25),
                    fallback=0.25,
                    minimum=0.1,
                    maximum=1.5,
                ),
                "speed_profile": post_settings.get("speed_profile", "balanced"),
                "subtitle_preset": post_settings.get("subtitle_preset", "platform_default"),
                "color_profile": post_settings.get("color_profile", "natural"),
                "skin_protect_strength": _coerce_float_bounded(
                    post_settings.get("skin_protect_strength", 0.5),
                    fallback=0.5,
                    minimum=0.0,
                    maximum=1.0,
                ),
            },
            "media_intelligence": media_intelligence,
            "tier": "pro",
            "user_id": user_id,
            "errors": []
        }
        
        # Run Graph
        tracker.start_phase("graph_execution")
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
                    "media_intelligence": {"msg": "Analyzing Media Content...", "p": 10},
                    "director": {"msg": "Director Planning...", "p": 15},
                    "platform": {"msg": "Platform Adaptation...", "p": 20},
                    "brand_safety": {"msg": "Guardian: Brand Safety Check...", "p": 25},
                    "ab_test": {"msg": "Variant: A/B Test Optimization...", "p": 35},
                    "cutter": {"msg": "AI Smart Cutting...", "p": 50},
                    "audio": {"msg": "Audio Mastery...", "p": 65},
                    "visuals": {"msg": "Visual Enhancement...", "p": 80},
                    "hook": {"msg": "Optimizing Hook...", "p": 82},
                    "validator": {"msg": "Quality Review...", "p": 85},
                    "qc_gate": {"msg": "Final Producer Check...", "p": 90},
                    "iteration_control": {"msg": "Refining Content...", "p": 92},
                    "compiler": {"msg": "Final Rendering...", "p": 95},
                }
                
                info = node_to_info.get(node_name, {"msg": f"Stage: {node_name}", "p": 50})
                msg = info["msg"]
                progress_p = info["p"]
                
                # Update DB and Publish
                await update_status(job_id, "processing", f"[AI] {msg}")
                publish_progress(job_id, "processing", msg, progress_p, user_id=user_id)
        # 1. Finalize State
        tracker.end_phase("graph_execution")
        output_rel_path = final_state.get("output_path")
        graph_errors = final_state.get("errors") or []
        if graph_errors and not output_rel_path:
            raise Exception(f"Graph Errors: {graph_errors}")
        if not output_rel_path:
            raise Exception("No output path returned from Graph.")
            
        # Success
        tracker.end_phase("total_workflow")
        performance_metrics = metrics_service.finalize(job_id)

        completion_msg = "Pro Edit Ready!"
        timeout_total = int((performance_metrics or {}).get("stage_timeout_total", 0) or 0)
        if graph_errors or timeout_total > 0:
            completion_msg = "Pro Edit Ready (with degraded AI recommendations)"
        
        # Extract metadata
        media_intelligence = final_state.get("media_intelligence")
        qc_result = final_state.get("qc_result")
        director_plan = final_state.get("director_plan")
        brand_safety_result = final_state.get("brand_safety_result")
        ab_test_result = final_state.get("ab_test_result")
        audio_qa = final_state.get("audio_qa")
        color_qa = final_state.get("color_qa")
        subtitle_qa = final_state.get("subtitle_qa")
        
        await update_status(
            job_id, 
            "complete", 
            completion_msg, 
            output_rel_path, 
            media_intelligence=media_intelligence,
            qc_result=qc_result,
            director_plan=director_plan,
            brand_safety_result=brand_safety_result,
            ab_test_result=ab_test_result,
            audio_qa=audio_qa,
            color_qa=color_qa,
            subtitle_qa=subtitle_qa,
            performance_metrics=performance_metrics
        )
        publish_progress(job_id, "complete", completion_msg, 100, user_id=user_id)
        print(f"[Workflow v4] Job {job_id} complete!")

    except Exception as e:
        print(f"[Workflow v4] Job {job_id} failed: {e}")
        import traceback
        traceback.print_exc()
        await update_status(job_id, "failed", f"Processing failed: {str(e)[:100]}")
        publish_progress(job_id, "failed", f"Processing failed: {str(e)[:100]}", 0, user_id=user_id)


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
    ab_test_result: dict | None = None,
    audio_qa: dict | None = None,
    color_qa: dict | None = None,
    subtitle_qa: dict | None = None,
    performance_metrics: dict | None = None
):
    async with SessionLocal() as session:
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
            if media_intelligence is not None:
                job.media_intelligence = media_intelligence
            if qc_result is not None:
                job.qc_result = qc_result
            if director_plan is not None:
                job.director_plan = director_plan
            if brand_safety_result is not None:
                job.brand_safety_result = brand_safety_result
            if ab_test_result is not None:
                job.ab_test_result = ab_test_result
            if audio_qa is not None:
                job.audio_qa = audio_qa
            if color_qa is not None:
                job.color_qa = color_qa
            if subtitle_qa is not None:
                job.subtitle_qa = subtitle_qa
            if performance_metrics is not None:
                job.performance_metrics = performance_metrics
                
            await session.commit()
            if status in {"complete", "failed"}:
                try:
                    await n8n_service.send_job_status_event(job)
                except Exception as exc:
                    print(f"[n8n] webhook notify failed for job {job_id}: {exc}")
async def render_orchestrated_job(job_id: int, cuts: list, vf_filters: str | None = None, af_filters: str | None = None):
    """
    Directly renders a job using provided technical parameters, bypassing AI agents.
    Used for n8n/External Orchestration.
    """
    async with SessionLocal() as session:
        job = await session.get(Job, job_id)
        if not job: return
        job.status = "processing"
        job.progress_message = "Rendering orchestrated edit..."
        source_path = job.source_path
        user_id = job.user_id
        tier = job.tier
        await session.commit()

    publish_progress(job_id, "processing", "Starting technical render...", 5, user_id=user_id)
    
    from .rendering_orchestrator import rendering_orchestrator
    
    output_filename = f"job-{job_id}-orchestrated.mp4"
    output_abs = Path(settings.storage_root) / "outputs" / output_filename
    output_abs.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        tracker = metrics_service.get_tracker(job_id)
        tracker.start_phase("orchestrated_render")
        success = await rendering_orchestrator.render_parallel(
            job_id=job_id,
            source_path=source_path,
            cuts=cuts,
            output_path=str(output_abs),
            vf_filters=vf_filters,
            af_filters=af_filters,
            crf=18 if tier == "pro" else 23,
            preset="medium",
            user_id=user_id
        )
        tracker.end_phase("orchestrated_render")
        
        if success:
            final_rel_path = f"storage/outputs/{output_filename}"
            await update_status(job_id, "complete", "Orchestrated Edit Ready!", final_rel_path)
            publish_progress(job_id, "complete", "Orchestrated Edit Ready!", 100, user_id=user_id)
        else:
            raise Exception("Rendering failed.")
            
    except Exception as e:
        logger.error("orchestration_render_failed", job_id=job_id, error=str(e))
        await update_status(job_id, "failed", f"Orchestration failed: {str(e)}")
        publish_progress(job_id, "failed", f"Orchestration failed: {str(e)}", 0, user_id=user_id)
