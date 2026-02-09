"""
Audio Profiles Service - Platform-specific loudness templates and processing chains.
"""
import structlog
from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass

logger = structlog.get_logger()

PlatformType = Literal["youtube", "tiktok", "instagram", "podcast", "broadcast"]


@dataclass
class AudioProfile:
    """Platform-specific audio processing profile."""
    name: str
    target_lufs: float
    true_peak_limit: float  # dBTP
    sample_rate: int
    
    # Processing chain flags
    apply_compression: bool = True
    apply_limiter: bool = True
    apply_denoise: bool = False
    apply_dereverb: bool = False
    
    # FFmpeg filter chain
    ffmpeg_filter: str = ""


# Platform-specific audio profiles
AUDIO_PROFILES: Dict[PlatformType, AudioProfile] = {
    "youtube": AudioProfile(
        name="YouTube",
        target_lufs=-14.0,
        true_peak_limit=-1.0,
        sample_rate=48000,
        ffmpeg_filter="loudnorm=I=-14:TP=-1:LRA=11,acompressor=threshold=-20dB:ratio=4:attack=5:release=50"
    ),
    "tiktok": AudioProfile(
        name="TikTok",
        target_lufs=-14.0,
        true_peak_limit=-1.0,
        sample_rate=44100,
        ffmpeg_filter="loudnorm=I=-14:TP=-1:LRA=7,acompressor=threshold=-18dB:ratio=6:attack=3:release=30"
    ),
    "instagram": AudioProfile(
        name="Instagram Reels",
        target_lufs=-14.0,
        true_peak_limit=-1.0,
        sample_rate=44100,
        ffmpeg_filter="loudnorm=I=-14:TP=-1:LRA=8"
    ),
    "podcast": AudioProfile(
        name="Podcast",
        target_lufs=-16.0,
        true_peak_limit=-1.5,
        sample_rate=48000,
        apply_denoise=True,
        ffmpeg_filter="loudnorm=I=-16:TP=-1.5:LRA=9,highpass=f=80,lowpass=f=12000,acompressor"
    ),
    "broadcast": AudioProfile(
        name="Broadcast",
        target_lufs=-24.0,  # EBU R128
        true_peak_limit=-2.0,
        sample_rate=48000,
        ffmpeg_filter="loudnorm=I=-24:TP=-2:LRA=7"
    )
}


class AudioProfileService:
    """Service for applying platform-specific audio processing."""
    
    @staticmethod
    def get_profile(platform: PlatformType) -> AudioProfile:
        """Get audio profile for platform."""
        return AUDIO_PROFILES.get(platform, AUDIO_PROFILES["youtube"])
    
    @staticmethod
    def get_ffmpeg_filter(
        platform: PlatformType,
        denoise: bool = False,
        dereverb: bool = False
    ) -> str:
        """Build FFmpeg audio filter chain for platform."""
        profile = AudioProfileService.get_profile(platform)
        filters = []
        
        # Optional pre-processing
        if denoise:
            # Simple highpass to reduce low-frequency noise
            filters.append("highpass=f=100")
        
        if dereverb:
            # Simple gate to reduce reverb tails
            filters.append("agate=threshold=-30dB:ratio=2:attack=25:release=100")
        
        # Core loudness normalization
        filters.append(profile.ffmpeg_filter)
        
        return ",".join(filters)
    
    @staticmethod
    def get_speech_enhancement_filter() -> str:
        """Get filter chain optimized for speech clarity."""
        return (
            "highpass=f=80,"           # Remove low rumble
            "lowpass=f=12000,"         # Remove high noise
            "afftdn=nf=-25,"           # FFT denoise
            "acompressor=threshold=-20dB:ratio=3:attack=10:release=100,"
            "loudnorm=I=-16:TP=-1.5:LRA=11"
        )
    
    @staticmethod
    def get_music_enhancement_filter() -> str:
        """Get filter chain for music/background mixing."""
        return (
            "loudnorm=I=-20:TP=-1:LRA=15,"  # Softer for background
            "equalizer=f=3000:width_type=o:width=2:g=2"  # Presence boost
        )
    
    @staticmethod
    def build_ducking_filter(
        speech_volume: float = 1.0,
        music_volume: float = 0.3
    ) -> str:
        """Build audio ducking filter for speech over music."""
        return (
            f"[0:a]volume={speech_volume}[speech];"
            f"[1:a]volume={music_volume}[music];"
            "[speech][music]amix=inputs=2:duration=first"
        )


# Convenience function
def get_audio_profile(platform: PlatformType) -> AudioProfile:
    """Get audio profile for platform."""
    return AudioProfileService.get_profile(platform)
