"""
Media Analysis Service - Scene detection, ffprobe metadata, loudness analysis.
Pre-processes video before agent planning for better decisions.
"""
import subprocess
import json
import structlog
import asyncio
import gc
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path
from .concurrency import limits

logger = structlog.get_logger()

# SCENEDETECT_AVAILABLE is now always False as we move to FFmpeg-native
SCENEDETECT_AVAILABLE = False
import re


@dataclass
class SceneInfo:
    """Information about a detected scene."""
    start_time: float
    end_time: float
    duration: float
    scene_number: int


@dataclass
class VideoMetadata:
    """Normalized video metadata from ffprobe."""
    duration: float
    width: int
    height: int
    fps: float
    codec: str
    bitrate: Optional[int]
    has_audio: bool
    audio_codec: Optional[str]
    sample_rate: Optional[int]
    channels: Optional[int]


@dataclass
class LoudnessInfo:
    """Audio loudness analysis results."""
    integrated_lufs: float  # Overall loudness
    true_peak_dbfs: float   # Maximum true peak
    lra: float              # Loudness range
    needs_normalization: bool
    target_lufs: float = -14.0  # Default YouTube/streaming target


@dataclass
class MediaAnalysis:
    """Complete media analysis results."""
    metadata: Optional[VideoMetadata]
    scenes: List[SceneInfo]
    loudness: Optional[LoudnessInfo]
    avg_shot_length: Optional[float]
    black_frame_pct: Optional[float]


# Analysis lock is handled via limits.analysis_semaphore


