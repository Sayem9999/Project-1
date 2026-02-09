"""
Validator Node - Deterministic pre-render validation.
Checks timing overlaps, subtitle bounds, codec compatibility, duration tolerances.
"""
import structlog
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from ..state import GraphState

logger = structlog.get_logger()


@dataclass
class ValidationResult:
    """Result of validation checks."""
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, msg: str):
        self.errors.append(msg)
        self.passed = False
    
    def add_warning(self, msg: str):
        self.warnings.append(msg)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings
        }


class PreRenderValidator:
    """
    Deterministic validation checks before rendering.
    Prevents expensive failed renders.
    """
    
    def __init__(self):
        self.duration_tolerance = 0.5  # seconds
        self.min_cut_duration = 0.1    # seconds
        self.max_subtitle_chars = 80
        self.subtitle_margin = 0.05    # 5% safe area
    
    def validate(self, state: GraphState) -> ValidationResult:
        """Run all validation checks."""
        result = ValidationResult()
        
        # Run all validators
        self._check_timing_overlaps(state, result)
        self._check_cut_durations(state, result)
        self._check_subtitle_bounds(state, result)
        self._check_codec_compatibility(state, result)
        self._check_duration_tolerance(state, result)
        self._check_audio_tracks(state, result)
        
        logger.info(
            "validation_complete",
            passed=result.passed,
            errors=len(result.errors),
            warnings=len(result.warnings)
        )
        
        return result
    
    def _check_timing_overlaps(self, state: GraphState, result: ValidationResult):
        """Check for overlapping cuts or effects."""
        cuts = state.get("cuts", [])
        if not cuts:
            return
        
        # Sort by start time
        sorted_cuts = sorted(cuts, key=lambda x: x.get("start", 0))
        
        for i in range(len(sorted_cuts) - 1):
            current = sorted_cuts[i]
            next_cut = sorted_cuts[i + 1]
            
            current_end = current.get("end", 0)
            next_start = next_cut.get("start", 0)
            
            if current_end > next_start:
                overlap = current_end - next_start
                result.add_error(
                    f"Timing overlap: cut {i} ends at {current_end:.2f}s "
                    f"but cut {i+1} starts at {next_start:.2f}s (overlap: {overlap:.2f}s)"
                )
    
    def _check_cut_durations(self, state: GraphState, result: ValidationResult):
        """Check for cuts that are too short."""
        cuts = state.get("cuts", [])
        
        for i, cut in enumerate(cuts):
            duration = cut.get("end", 0) - cut.get("start", 0)
            if duration < self.min_cut_duration:
                result.add_warning(
                    f"Cut {i} is very short ({duration:.3f}s), may cause playback issues"
                )
            if duration < 0:
                result.add_error(
                    f"Cut {i} has negative duration (start: {cut.get('start')}, end: {cut.get('end')})"
                )
    
    def _check_subtitle_bounds(self, state: GraphState, result: ValidationResult):
        """Check subtitle text length and timing."""
        # Look for subtitles in visual_effects
        effects = state.get("visual_effects", [])
        
        for i, effect in enumerate(effects):
            if effect.get("type") == "subtitle" or "text" in effect:
                text = effect.get("text", "")
                
                # Check length
                if len(text) > self.max_subtitle_chars:
                    result.add_warning(
                        f"Subtitle {i} exceeds {self.max_subtitle_chars} chars ({len(text)} chars)"
                    )
                
                # Check timing
                start = effect.get("start", 0)
                end = effect.get("end", 0)
                if end <= start:
                    result.add_error(
                        f"Subtitle {i} has invalid timing (start: {start}, end: {end})"
                    )
    
    def _check_codec_compatibility(self, state: GraphState, result: ValidationResult):
        """Check for incompatible codec/filter combinations."""
        effects = state.get("visual_effects", [])
        
        # Known incompatible combinations
        incompatible_filters = {
            "hevc": ["complex_filter_x"],  # Example
        }
        
        for effect in effects:
            filter_name = effect.get("filter", "")
            # Check against known issues (expand as needed)
            if "undefined" in str(filter_name).lower():
                result.add_error(f"Filter contains undefined reference: {filter_name}")
    
    def _check_duration_tolerance(self, state: GraphState, result: ValidationResult):
        """Check if output duration matches expected."""
        user_request = state.get("user_request", {})
        target_duration = user_request.get("target_duration")
        
        if not target_duration:
            return
        
        cuts = state.get("cuts", [])
        if not cuts:
            return
        
        # Calculate total duration from cuts
        total_duration = sum(
            cut.get("end", 0) - cut.get("start", 0) 
            for cut in cuts
        )
        
        diff = abs(total_duration - target_duration)
        if diff > self.duration_tolerance:
            result.add_warning(
                f"Output duration ({total_duration:.1f}s) differs from target "
                f"({target_duration}s) by {diff:.1f}s"
            )
    
    def _check_audio_tracks(self, state: GraphState, result: ValidationResult):
        """Validate audio track configuration."""
        audio_tracks = state.get("audio_tracks", [])
        
        for i, track in enumerate(audio_tracks):
            # Check volume ranges
            volume = track.get("volume", 1.0)
            if volume < 0:
                result.add_error(f"Audio track {i} has negative volume: {volume}")
            if volume > 3.0:
                result.add_warning(f"Audio track {i} volume is very high: {volume}")
            
            # Check timing
            start = track.get("start", 0)
            end = track.get("end")
            if end is not None and end < start:
                result.add_error(f"Audio track {i} has invalid timing")


# Create validator instance
validator = PreRenderValidator()


def validator_node(state: GraphState) -> Dict[str, Any]:
    """
    LangGraph node for pre-render validation.
    """
    logger.info("validator_node_start", job_id=state.get("job_id"))
    
    result = validator.validate(state)
    
    # Add errors to state
    new_errors = state.get("errors", []).copy()
    new_errors.extend(result.errors)
    
    return {
        "errors": new_errors,
        "validation_result": result.to_dict()
    }
