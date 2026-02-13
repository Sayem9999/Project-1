import os
import sys

# Standardize tool resolution
def _resolve_tool_path(tool_name: str):
    ext = ".exe" if os.name == "nt" else ""
    paths = [
        f"tools/ffmpeg-8.0.1-essentials_build/bin/{tool_name}{ext}",
        f"../tools/ffmpeg-8.0.1-essentials_build/bin/{tool_name}{ext}",
        f"../../tools/ffmpeg-8.0.1-essentials_build/bin/{tool_name}{ext}"
    ]
    for p in paths:
        if os.path.exists(p):
            return os.path.abspath(p)
    return tool_name

FFMPEG_PATH = _resolve_tool_path("ffmpeg")
FFPROBE_PATH = _resolve_tool_path("ffprobe")

# Inject into environment before importing pydub
if FFMPEG_PATH != "ffmpeg":
    os.environ["PATH"] = os.path.dirname(FFMPEG_PATH) + os.pathsep + os.environ.get("PATH", "")

from pydub import AudioSegment, effects
if FFMPEG_PATH != "ffmpeg":
    AudioSegment.converter = FFMPEG_PATH
    AudioSegment.ffprobe = FFPROBE_PATH

class AudioService:
    @staticmethod
    def normalize_audio(file_path: str, target_dBFS: float = -20.0) -> str:
        """
        Normalize audio to a specific dBFS.
        Returns path to processed file.
        """
        try:
            sound = AudioSegment.from_file(file_path)
            change_in_dBFS = target_dBFS - sound.dBFS
            normalized_sound = sound.apply_gain(change_in_dBFS)
            
            output_path = f"{file_path}_norm.mp3"
            normalized_sound.export(output_path, format="mp3")
            return output_path
        except Exception as e:
            print(f"[AudioService] Normalization Error: {e}")
            return file_path

    @staticmethod
    def mix_tracks(base_track: str, overlay_track: str, overlay_gain: float = -10.0) -> str:
        """
        Mix an overlay track (music) onto a base track (voice/video audio).
        """
        try:
            sound1 = AudioSegment.from_file(base_track)
            sound2 = AudioSegment.from_file(overlay_track).apply_gain(overlay_gain)
            
            # Loop sound2 if shorter? Or just overlay.
            # For now, simple overlay
            output = sound1.overlay(sound2)
            
            output_path = "storage/outputs/mixed_audio.mp3"
            output.export(output_path, format="mp3")
            return output_path
        except Exception as e:
            print(f"[AudioService] Mixing Error: {e}")
            return base_track

audio_service = AudioService()
