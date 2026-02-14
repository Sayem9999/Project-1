from ..state import GraphState
from pathlib import Path
import os
# Configure MoviePy to use the correct FFmpeg binary (v2.0+ compatible)
def _resolve_ffmpeg():
    ext = ".exe" if os.name == 'nt' else ""
    paths_to_check = [
        f"tools/ffmpeg-8.0.1-essentials_build/bin/ffmpeg{ext}",
        f"../tools/ffmpeg-8.0.1-essentials_build/bin/ffmpeg{ext}",
        f"../../tools/ffmpeg-8.0.1-essentials_build/bin/ffmpeg{ext}"
    ]
    for p in paths_to_check:
        if os.path.exists(p):
            return os.path.abspath(p)
    return "ffmpeg"

FFMPEG_BINARY = _resolve_ffmpeg()
if FFMPEG_BINARY != "ffmpeg":
    os.environ["IMAGEIO_FFMPEG_EXE"] = FFMPEG_BINARY

from ...services.concurrency import limits
from ...config import settings
from ...services.workflow_engine import ensure_editing_cuts
from ...services.post_production_depth import (
    build_subtitle_filter,
    build_lower_third_filter,
)

async def compiler_node(state: GraphState) -> GraphState:
    """
    Compiler Node: Assembles the final video.
    Supports local rendering (CPU) and Modal offloading (GPU).
    """
    job_id = state.get("job_id")
    source_path = state.get("source_path")
    cuts = state.get("cuts", [])
    tier = state.get("tier", "standard")
    user_id = state.get("user_id")
    visual_effects = state.get("visual_effects", [])
    srt_path = state.get("srt_path")
    platform = state.get("user_request", {}).get("platform", "youtube")
    audio_post_filter = state.get("audio_post_filter")
    
    # 0. Build FFmpeg filter chain
    vf_list = []
    
    # Scale and Pad (Pro Default)
    vf_list.append("scale=1280:720:force_original_aspect_ratio=decrease")
    vf_list.append("pad=1280:720:(ow-iw)/2:(oh-ih)/2")

    # Add AI-generated effects
    for effect in visual_effects:
        if isinstance(effect, dict) and effect.get("type") == "ffmpeg_filter":
            val = effect.get("value", "").strip()
            if not val:
                continue
            
            # Robust LUT Check: AI often suggests LUTs that don't exist on disk, crashing FFmpeg
            if "lut3d" in val:
                import re
                # Extract filename from lut3d=filename.cube
                match = re.search(r"lut3d=['\"]?([^'\", ]+)['\"]?", val)
                if match:
                    lut_name = match.group(1)
                    # Common locations
                    lut_paths = [
                        Path(os.getcwd()) / "assets" / "luts" / lut_name,
                        Path(os.getcwd()) / "backend" / "assets" / "luts" / lut_name,
                        Path(os.getcwd()) / "app" / "assets" / "luts" / lut_name,
                    ]
                    
                    found = False
                    for p in lut_paths:
                        if p.exists():
                            # Path must be absolute and escaped for FFmpeg
                            abs_lut = str(p.absolute()).replace("\\", "/").replace(":", "\\:")
                            val = val.replace(lut_name, abs_lut)
                            found = True
                            break
                    
                    if not found:
                        print(f"--- [Graph] Compiler Warning: LUT '{lut_name}' not found. Stripping filter. ---")
                        # Strip the lut3d component from the filter string
                        val = re.sub(r",?lut3d=['\"]?[^'\", ]+['\"]?", "", val).strip(",")
            
            if val:
                vf_list.append(val)

    # Subtitles (highest priority, added last)
    if srt_path:
        vf_list.append(build_subtitle_filter(srt_path, platform))

    lower_third = build_lower_third_filter(state.get("title") or state.get("director_plan", {}).get("headline"))
    if lower_third:
        vf_list.append(lower_third)

    compiled_vf = ",".join(vf_list) if vf_list else None
    compiled_af = audio_post_filter or None
    print(f"--- [Graph] Compiler: Filter Chain -> {compiled_vf} ---")

    # 1. Attempt Modal Offloading (GPU)
    from ...services.modal_service import modal_service
    from ...services.workflow_engine import publish_progress
    
    if modal_service.enabled:
        publish_progress(job_id, "processing", "Offloading to GPU Cluster (Modal)...", 85, user_id=user_id)
        modal_output = await modal_service.render_video(
            job_id=job_id,
            source_path=source_path,
            cuts=cuts,
            fps=24,
            crf=18 if tier == "pro" else 23,
            vf_filters=compiled_vf,
            af_filters=compiled_af
        )
        if modal_output:
            print(f"--- [Graph] Modal Rendering Success: {modal_output} ---")
            return {
                "output_path": modal_output,
                "visual_effects": []
            }
        print("--- [Graph] Modal Rendering Failed, falling back to local CPU ---")

    # On constrained production hosts, local Pro rendering is too memory-heavy.
    if tier == "pro" and settings.environment == "production":
        return {
            "errors": [
                "Pro render requires Modal GPU offload in production. "
                "Local CPU fallback is disabled to avoid OOM on 512MB instances."
            ]
        }

    # 2. Local Parallel Rendering
    async with limits.render_semaphore:
        print("--- [Graph] Compiler Rendering (Local Parallel) ---")
        publish_progress(job_id, "processing", "Rendering scenes in parallel (Pro)...", 85, user_id=user_id)
        
        output_path = f"job-{job_id}-pro.mp4"
        abs_output = Path(os.getcwd()) / "storage" / "outputs" / output_path
        abs_output.parent.mkdir(parents=True, exist_ok=True)
        
        from ...services.rendering_orchestrator import rendering_orchestrator
        
        try:
            success = await rendering_orchestrator.render_parallel(
                job_id=job_id,
                source_path=source_path,
                cuts=cuts,
                output_path=str(abs_output),
                vf_filters=compiled_vf,
                af_filters=compiled_af,
                crf=18 if tier == "pro" else 23,
                preset="medium",
                transition_style=state.get("director_plan", {}).get("transition_style", "dissolve"),
                transition_duration=float(state.get("director_plan", {}).get("transition_duration", 0.25)),
                user_id=user_id
            )
            
            if success:
                return {
                    "output_path": f"storage/outputs/{output_path}",
                    "visual_effects": [] 
                }
            else:
                raise Exception("Parallel rendering failed.")
                
        except Exception as e:
            print(f"Compiler Error: {e}")
            # Fallback to copy if all else fails (safety)
            if os.path.exists(source_path):
                import shutil
                shutil.copy(source_path, abs_output)
                return {
                    "output_path": f"storage/outputs/{output_path}",
                    "errors": [f"Rendering crashed: {str(e)}. Fallback to raw copy."]
                }
            return {"errors": [str(e)]}
    media_duration = (
        state.get("media_intelligence", {})
        .get("visual", {})
        .get("metadata", {})
        .get("duration", 30.0)
    )
    pacing = state.get("user_request", {}).get("pacing", "medium")
    cuts = ensure_editing_cuts(cuts or [], duration=float(media_duration or 30.0), pacing=pacing)
