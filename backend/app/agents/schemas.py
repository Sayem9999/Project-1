"""
Agent Output Schemas - Pydantic models for structured agent outputs.
Each agent returns validated JSON that matches these schemas.
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional
from enum import Enum


# ============================================================================
# Director Agent
# ============================================================================
class DirectorInstructions(BaseModel):
    cutter: str = Field(..., description="Instructions for SLICE (Cutter)")
    color: str = Field(..., description="Instructions for PRISM (Colorist)")
    audio: str = Field(..., description="Instructions for ECHO (Audio)")


class DirectorOutput(BaseModel):
    """Output from MAX - the Director Agent."""
    directors_vision: str = Field(..., description="2-3 sentence artistic vision")
    pacing: Literal["fast", "medium", "slow"]
    mood: str = Field(..., description="One-word emotional tone")
    color_palette: str = Field(..., description="Primary colors to use")
    instructions: DirectorInstructions


# ============================================================================
# Cutter Agent
# ============================================================================
class CutItem(BaseModel):
    start: float
    end: float
    reason: str

class CutterOutput(BaseModel):
    """Output from SLICE - the Cutter Agent."""
    cuts: list[CutItem] = Field(..., description="List of segments to keep")
    ffmpeg_select_filter: str = Field(..., description="FFmpeg filter for cuts")
    reasoning: str = Field(..., description="Why this creates intended pacing")
    estimated_cuts: Literal["Many jump cuts", "Moderate transitions", "Minimal cuts"]


# ============================================================================
# Color Agent
# ============================================================================
class ColorOutput(BaseModel):
    """Output from PRISM - the Colorist Agent."""
    ffmpeg_color_filter: str = Field(..., description="FFmpeg color filter chain")
    color_mood: str = Field(..., description="One-word emotional descriptor")
    lut_recommendation: str = Field(..., description="Suggested LUT style")


# ============================================================================
# Audio Agent
# ============================================================================
class AudioOutput(BaseModel):
    """Output from ECHO - the Audio Engineer Agent."""
    ffmpeg_audio_filter: str = Field(..., description="FFmpeg audio filter chain")
    audio_character: str = Field(..., description="One-word descriptor")
    notes: str = Field(..., description="Brief sonic signature explanation")


# ============================================================================
# QC Agent
# ============================================================================
class QCOutput(BaseModel):
    """Output from THE PRODUCER - the QC Agent."""
    approved: bool
    score: float = Field(..., ge=1, le=10)
    verdict: Literal["APPROVED", "NEEDS REVISION"]
    feedback: str
    standout_element: str = Field(..., description="Best part of the plan")


# ============================================================================
# Script Agent
# ============================================================================
class FontConfig(BaseModel):
    font: str
    size: int
    color: str
    outline_color: str
    outline_width: int
    position: str
    margin_bottom: int


class TimingAdjustment(BaseModel):
    original_start: float
    adjusted_start: float
    reason: str


class ScriptOutput(BaseModel):
    """Output from SCRIBE - the Script Agent."""
    subtitle_style: str
    font_config: FontConfig
    timing_adjustments: list[TimingAdjustment] = []
    ffmpeg_subtitle_filter: str
    enhancement_tips: list[str] = []


# ============================================================================
# Transition Agent
# ============================================================================
class TransitionItem(BaseModel):
    position: str
    type: str
    duration: float
    reason: str


class TransitionOutput(BaseModel):
    """Output from TRANS - the Transition Agent."""
    transitions: list[TransitionItem]
    ffmpeg_filter: str
    style_note: str


# ============================================================================
# Thumbnail Agent
# ============================================================================
class RecommendedFrame(BaseModel):
    timestamp: float
    reason: str
    score: float


class TextOverlay(BaseModel):
    text: str
    position: str
    style: str


class ThumbnailOutput(BaseModel):
    """Output from THUMB - the Thumbnail Agent."""
    recommended_frames: list[RecommendedFrame]
    best_timestamp: float
    text_overlay: Optional[TextOverlay] = None
    enhancements: list[str] = []
    ffmpeg_extract: str
    ffmpeg_enhance: str = ""


# ============================================================================
# VFX Agent
# ============================================================================
class VFXOutput(BaseModel):
    """Output from VFX specialist agent."""
    effects: list[dict] = []
    ffmpeg_filter: str
    complexity: Literal["simple", "moderate", "complex"]
    notes: str = ""


# ============================================================================
# Keyframe Agent
# ============================================================================
class KeyframeOutput(BaseModel):
    """Output from keyframe extraction agent."""
    keyframes: list[dict] = []
    scene_changes: list[float] = []
    analysis: str = ""


# ============================================================================
# Subtitle Agent
# ============================================================================
class SubtitleOutput(BaseModel):
    """Output from subtitle agent."""
    srt_content: str = ""
    style: str = "default"
    ffmpeg_filter: str = ""


# ============================================================================
# Metadata Agent
# ============================================================================
class MetadataOutput(BaseModel):
    """Output from metadata agent."""
    title: str = ""
    description: str = ""
    tags: list[str] = []
    category: str = ""


# ============================================================================
# NEW SPECIALIST AGENTS
# ============================================================================

# Hook Agent
class HookOutput(BaseModel):
    """Output from HOOK - optimize first 3 seconds for retention."""
    attention_technique: str = Field(..., description="Hook technique used")
    opening_cuts: list[dict] = Field(default=[], description="Cuts for first 3s")
    hook_text: Optional[str] = Field(None, description="Text overlay for hook")
    retention_score: int = Field(..., ge=1, le=10, description="Predicted retention")


# Platform Agent
class PlatformOutput(BaseModel):
    """Output from PLATFORM - adapt for different platforms."""
    platform: Literal["tiktok", "reels", "youtube_shorts", "youtube_long"]
    aspect_ratio: str = Field(..., description="e.g., 9:16, 16:9, 1:1")
    max_duration: int = Field(..., description="Max duration in seconds")
    captions_style: str
    music_policy: str
    ffmpeg_resize: str = ""


# Brand Safety Agent
class Violation(BaseModel):
    type: str
    severity: Literal["low", "medium", "high"]
    timestamp: Optional[float] = None
    description: str


class BrandSafetyOutput(BaseModel):
    """Output from BRAND_SAFETY - content moderation checks."""
    is_safe: bool
    violations: list[Violation] = []
    risk_score: int = Field(..., ge=0, le=100)
    recommendations: list[str] = []


# A/B Test Agent
class Variant(BaseModel):
    id: str
    type: Literal["opening", "title", "thumbnail", "hook"]
    content: dict
    predicted_performance: float = Field(..., ge=0, le=1)


class ABTestOutput(BaseModel):
    """Output from AB_TEST - generate variants for testing."""
    variants: list[Variant]
    rankings: list[str] = Field(..., description="Variant IDs in ranked order")
    rationale: str


# Eval Agent
class EvalScore(BaseModel):
    category: str
    score: float = Field(..., ge=1, le=10)
    reason: str


class EvalOutput(BaseModel):
    """Output from EVAL - the technical and aesthetic evaluator."""
    overall_score: float = Field(..., ge=1, le=10)
    scores: list[EvalScore]
    approved: bool
    verdict: str
    critical_issues: list[str] = []
    optimization_suggestions: list[str] = []


# ============================================================================
# Schema Registry - Map agent names to their output schemas
# ============================================================================
AGENT_SCHEMAS = {
    "director": DirectorOutput,
    "cutter": CutterOutput,
    "color": ColorOutput,
    "audio": AudioOutput,
    "qc": QCOutput,
    "script": ScriptOutput,
    "transition": TransitionOutput,
    "thumbnail": ThumbnailOutput,
    "vfx": VFXOutput,
    "keyframe": KeyframeOutput,
    "subtitle": SubtitleOutput,
    "metadata": MetadataOutput,
    # New specialist agents
    "hook": HookOutput,
    "platform": PlatformOutput,
    "brand_safety": BrandSafetyOutput,
    "ab_test": ABTestOutput,
    "eval": EvalOutput,
}
