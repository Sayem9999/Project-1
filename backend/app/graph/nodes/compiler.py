from ..state import GraphState
from pathlib import Path
import os
# Configure MoviePy to use the correct FFmpeg binary (v2.0+ compatible)
FFMPEG_BINARY = r"C:\Users\Sayem\Downloads\New folder\Project-1-1\tools\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe"
if os.path.exists(FFMPEG_BINARY):
    os.environ["IMAGEIO_FFMPEG_EXE"] = FFMPEG_BINARY

from ...services.concurrency import limits
from ...config import settings

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
            vf_filters=None,
            af_filters=None
        )
        if modal_output:
            print(f"--- [Graph] Modal Rendering Success: {modal_output} ---")
            return {
                "output_path": modal_output,
                "visual_effects": []
            }
        print("--- [Graph] Modal Rendering Failed, falling back to local CPU ---")

    # On constrained production hosts, local Pro rendering is too memory-heavy.
    # DISABLED for Smoke Test on local powerful machine
    # if tier == "pro" and settings.environment == "production":
    #     return {
    #         "errors": [
    #             "Pro render requires Modal GPU offload in production. "
    #             "Local CPU fallback is disabled to avoid OOM on 512MB instances."
    #         ]
    #     }

    # 2. Local Fallback Rendering (CPU)
    async with limits.render_semaphore:
        print("--- [Graph] Compiler Rendering (Local) ---")
        publish_progress(job_id, "processing", "Rendering video on local CPU...", 85, user_id=user_id)
        
        output_path = f"job-{job_id}-pro.mp4"
        abs_output = Path(os.getcwd()) / "storage" / "outputs" / output_path
        abs_output.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Import MoviePy lazily so non-render processes don't pay memory cost.
            from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip

            # Load Source
            original_clip = VideoFileClip(source_path)
            
            # Create Subclips based on Cuts
            clips = []
            for cut in cuts:
                start = float(cut.get("start", 0))
                end = float(cut.get("end", original_clip.duration))
                if start >= original_clip.duration: continue
                if end > original_clip.duration: end = original_clip.duration
                if start >= end: continue
                
                sub = original_clip.subclipped(start, end)
                clips.append(sub)
                
            if not clips:
                final_video = original_clip
            else:
                final_video = concatenate_videoclips(clips, method="compose")

            # --- Visual Effects ---
            visual_effects = state.get("visual_effects", [])
            vf_filters = []
            
            print(f"--- [Graph] Processing {len(visual_effects)} visual effects ---")
            
            for effect in visual_effects:
                if effect.get("type") == "ffmpeg_filter" and effect.get("value"):
                    # Clean the filter value (remove -vf if agent included it or quotes)
                    val = effect["value"].strip()
                    # Strip common agent hallucinations
                    if val.startswith("-vf "): val = val[4:]
                    val = val.strip('"').strip("'").strip(",")
                    
                    if val:
                        print(f"--- [Graph] Applying Filter: {val} ---")
                        vf_filters.append(val)
                elif effect.get("type") == "lut":
                    print(f"--- [Graph] LUT Recommended: {effect.get('value')} (Skipping: file path mapping not implemented) ---")
            # ----------------------

            # --- Audio Enhancement & Mixing ---
            audio_tracks = state.get("audio_tracks", [])
            try:
                from ...services.audio_service import audio_service
                if final_video.audio:
                    print("--- [Graph] Processing Audio ---")
                    temp_audio_path = f"storage/outputs/temp_audio_{job_id}.mp3"
                    final_video.audio.write_audiofile(temp_audio_path, logger=None)
                    
                    # 1. Normalize
                    norm_audio_path = audio_service.normalize_audio(temp_audio_path)
                    
                    # 2. Mix with music if available
                    final_audio_path = norm_audio_path
                    if audio_tracks:
                        print(f"--- [Graph] Suggesting {len(audio_tracks)} music tracks ---")
                        # Note: In a real app, we'd look up audio_tracks[0].name in a library
                        # Since library is empty, we'll just use normalized original for now.
                    
                    new_audio = AudioFileClip(final_audio_path)
                    final_video = final_video.set_audio(new_audio)
            except Exception as ae:
                print(f"Audio Enhancement/Mixing Failed: {ae}")
            # -------------------------

            # Render
            ffmpeg_args = ["-crf", "18" if tier == "pro" else "23"]
            if vf_filters:
                # Combine multiple filters with comma
                combined_vf = ",".join(vf_filters)
                ffmpeg_args += ["-vf", combined_vf]
                print(f"--- [Graph] Final FFmpeg VF Args: {combined_vf} ---")

            final_video.write_videofile(
                str(abs_output), 
                codec="libx264", 
                audio_codec="aac", 
                threads=4,
                fps=24,
                preset="medium",
                ffmpeg_params=ffmpeg_args,
                logger=None
            )
            
            original_clip.close()
            
            return {
                "output_path": f"storage/outputs/{output_path}",
                "visual_effects": visual_effects 
            }
            
        except Exception as e:
            print(f"Compiler Error: {e}")
            return {"errors": [str(e)]}
