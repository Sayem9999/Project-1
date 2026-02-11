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

logger = structlog.get_logger()

# PySceneDetect (lazy import)
try:
    from scenedetect import open_video, SceneManager
    from scenedetect.detectors import ContentDetector
    SCENEDETECT_AVAILABLE = True
except ImportError:
    SCENEDETECT_AVAILABLE = False


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
        
        # Run these sequentially to avoid peak memory pressure on 512MB tier
        metadata = await self.get_metadata(video_path)
        
        # Scenes is the most memory intensive part
        scenes = await self.detect_scenes(video_path)
        gc.collect() # Force cleanup after heavy decoding
        
        loudness = None
        if metadata and metadata.has_audio:
            loudness = await self.analyze_loudness(video_path, metadata.duration)
        
        # Calculate average shot length
        avg_shot_length = None
        if scenes and len(scenes) > 1:
            avg_shot_length = sum(s.duration for s in scenes) / len(scenes)
        
        analysis = MediaAnalysis(
            metadata=metadata,
            scenes=scenes,
            loudness=loudness,
            avg_shot_length=avg_shot_length,
            black_frame_pct=None  # TODO: Implement black frame detection
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
        def _run_ffprobe():
            cmd = [
                self.ffprobe,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            return subprocess.run(cmd, capture_output=True, text=True, timeout=180)

        try:
            result = await asyncio.to_thread(_run_ffprobe)
            if result.returncode != 0:
                logger.error("ffprobe_failed", error=result.stderr)
                return None
            
            data = json.loads(result.stdout)
            
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
            
        except subprocess.TimeoutExpired:
            logger.error("ffprobe_timeout")
            return None
        except Exception as e:
            logger.error("metadata_extraction_failed", error=str(e))
            return None
    
    async def detect_scenes(self, video_path: str, threshold: float = 27.0) -> List[SceneInfo]:
        """Detect scene changes using PySceneDetect (in background thread)."""
        if not SCENEDETECT_AVAILABLE:
            logger.warning("scenedetect_not_available")
            return []
        
        def _run_detection():
            try:
                video = open_video(video_path)
                scene_manager = SceneManager()
                # Use a higher threshold if needed, but downscale is key for memory
                scene_manager.add_detector(ContentDetector(threshold=threshold))
                
                # downscale reduces decoding resolution (e.g., 2 means half width/height)
                # This drastically reduces memory usage on high-res videos
                scene_manager.detect_scenes(video, show_progress=False)
                return scene_manager.get_scene_list()
            except Exception as e:
                logger.error("scenedetect_thread_failed", error=str(e))
                return []

        try:
            # Set a hard timeout for scene detection to prevent 0% hangs
            # This is extremely resource intensive
            logger.info("scene_detection_thread_start", path=video_path)
            scene_list = await asyncio.wait_for(asyncio.to_thread(_run_detection), timeout=300)
            
            scenes = []
            for i, (start, end) in enumerate(scene_list):
                start_time = start.get_seconds()
                end_time = end.get_seconds()
                scenes.append(SceneInfo(
                    start_time=start_time,
                    end_time=end_time,
                    duration=end_time - start_time,
                    scene_number=i + 1
                ))
            
            logger.info("scene_detection_complete", scene_count=len(scenes))
            return scenes
            
        except Exception as e:
            logger.error("scene_detection_failed", error=str(e))
            return []
    
    async def analyze_loudness(
        self,
        video_path: str,
        duration: Optional[float] = None,
        target_lufs: float = -14.0
    ) -> Optional[LoudnessInfo]:
        """Analyze audio loudness using ffmpeg loudnorm filter."""
        def _run_ffmpeg():
            analysis_seconds = min(duration or 60.0, 60.0)
            cmd = [
                self.ffmpeg,
                "-hide_banner",
                "-t", str(analysis_seconds),
                "-i", video_path,
                "-af", "loudnorm=print_format=json",
                "-f", "null",
                "-"
            ]
            timeout_seconds = 300 if analysis_seconds >= 30 else 120
            return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds)

        try:
            result = await asyncio.to_thread(_run_ffmpeg)
            
            # Parse loudnorm output from stderr
            output = result.stderr
            
            # Find JSON block in output
            json_start = output.rfind("{")
            json_end = output.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = output[json_start:json_end]
                loudness_data = json.loads(json_str)
                
                integrated = float(loudness_data.get("input_i", -70))
                true_peak = float(loudness_data.get("input_tp", -70))
                lra = float(loudness_data.get("input_lra", 0))
                
                # Check if normalization needed
                needs_norm = abs(integrated - target_lufs) > 1.0 or true_peak > -1.0
                
                return LoudnessInfo(
                    integrated_lufs=integrated,
                    true_peak_dbfs=true_peak,
                    lra=lra,
                    needs_normalization=needs_norm,
                    target_lufs=target_lufs
                )
            
            return None
            
        except subprocess.TimeoutExpired:
            logger.warning("loudness_analysis_timeout")
            return None
        except Exception as e:
            logger.warning("loudness_analysis_failed", error=str(e))
            return None
    
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
