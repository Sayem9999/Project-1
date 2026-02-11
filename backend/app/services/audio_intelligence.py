"""
Audio Intelligence - Loudness profiling, silence trimming, speech ducking.
"""
import structlog
import subprocess
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class LoudnessSegment:
    """Loudness data for a segment of audio."""
    start: float
    end: float
    integrated_lufs: float
    peak_dbfs: float
    is_speech: bool = False
    is_music: bool = False
    is_silence: bool = False


@dataclass
class SilenceRegion:
    """A region of silence in the audio."""
    start: float
    end: float
    duration: float
    
    @property
    def is_trimmable(self) -> bool:
        """Silence longer than 0.5s is trimmable."""
        return self.duration > 0.5


@dataclass
class DuckingPolicy:
    """Audio ducking configuration."""
    duck_level: float = 0.3  # Volume multiplier when ducking
    attack_time: float = 0.1  # Seconds to fade down
    release_time: float = 0.3  # Seconds to fade up
    threshold_db: float = -30  # Speech detection threshold
    hold_time: float = 0.5  # Hold ducking after speech ends


@dataclass
class AudioAnalysis:
    """Complete audio analysis for a file."""
    duration: float
    overall_lufs: float
    overall_peak: float
    segments: List[LoudnessSegment] = field(default_factory=list)
    silence_regions: List[SilenceRegion] = field(default_factory=list)
    speech_regions: List[Tuple[float, float]] = field(default_factory=list)
    needs_normalization: bool = False


