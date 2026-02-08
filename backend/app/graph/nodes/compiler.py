from ..state import GraphState
from moviepy import VideoFileClip, concatenate_videoclips, CompositeAudioClip, AudioFileClip, vfx
import os
from pathlib import Path

async def compiler_node(state: GraphState) -> GraphState:
    """
    Compiler Node: Assembles the final video using MoviePy.
    """
    print("--- [Graph] Compiler Rendering ---")
    
    source_path = state.get("source_path")
    cuts = state.get("cuts", [])
    output_path = f"job-{state.get('job_id')}-pro.mp4"
    abs_output = Path(os.getcwd()) / "storage" / "outputs" / output_path
    abs_output.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load Source
        # Note: MoviePy v2 might handle context managers differently, but this is standard
        original_clip = VideoFileClip(source_path)
        
        # Create Subclips based on Cuts
        clips = []
        for cut in cuts:
            start = float(cut.get("start", 0))
            end = float(cut.get("end", 5)) # Default 5s if missing
            # Safety check
            if start >= original_clip.duration: continue
            if end > original_clip.duration: end = original_clip.duration
            if start >= end: continue
            
            sub = original_clip.subclipped(start, end)
            
            # Apply Visual Effects (Simple placeholder for now)
            # In a real app, parse "visual_effects" list and apply filters
            # e.g. sub = sub.fx(vfx.colorx, 1.2)
            
            clips.append(sub)
            
        if not clips:
            print("No valid clips found, using original.")
            final_video = original_clip
        else:
            final_video = concatenate_videoclips(clips, method="compose")

        # --- Audio Enhancement (Pydub) ---
        try:
            from ...services.audio_service import audio_service
            
            # 1. Export temp audio
            temp_audio_path = f"storage/outputs/temp_audio_{state.get('job_id')}.mp3"
            final_video.audio.write_audiofile(temp_audio_path, logger=None)
            
            # 2. Normalize
            norm_audio_path = audio_service.normalize_audio(temp_audio_path)
            
            # 3. Re-attach
            new_audio = AudioFileClip(norm_audio_path)
            final_video = final_video.set_audio(new_audio)
            print("Audio normalized successfully.")
            
        except Exception as ae:
            print(f"Audio Enhancement Failed: {ae}")
            # Continue with original audio
        # ---------------------------------

        # Render
        # Threads=4 for speed
        final_video.write_videofile(
            str(abs_output), 
            codec="libx264", 
            audio_codec="aac", 
            threads=4,
            fps=24,
            logger=None # Silence standard logger to avoid spam
        )
        
        original_clip.close()
        
        return {
            "output_path": f"storage/outputs/{output_path}",
            "visual_effects": [] # Cleared
        }
        
    except Exception as e:
        print(f"Compiler Error: {e}")
        import traceback
        traceback.print_exc()
        return {"errors": [str(e)]}
