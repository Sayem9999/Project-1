from pydub import AudioSegment, effects
import os

# Set FFmpeg path for pydub
FFMPEG_BINARY = "./tools/ffmpeg-8.0.1-essentials_build/bin/ffmpeg.exe"
if os.path.exists(FFMPEG_BINARY):
    AudioSegment.converter = os.path.abspath(FFMPEG_BINARY)
    os.environ["PATH"] += os.pathsep + os.path.dirname(os.path.abspath(FFMPEG_BINARY))

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
