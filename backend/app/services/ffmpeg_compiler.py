"""
FFmpeg Compiler - Converts Timeline DSL to FFmpeg command graph.
"""
import structlog
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path

from .timeline_dsl import Timeline, Clip, Transition, Overlay, AudioTrack, TransitionType

logger = structlog.get_logger()


class FFmpegCompiler:
    """
    Compiles Timeline DSL to FFmpeg filter graphs and commands.
    """
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg = ffmpeg_path
    
    def compile(self, timeline: Timeline, output_path: str) -> List[str]:
        """
        Compile timeline to FFmpeg command.
        Returns the command as a list of arguments.
        """
        cmd = [self.ffmpeg, "-y"]  # -y to overwrite
        
        # Add inputs
        cmd.extend(self._build_inputs(timeline))
        
        # Build filter graph
        filter_complex = self._build_filter_complex(timeline)
        if filter_complex:
            cmd.extend(["-filter_complex", filter_complex])
        
        # Map outputs
        cmd.extend(self._build_output_mapping(timeline))
        
        # Hardware-accelerated output settings
        from .gpu_capabilities import gpu_detector
        encoding_args = gpu_detector.get_encoding_args()
        cmd.extend(encoding_args)
        
        # Audio and container settings
        cmd.extend([
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            output_path
        ])
        
        logger.info("ffmpeg_compiled", timeline_id=timeline.id, cmd_length=len(cmd))
        return cmd
    
    def _build_inputs(self, timeline: Timeline) -> List[str]:
        """Build input file arguments."""
        inputs = []
        seen_sources = set()
        
        # Add main source
        if timeline.source_file:
            inputs.extend(["-i", timeline.source_file])
            seen_sources.add(timeline.source_file)
        
        # Add any additional audio sources
        for audio in timeline.audio_tracks:
            if audio.source not in seen_sources:
                inputs.extend(["-i", audio.source])
                seen_sources.add(audio.source)
        
        return inputs
    
    def _build_filter_complex(self, timeline: Timeline) -> str:
        """Build the filter_complex string."""
        filters = []
        
        # Build video filter chain
        video_filters = self._build_video_filters(timeline)
        if video_filters:
            filters.append(video_filters)
        
        # Build audio filter chain
        audio_filters = self._build_audio_filters(timeline)
        if audio_filters:
            filters.append(audio_filters)
        
        # Build overlay filters
        overlay_filters = self._build_overlay_filters(timeline)
        if overlay_filters:
            filters.append(overlay_filters)
        
        return ";".join(filters) if filters else ""
    
    def _build_video_filters(self, timeline: Timeline) -> str:
        """Build video filter chain for clips and transitions."""
        if not timeline.clips:
            return ""
        
        filter_parts = []
        clip_labels = []
        
        for i, clip in enumerate(timeline.clips):
            label = f"v{i}"
            
            # Trim to source range
            trim = f"[0:v]trim={clip.source_range.start}:{clip.source_range.end}"
            trim += f",setpts=PTS-STARTPTS"
            
            # Apply speed adjustment
            if clip.speed != 1.0:
                trim += f",setpts={1/clip.speed}*PTS"
            
            # Apply clip-specific filters
            for flt in clip.filters:
                trim += f",{flt}"
            
            trim += f"[{label}]"
            filter_parts.append(trim)
            clip_labels.append(f"[{label}]")
        
        # Concatenate clips
        if len(clip_labels) > 1:
            concat_inputs = "".join(clip_labels)
            filter_parts.append(f"{concat_inputs}concat=n={len(clip_labels)}:v=1:a=0[vout]")
        else:
            # Single clip, just rename
            filter_parts.append(f"{clip_labels[0]}copy[vout]")
        
        # Apply color grade if specified
        if timeline.color_grade:
            grade_filter = self._get_color_grade_filter(timeline.color_grade)
            if grade_filter:
                filter_parts.append(f"[vout]{grade_filter}[vout]")
        
        return ";".join(filter_parts)
    
    def _build_audio_filters(self, timeline: Timeline) -> str:
        """Build audio filter chain."""
        filters = []
        
        # Basic audio extraction and normalization
        audio_chain = f"[0:a]loudnorm=I={timeline.loudness_target}:TP=-1:LRA=11[aout]"
        filters.append(audio_chain)
        
        return ";".join(filters)
    
    def _build_overlay_filters(self, timeline: Timeline) -> str:
        """Build subtitle/text overlay filters."""
        if not timeline.overlays:
            return ""
        
        filters = []
        
        for overlay in timeline.overlays:
            if overlay.type == "text":
                # Use drawtext filter
                text = overlay.content.replace("'", "\\'").replace(":", "\\:")
                style = overlay.style
                
                font = style.get("font", "Arial")
                size = style.get("size", 48)
                color = style.get("color", "white")
                
                drawtext = (
                    f"drawtext=text='{text}'"
                    f":fontfile=/Windows/Fonts/arial.ttf"
                    f":fontsize={size}"
                    f":fontcolor={color}"
                    f":x=(w-text_w)/2:y=h-th-50"
                    f":enable='between(t,{overlay.time_range.start},{overlay.time_range.end})'"
                )
                filters.append(f"[vout]{drawtext}[vout]")
        
        return ";".join(filters)
    
    def _build_output_mapping(self, timeline: Timeline) -> List[str]:
        """Build output stream mapping."""
        return ["-map", "[vout]", "-map", "[aout]"]
    
    def _get_color_grade_filter(self, palette: str) -> Optional[str]:
        """Convert color palette name to FFmpeg filter."""
        grades = {
            "teal_orange": "colorbalance=rs=-.1:gs=0:bs=.1:rm=0:gm=0:bm=0:rh=.1:gh=0:bh=-.1",
            "warm": "colortemperature=6500",
            "cool": "colortemperature=4500",
            "desaturated": "eq=saturation=0.7",
            "vibrant": "eq=saturation=1.3:contrast=1.1",
            "cinematic": "curves=preset=cross_process",
        }
        
        # Normalize palette name
        normalized = palette.lower().replace(" ", "_").replace("&", "_")
        
        for key, value in grades.items():
            if key in normalized:
                return value
        
        return None
    
    async def execute(self, timeline: Timeline, output_path: str) -> Dict[str, Any]:
        """
        Compile and execute FFmpeg command.
        Returns execution result.
        """
        cmd = self.compile(timeline, output_path)
        
        logger.info("ffmpeg_execute_start", timeline_id=timeline.id)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("ffmpeg_execute_success", timeline_id=timeline.id)
                return {
                    "success": True,
                    "output_path": output_path,
                    "cmd": " ".join(cmd)
                }
            else:
                logger.error(
                    "ffmpeg_execute_failed",
                    timeline_id=timeline.id,
                    stderr=result.stderr[:500]
                )
                return {
                    "success": False,
                    "error": result.stderr,
                    "cmd": " ".join(cmd)
                }
                
        except subprocess.TimeoutExpired:
            logger.error("ffmpeg_timeout", timeline_id=timeline.id)
            return {
                "success": False,
                "error": "FFmpeg execution timed out",
                "cmd": " ".join(cmd)
            }
        except Exception as e:
            logger.error("ffmpeg_exception", timeline_id=timeline.id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "cmd": " ".join(cmd)
            }


# Global compiler instance
ffmpeg_compiler = FFmpegCompiler()
