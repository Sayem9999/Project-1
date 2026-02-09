"""
Timeline DSL - Intermediate JSON representation for video edits.
Converts agent directives into a canonical timeline format.
"""
import structlog
from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = structlog.get_logger()


class TrackType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    OVERLAY = "overlay"
    SUBTITLE = "subtitle"


class TransitionType(str, Enum):
    CUT = "cut"
    CROSSFADE = "crossfade"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    WIPE = "wipe"
    DISSOLVE = "dissolve"


@dataclass
class TimeRange:
    """Time range with start and end in seconds."""
    start: float
    end: float
    
    @property
    def duration(self) -> float:
        return self.end - self.start
    
    def to_dict(self) -> Dict[str, float]:
        return {"start": self.start, "end": self.end, "duration": self.duration}


@dataclass
class Clip:
    """A single clip in the timeline."""
    id: str
    source: str  # Source file path
    source_range: TimeRange  # Range in source file
    timeline_start: float  # Position on timeline
    track: int = 0
    
    # Effects
    speed: float = 1.0
    volume: float = 1.0
    filters: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "source_range": self.source_range.to_dict(),
            "timeline_start": self.timeline_start,
            "track": self.track,
            "speed": self.speed,
            "volume": self.volume,
            "filters": self.filters,
        }


@dataclass
class Transition:
    """Transition between clips."""
    type: TransitionType
    duration: float
    from_clip: str  # Clip ID
    to_clip: str    # Clip ID
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "duration": self.duration,
            "from_clip": self.from_clip,
            "to_clip": self.to_clip,
        }


@dataclass
class Overlay:
    """Text or image overlay."""
    id: str
    type: Literal["text", "image"]
    content: str  # Text content or image path
    time_range: TimeRange
    position: Dict[str, Any] = field(default_factory=dict)  # x, y, anchor
    style: Dict[str, Any] = field(default_factory=dict)  # font, size, color
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "time_range": self.time_range.to_dict(),
            "position": self.position,
            "style": self.style,
        }


@dataclass
class AudioTrack:
    """Audio track configuration."""
    id: str
    source: str
    source_range: TimeRange
    timeline_start: float
    volume: float = 1.0
    fade_in: float = 0.0
    fade_out: float = 0.0
    ducking: bool = False  # Duck when speech is present
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "source_range": self.source_range.to_dict(),
            "timeline_start": self.timeline_start,
            "volume": self.volume,
            "fade_in": self.fade_in,
            "fade_out": self.fade_out,
            "ducking": self.ducking,
        }


@dataclass
class Timeline:
    """Complete timeline representation."""
    id: str
    source_file: str
    duration: float
    resolution: tuple[int, int] = (1920, 1080)
    fps: float = 30.0
    
    clips: List[Clip] = field(default_factory=list)
    transitions: List[Transition] = field(default_factory=list)
    overlays: List[Overlay] = field(default_factory=list)
    audio_tracks: List[AudioTrack] = field(default_factory=list)
    
    # Global effects
    color_grade: Optional[str] = None
    loudness_target: float = -14.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_file": self.source_file,
            "duration": self.duration,
            "resolution": list(self.resolution),
            "fps": self.fps,
            "clips": [c.to_dict() for c in self.clips],
            "transitions": [t.to_dict() for t in self.transitions],
            "overlays": [o.to_dict() for o in self.overlays],
            "audio_tracks": [a.to_dict() for a in self.audio_tracks],
            "color_grade": self.color_grade,
            "loudness_target": self.loudness_target,
        }
    
    def add_clip(self, clip: Clip) -> "Timeline":
        self.clips.append(clip)
        return self
    
    def add_transition(self, transition: Transition) -> "Timeline":
        self.transitions.append(transition)
        return self
    
    def add_overlay(self, overlay: Overlay) -> "Timeline":
        self.overlays.append(overlay)
        return self
    
    def add_audio(self, audio: AudioTrack) -> "Timeline":
        self.audio_tracks.append(audio)
        return self


def from_graph_state(state: Dict[str, Any]) -> Timeline:
    """
    Convert LangGraph state to Timeline DSL.
    """
    job_id = state.get("job_id", 0)
    source_path = state.get("source_path", "")
    
    timeline = Timeline(
        id=f"timeline_{job_id}",
        source_file=source_path,
        duration=0.0,
    )
    
    # Convert cuts to clips
    cuts = state.get("cuts", [])
    timeline_pos = 0.0
    
    for i, cut in enumerate(cuts):
        clip = Clip(
            id=f"clip_{i}",
            source=source_path,
            source_range=TimeRange(
                start=cut.get("start", 0),
                end=cut.get("end", 0)
            ),
            timeline_start=timeline_pos,
            filters=cut.get("filters", [])
        )
        timeline.add_clip(clip)
        timeline_pos += clip.source_range.duration
    
    timeline.duration = timeline_pos
    
    # Convert visual effects to overlays
    effects = state.get("visual_effects", [])
    for i, effect in enumerate(effects):
        if effect.get("type") == "text" or "text" in effect:
            overlay = Overlay(
                id=f"overlay_{i}",
                type="text",
                content=effect.get("text", ""),
                time_range=TimeRange(
                    start=effect.get("start", 0),
                    end=effect.get("end", 0)
                ),
                style=effect.get("style", {})
            )
            timeline.add_overlay(overlay)
    
    # Convert audio tracks
    audio_tracks = state.get("audio_tracks", [])
    for i, track in enumerate(audio_tracks):
        audio = AudioTrack(
            id=f"audio_{i}",
            source=track.get("source", source_path),
            source_range=TimeRange(
                start=track.get("start", 0),
                end=track.get("end", timeline.duration)
            ),
            timeline_start=0.0,
            volume=track.get("volume", 1.0)
        )
        timeline.add_audio(audio)
    
    # Apply color grade from director plan
    director_plan = state.get("director_plan", {})
    if "color_palette" in director_plan:
        timeline.color_grade = director_plan["color_palette"]
    
    logger.info(
        "timeline_created",
        job_id=job_id,
        clips=len(timeline.clips),
        overlays=len(timeline.overlays),
        duration=timeline.duration
    )
    
    return timeline
