from ..state import GraphState
from moviepy import VideoFileClip, concatenate_videoclips, CompositeAudioClip, AudioFileClip, vfx
from pathlib import Path
import os
# Configure MoviePy to use the correct FFmpeg binary (v2.0+ compatible)
FFMPEG_BINARY = "./tools/ffmpeg-8.0.1-essentials_build/bin/ffmpeg.exe"
if os.path.exists(FFMPEG_BINARY):
    os.environ["IMAGEIO_FFMPEG_EXE"] = FFMPEG_BINARY

from ...services.concurrency import limits

async def compiler_node(state: GraphState) -> GraphState:
    """
    Compiler Node: Assembles the final video.
    Supports local rendering (CPU) and Modal offloading (GPU).
    """
    job_id = state.get("job_id")
    source_path = state.get("source_path")
    cuts = state.get("cuts", [])
    tier = state.get("tier", "standard")
    
    # 1. Attempt Modal Offloading (GPU)
    from ...services.modal_service import modal_service
    from ...services.workflow_engine import publish_progress
    
    if modal_service.enabled:
        publish_progress(job_id, "processing", "Offloading to GPU Cluster (Modal)...", 85)
        modal_output = await modal_service.render_video(
            job_id=job_id,
            source_path=source_path,
            cuts=cuts,
            fps=24 if tier == "pro" else 24, # Standardize
            crf=18 if tier == "pro" else 23
        )
        if modal_output:
            print(f"--- [Graph] Modal Rendering Success: {modal_output} ---")
            return {
                "output_path": modal_output,
                "visual_effects": []
            }
        print("--- [Graph] Modal Rendering Failed, falling back to local CPU ---")

    # 2. Local Fallback Rendering (CPU)
    async with limits.render_semaphore:
        print("--- [Graph] Compiler Rendering (Local) ---")
        publish_progress(job_id, "processing", "Rendering video on local CPU...", 85)
        
        output_path = f"job-{job_id}-pro.mp4"
        abs_output = Path(os.getcwd()) / "storage" / "outputs" / output_path
        abs_output.parent.mkdir(parents=True, exist_ok=True)
        
        try:
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

            # --- Audio Enhancement ---
            try:
                from ...services.audio_service import audio_service
                if final_video.audio:
                    temp_audio_path = f"storage/outputs/temp_audio_{job_id}.mp3"
                    final_video.audio.write_audiofile(temp_audio_path, logger=None)
                    norm_audio_path = audio_service.normalize_audio(temp_audio_path)
                    new_audio = AudioFileClip(norm_audio_path)
                    final_video = final_video.set_audio(new_audio)
            except Exception as ae:
                print(f"Audio Enhancement Failed: {ae}")
            # -------------------------

            # Render
            final_video.write_videofile(
                str(abs_output), 
                codec="libx264", 
                audio_codec="aac", 
                threads=4,
                fps=24,
                preset="medium",
                ffmpeg_params=["-crf", "18" if tier == "pro" else "23"],
                logger=None
            )
            
            original_clip.close()
            
            return {
                "output_path": f"storage/outputs/{output_path}",
                "visual_effects": [] 
            }
            
        except Exception as e:
            print(f"Compiler Error: {e}")
            return {"errors": [str(e)]}