class AudioIntelligence:
    """
    Advanced audio analysis and processing.
    """
    
    def __init__(self, ffmpeg_path: str = "ffmpeg", ffprobe_path: str = "ffprobe"):
        self.ffmpeg = self._resolve_path(ffmpeg_path)
        self.ffprobe = self._resolve_path(ffprobe_path)
        self.segment_duration = 5.0  # Analyze in 5-second segments
        self.silence_threshold = -40  # dB
        self.speech_threshold = -30   # dB
        self.max_analysis_seconds = 60.0
        logger.info("audio_intelligence_init", ffmpeg=self.ffmpeg, ffprobe=self.ffprobe)

    def _resolve_path(self, cmd: str) -> str:
        """Resolve command path, checking project tools as fallback."""
        import shutil
        import os
        from pathlib import Path
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
    
    async def analyze(self, audio_path: str) -> AudioAnalysis:
        """Run complete audio analysis."""
        logger.info("audio_analysis_start", path=audio_path)
        
        # Get overall loudness
        overall = await self._analyze_overall_loudness(audio_path)
        if not overall:
            return AudioAnalysis(
                duration=0,
                overall_lufs=-70,
                overall_peak=-70
            )
        
        # Detect silence regions
        silence_regions = await self._detect_silence(audio_path)
        
        # Detect speech regions (simple VAD)
        speech_regions = await self._detect_speech_regions(audio_path)
        
        analysis = AudioAnalysis(
            duration=overall.get("duration", 0),
            overall_lufs=overall.get("integrated_lufs", -70),
            overall_peak=overall.get("true_peak", -70),
            silence_regions=silence_regions,
            speech_regions=speech_regions,
            needs_normalization=abs(overall.get("integrated_lufs", -14) - (-14)) > 1
        )
        
        logger.info(
            "audio_analysis_complete",
            duration=analysis.duration,
            lufs=analysis.overall_lufs,
            silence_count=len(silence_regions),
            speech_count=len(speech_regions)
        )
        
        return analysis
    
    async def _analyze_overall_loudness(self, audio_path: str) -> Optional[Dict[str, float]]:
        """Analyze overall loudness using loudnorm filter."""
        def _run_analysis():
            duration = self._probe_duration(audio_path)
            analysis_seconds = min(duration or self.max_analysis_seconds, self.max_analysis_seconds)
            cmd = [
                self.ffmpeg,
                "-hide_banner",
                "-t", str(analysis_seconds),
                "-i", audio_path,
                "-af", "loudnorm=print_format=json",
                "-f", "null",
                "-"
            ]
            
            timeout_seconds = 120 if analysis_seconds >= 30 else 60
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds)
            return result, duration, analysis_seconds

        try:
            result, duration, analysis_seconds = await asyncio.to_thread(_run_analysis)
            
            # Parse loudnorm output from stderr
            output = result.stderr
            json_start = output.rfind("{")
            json_end = output.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                loudness_data = json.loads(output[json_start:json_end])
                return {
                    "integrated_lufs": float(loudness_data.get("input_i", -70)),
                    "true_peak": float(loudness_data.get("input_tp", -70)),
                    "lra": float(loudness_data.get("input_lra", 0)),
                    "duration": duration or analysis_seconds
                }
            return None
            
        except subprocess.TimeoutExpired:
            logger.warning("loudness_analysis_timeout")
            return None
        except Exception as e:
            logger.warning("loudness_analysis_failed", error=str(e))
            return None

    def _probe_duration(self, audio_path: str) -> Optional[float]:
        """Return media duration in seconds using ffprobe."""
        try:
            cmd = [
                self.ffprobe,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=nk=1:nw=1",
                audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return None
            return float(result.stdout.strip() or 0)
        except Exception:
            return None
    
    async def _detect_silence(self, audio_path: str) -> List[SilenceRegion]:
        """Detect silent regions using silencedetect filter."""
        def _run_silence():
            duration = self._probe_duration(audio_path)
            analysis_seconds = min(duration or self.max_analysis_seconds, self.max_analysis_seconds)
            cmd = [
                self.ffmpeg,
                "-hide_banner",
                "-t", str(analysis_seconds),
                "-i", audio_path,
                "-af", f"silencedetect=noise={self.silence_threshold}dB:d=0.3",
                "-f", "null",
                "-"
            ]
            timeout_seconds = 45 if analysis_seconds >= 30 else 25
            return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds)

        try:
            result = await asyncio.to_thread(_run_silence)
            
            regions = []
            lines = result.stderr.split("\n")
            
            current_start = None
            for line in lines:
                if "silence_start:" in line:
                    try:
                        current_start = float(line.split("silence_start:")[1].strip().split()[0])
                    except (IndexError, ValueError):
                        pass
                elif "silence_end:" in line and current_start is not None:
                    try:
                        parts = line.split("silence_end:")[1].strip().split()
                        end = float(parts[0])
                        duration = float(parts[-1]) if len(parts) > 1 else end - current_start
                        regions.append(SilenceRegion(
                            start=current_start,
                            end=end,
                            duration=duration
                        ))
                    except (IndexError, ValueError):
                        pass
                    current_start = None
            
            return regions
            
        except subprocess.TimeoutExpired:
            logger.warning("silence_detection_timeout")
            return []
        except Exception as e:
            logger.warning("silence_detection_failed", error=str(e))
            return []
    
    async def _detect_speech_regions(self, audio_path: str) -> List[Tuple[float, float]]:
        """
        Simple speech detection based on energy levels.
        For production, use WhisperX or Pyannote.
        """
        # For now, invert silence regions as a simple heuristic
        silence_regions = await self._detect_silence(audio_path)
        
        if not silence_regions:
            return []
        
        speech_regions = []
        prev_end = 0.0
        
        for silence in silence_regions:
            if silence.start > prev_end + 0.1:
                speech_regions.append((prev_end, silence.start))
            prev_end = silence.end
        
        return speech_regions
    
    def get_trim_suggestions(self, analysis: AudioAnalysis) -> List[Dict[str, Any]]:
        """
        Get suggestions for silence trimming.
        """
        suggestions = []
        
        for region in analysis.silence_regions:
            if region.is_trimmable:
                # Suggest keeping small padding
                keep_before = 0.2
                keep_after = 0.2
                
                trim_start = region.start + keep_before
                trim_end = region.end - keep_after
                
                if trim_end > trim_start:
                    suggestions.append({
                        "type": "trim_silence",
                        "original_start": region.start,
                        "original_end": region.end,
                        "trim_start": trim_start,
                        "trim_end": trim_end,
                        "savings": trim_end - trim_start
                    })
        
        return suggestions
    
    def build_ducking_filter(
        self, 
        analysis: AudioAnalysis,
        policy: DuckingPolicy = None
    ) -> str:
        """
        Build FFmpeg filter for audio ducking during speech.
        """
        policy = policy or DuckingPolicy()
        
        if not analysis.speech_regions:
            return ""
        
        # Build volume keyframes for ducking
        keyframes = []
        
        for start, end in analysis.speech_regions:
            # Fade down before speech
            duck_start = max(0, start - policy.attack_time)
            keyframes.append(f"{duck_start}:volume=1.0")
            keyframes.append(f"{start}:volume={policy.duck_level}")
            
            # Hold during speech + hold time
            hold_end = end + policy.hold_time
            keyframes.append(f"{hold_end}:volume={policy.duck_level}")
            
            # Fade up after
            release_end = hold_end + policy.release_time
            keyframes.append(f"{release_end}:volume=1.0")
        
        # Use volume filter with sendcmd for keyframes
        # Simplified version: use sidechaincompress
        return f"sidechaincompress=threshold={policy.threshold_db}dB:ratio=4:attack={int(policy.attack_time*1000)}:release={int(policy.release_time*1000)}"
    
    def get_normalization_filter(
        self, 
        target_lufs: float = -14.0,
        analysis: Optional[AudioAnalysis] = None
    ) -> str:
        """
        Get FFmpeg filter for loudness normalization.
        """
        if analysis and not analysis.needs_normalization:
            return ""
        
        return f"loudnorm=I={target_lufs}:TP=-1:LRA=11"


# Global instance
audio_intelligence = AudioIntelligence()
