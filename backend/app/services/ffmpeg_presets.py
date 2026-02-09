"""
FFmpeg Presets - Content-category specific encoding presets.
"""
import structlog
from typing import Dict, Any, Literal
from dataclasses import dataclass

logger = structlog.get_logger()

ContentCategory = Literal["talking_head", "gameplay", "cinematic", "social", "tutorial"]


@dataclass
class FFmpegPreset:
    """FFmpeg encoding preset for a content category."""
    name: str
    category: ContentCategory
    
    # Video settings
    video_codec: str = "libx264"
    video_preset: str = "medium"
    crf: int = 23
    video_filter: str = ""
    
    # Audio settings
    audio_codec: str = "aac"
    audio_bitrate: str = "192k"
    audio_filter: str = ""
    
    # Output settings
    pixel_format: str = "yuv420p"
    movflags: str = "+faststart"
    
    def build_command_args(self) -> list:
        """Build FFmpeg command arguments."""
        args = [
            "-c:v", self.video_codec,
            "-preset", self.video_preset,
            "-crf", str(self.crf),
            "-c:a", self.audio_codec,
            "-b:a", self.audio_bitrate,
            "-pix_fmt", self.pixel_format,
            "-movflags", self.movflags
        ]
        
        if self.video_filter:
            args.extend(["-vf", self.video_filter])
        if self.audio_filter:
            args.extend(["-af", self.audio_filter])
        
        return args


# Content-category specific presets
PRESETS: Dict[ContentCategory, FFmpegPreset] = {
    "talking_head": FFmpegPreset(
        name="Talking Head / Podcast",
        category="talking_head",
        video_preset="slow",
        crf=20,  # Higher quality for faces
        video_filter="unsharp=5:5:0.5:5:5:0",  # Subtle sharpening
        audio_filter="highpass=f=80,lowpass=f=12000,loudnorm=I=-16:TP=-1.5:LRA=11",
    ),
    "gameplay": FFmpegPreset(
        name="Gameplay / Screen Recording",
        category="gameplay",
        video_preset="fast",  # Faster encoding for high motion
        crf=18,  # Lower CRF for detail preservation
        video_filter="",  # No filter - preserve original
        audio_filter="loudnorm=I=-14:TP=-1:LRA=11",
    ),
    "cinematic": FFmpegPreset(
        name="Cinematic / Film",
        category="cinematic",
        video_preset="slow",
        crf=18,  # High quality
        video_filter="colorbalance=rs=.1:gs=0:bs=.1",  # Subtle color grade
        audio_filter="loudnorm=I=-14:TP=-1:LRA=15",  # Wide dynamic range
    ),
    "social": FFmpegPreset(
        name="Social Media (TikTok/Reels)",
        category="social",
        video_preset="medium",
        crf=23,
        video_filter="eq=saturation=1.1:contrast=1.05",  # Slightly punchy
        audio_filter="loudnorm=I=-14:TP=-1:LRA=7,acompressor",  # Compressed audio
    ),
    "tutorial": FFmpegPreset(
        name="Tutorial / Educational",
        category="tutorial",
        video_preset="medium",
        crf=22,
        video_filter="unsharp=3:3:0.3:3:3:0",  # Light sharpening for text
        audio_filter="highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11",
    ),
}


class FFmpegPresetService:
    """Service for managing FFmpeg encoding presets."""
    
    @staticmethod
    def get_preset(category: ContentCategory) -> FFmpegPreset:
        """Get preset for content category."""
        return PRESETS.get(category, PRESETS["social"])
    
    @staticmethod
    def detect_category(
        has_face: bool = False,
        has_screen: bool = False,
        is_short: bool = False,
        high_motion: bool = False
    ) -> ContentCategory:
        """Auto-detect content category from video analysis."""
        if has_screen and high_motion:
            return "gameplay"
        if has_face and not high_motion:
            return "talking_head"
        if is_short:
            return "social"
        return "cinematic"
    
    @staticmethod
    def get_all_presets() -> Dict[ContentCategory, FFmpegPreset]:
        """Get all available presets."""
        return PRESETS.copy()
    
    @staticmethod
    def build_full_command(
        input_path: str,
        output_path: str,
        category: ContentCategory,
        extra_vf: str = "",
        extra_af: str = ""
    ) -> list:
        """Build complete FFmpeg command."""
        preset = FFmpegPresetService.get_preset(category)
        
        cmd = ["ffmpeg", "-i", input_path, "-y"]
        
        # Add preset args
        cmd.extend(preset.build_command_args())
        
        # Add extra filters if provided
        if extra_vf:
            cmd.extend(["-filter_complex", extra_vf])
        if extra_af:
            # Combine with existing audio filter
            combined_af = f"{preset.audio_filter},{extra_af}" if preset.audio_filter else extra_af
            # Find and replace -af
            for i, arg in enumerate(cmd):
                if arg == "-af":
                    cmd[i + 1] = combined_af
                    break
        
        cmd.append(output_path)
        return cmd


# Convenience function
def get_ffmpeg_preset(category: ContentCategory) -> FFmpegPreset:
    """Get FFmpeg preset for content category."""
    return FFmpegPresetService.get_preset(category)