class MediaAnalyzer:
    """
    Comprehensive media analysis for intelligent editing decisions.
    """
    
    def __init__(self, ffmpeg_path: str = "ffmpeg", ffprobe_path: str = "ffprobe"):
        self.ffmpeg = self._resolve_path(ffmpeg_path)
        self.ffprobe = self._resolve_path(ffprobe_path)
        logger.info("media_analyzer_init", ffmpeg=self.ffmpeg, ffprobe=self.ffprobe)
    
    def _resolve_path(self, cmd: str) -> str:
        """Resolve command path, checking project tools as fallback."""
        import shutil
        if shutil.which(cmd):
            return cmd
        
        # Look in tools directory relative to project root
        project_root = Path(__file__).parent.parent.parent.parent.absolute()
        local_bin = project_root / "tools" / "ffmpeg-8.0.1-essentials_build" / "bin"
        ext = ".exe" if os.name == 'nt' else ""
        local_cmd = local_bin / f"{cmd}{ext}"
        
        if local_cmd.exists():
            return str(local_cmd)
        return cmd
    
    async def analyze(self, video_path: str) -> MediaAnalysis:
        """Run complete analysis on video file."""
        logger.info("media_analysis_start", path=video_path)
        
        # Metadata is lightweight
        metadata = await self.get_metadata(video_path)
        
        # Scenes is the most memory intensive part
        async with limits.analysis_semaphore:
            scenes = await self.detect_scenes(video_path)
            gc.collect() # Force cleanup after heavy decoding
        
        # Calculate average shot length
        avg_shot_length = None
        if scenes and len(scenes) > 1:
            avg_shot_length = sum(s.duration for s in scenes) / len(scenes)
        
        analysis = MediaAnalysis(
            metadata=metadata,
            scenes=scenes,
            loudness=None, # Defer to AudioIntelligence
            avg_shot_length=avg_shot_length,
            black_frame_pct=None
        )
        
        logger.info(
            "media_analysis_complete",
            scenes=len(scenes),
            duration=metadata.duration if metadata else None,
            avg_shot_length=avg_shot_length
        )
        
        return analysis
    
    async def get_metadata(self, video_path: str) -> Optional[VideoMetadata]:
        """Extract video metadata using ffprobe."""
        cmd = [
            self.ffprobe,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]
        
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=180)
            
            if proc.returncode != 0:
                logger.error("ffprobe_failed", error=stderr.decode())
                return None
            
            data = json.loads(stdout.decode())
            
            # Find video stream
            video_stream = None
            audio_stream = None
            for stream in data.get("streams", []):
                if stream["codec_type"] == "video" and not video_stream:
                    video_stream = stream
                elif stream["codec_type"] == "audio" and not audio_stream:
                    audio_stream = stream
            
            if not video_stream:
                logger.error("no_video_stream_found")
                return None
            
            format_info = data.get("format", {})
            
            # Parse FPS
            fps_str = video_stream.get("r_frame_rate", "30/1")
            fps_parts = fps_str.split("/")
            fps = float(fps_parts[0]) / float(fps_parts[1]) if len(fps_parts) == 2 else 30.0
            
            return VideoMetadata(
                duration=float(format_info.get("duration", 0)),
                width=int(video_stream.get("width", 0)),
                height=int(video_stream.get("height", 0)),
                fps=fps,
                codec=video_stream.get("codec_name", "unknown"),
                bitrate=int(format_info.get("bit_rate", 0)) if format_info.get("bit_rate") else None,
                has_audio=audio_stream is not None,
                audio_codec=audio_stream.get("codec_name") if audio_stream else None,
                sample_rate=int(audio_stream.get("sample_rate", 0)) if audio_stream else None,
                channels=int(audio_stream.get("channels", 0)) if audio_stream else None
            )
            
        except asyncio.TimeoutError:
            logger.error("ffprobe_timeout")
            return None
        except Exception as e:
            logger.error("metadata_extraction_failed", error=str(e))
            return None
    
    async def detect_scenes(self, video_path: str, threshold: float = 0.4) -> List[SceneInfo]:
        """Detect scene changes using native FFmpeg filters (highly memory efficient)."""
        cmd = [
            self.ffmpeg,
            "-hide_banner",
            "-i", video_path,
            "-vf", f"select='gt(scene,{threshold})',showinfo",
            "-f", "null",
            "-"
        ]
        
        try:
            logger.info("scene_detection_native_start", path=video_path, threshold=threshold)
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=600)
            
            # Showinfo outputs to stderr
            output = stderr.decode()
            
            # Parse pts_time from lines like:
            # [Parsed_showinfo_1 @ 0x...] n:   0 pts:      0 pts_time:2.004 ...
            timestamps = [0.0]  # Always start with 0
            for line in output.splitlines():
                if "pts_time:" in line:
                    match = re.search(r"pts_time:([\d\.]+)", line)
                    if match:
                        timestamps.append(float(match.group(1)))
            
            # Get video duration from metadata to close the last scene
            metadata = await self.get_metadata(video_path)
            if metadata and metadata.duration > timestamps[-1]:
                timestamps.append(metadata.duration)
            
            # Sort and remove near-duplicates
            timestamps = sorted(list(set(timestamps)))
            
            scenes = []
            for i in range(len(timestamps) - 1):
                start_time = timestamps[i]
                end_time = timestamps[i+1]
                duration = end_time - start_time
                
                # Filter out extremely short glitches (< 0.5s)
                if duration > 0.5:
                    scenes.append(SceneInfo(
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                        scene_number=len(scenes) + 1
                    ))
            
            logger.info("scene_detection_native_complete", scene_count=len(scenes))
            return scenes
            
        except asyncio.TimeoutError:
            logger.error("scene_detection_timeout", timeout=600)
            return []
        except Exception as e:
            logger.error("scene_detection_failed", error=str(e), type=type(e).__name__)
            return []
    
    def to_agent_context(self, analysis: MediaAnalysis) -> str:
        """Format analysis results for agent context injection."""
        parts = ["**Video Analysis:**"]
        
        if analysis.metadata:
            m = analysis.metadata
            parts.append(f"- Duration: {m.duration:.1f}s, Resolution: {m.width}x{m.height}, FPS: {m.fps:.1f}")
            parts.append(f"- Codec: {m.codec}, Audio: {m.audio_codec or 'None'}")
        
        if analysis.scenes:
            parts.append(f"- Scenes detected: {len(analysis.scenes)}")
            if analysis.avg_shot_length:
                parts.append(f"- Average shot length: {analysis.avg_shot_length:.1f}s")
        
        if analysis.loudness:
            l = analysis.loudness
            parts.append(f"- Loudness: {l.integrated_lufs:.1f} LUFS, Peak: {l.true_peak_dbfs:.1f} dBFS")
            if l.needs_normalization:
                parts.append(f"- ⚠ Audio needs normalization to {l.target_lufs} LUFS")
        
        return "\n".join(parts)


# Global analyzer instance
media_analyzer = MediaAnalyzer()
