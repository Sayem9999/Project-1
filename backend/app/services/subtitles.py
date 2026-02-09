"""
Subtitles Service - Word-level timing, smart line breaks, safe area positioning.
"""
import structlog
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import re

logger = structlog.get_logger()


@dataclass
class Word:
    """A single word with timing information."""
    text: str
    start: float
    end: float
    confidence: float = 1.0


@dataclass
class SubtitleLine:
    """A subtitle line with timing and position."""
    text: str
    start: float
    end: float
    position: str = "bottom-center"  # bottom-center, top-center, etc.
    words: List[Word] = field(default_factory=list)


@dataclass
class SubtitleStyle:
    """Subtitle styling configuration."""
    font: str = "Arial"
    size: int = 48
    color: str = "#FFFFFF"
    outline_color: str = "#000000"
    outline_width: int = 2
    shadow: bool = True
    margin_bottom: int = 50
    margin_sides: int = 50
    max_chars_per_line: int = 42
    max_lines: int = 2
    
    def to_ass_style(self) -> str:
        """Convert to ASS style string."""
        return (
            f"FontName={self.font},"
            f"FontSize={self.size},"
            f"PrimaryColour=&H{self.color[1:]},"
            f"OutlineColour=&H{self.outline_color[1:]},"
            f"Outline={self.outline_width},"
            f"MarginV={self.margin_bottom}"
        )


class SubtitleService:
    """
    Advanced subtitle processing with word-level timing.
    """
    
    def __init__(self, style: SubtitleStyle = None):
        self.style = style or SubtitleStyle()
    
    def process_transcript(
        self, 
        words: List[Word],
        min_duration: float = 1.0,
        max_duration: float = 5.0
    ) -> List[SubtitleLine]:
        """
        Convert word-level transcript to subtitle lines.
        Applies smart line breaks and timing adjustments.
        """
        if not words:
            return []
        
        lines = []
        current_words = []
        current_text = ""
        line_start = words[0].start
        
        for word in words:
            test_text = (current_text + " " + word.text).strip()
            
            # Check if we need a new line
            needs_break = (
                len(test_text) > self.style.max_chars_per_line or
                word.start - line_start > max_duration or
                self._is_sentence_end(current_text)
            )
            
            if needs_break and current_words:
                # Finalize current line
                lines.append(SubtitleLine(
                    text=current_text,
                    start=line_start,
                    end=current_words[-1].end,
                    words=current_words.copy()
                ))
                
                # Start new line
                current_words = [word]
                current_text = word.text
                line_start = word.start
            else:
                current_words.append(word)
                current_text = test_text
        
        # Add final line
        if current_words:
            lines.append(SubtitleLine(
                text=current_text,
                start=line_start,
                end=current_words[-1].end,
                words=current_words.copy()
            ))
        
        # Apply minimum duration
        for line in lines:
            if line.end - line.start < min_duration:
                line.end = line.start + min_duration
        
        return lines
    
    def _is_sentence_end(self, text: str) -> bool:
        """Check if text ends with sentence punctuation."""
        return text.rstrip().endswith(('.', '!', '?', '...'))
    
    def smart_line_break(self, text: str, max_chars: int = None) -> List[str]:
        """
        Break text into lines at natural points.
        Prefers breaking at punctuation, conjunctions, prepositions.
        """
        max_chars = max_chars or self.style.max_chars_per_line
        
        if len(text) <= max_chars:
            return [text]
        
        # Natural break points (after these words)
        break_after = ['and', 'or', 'but', 'that', 'which', 'when', 'where', 'if', 'so', 'because']
        # Also break after commas
        
        words = text.split()
        lines = []
        current_line = []
        current_len = 0
        
        for i, word in enumerate(words):
            word_len = len(word) + (1 if current_line else 0)  # +1 for space
            
            if current_len + word_len > max_chars and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_len = len(word)
            else:
                current_line.append(word)
                current_len += word_len
                
                # Check for natural break point
                if (word.lower().rstrip('.,!?') in break_after or word.endswith(',')) \
                   and current_len > max_chars // 2:
                    lines.append(' '.join(current_line))
                    current_line = []
                    current_len = 0
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines[:self.style.max_lines]
    
    def apply_safe_area(
        self, 
        line: SubtitleLine,
        video_height: int = 1080,
        action_safe_pct: float = 0.05
    ) -> SubtitleLine:
        """Adjust subtitle position to stay within safe area."""
        safe_margin = int(video_height * action_safe_pct)
        
        if line.position == "bottom-center":
            # Ensure margin is at least safe area
            self.style.margin_bottom = max(self.style.margin_bottom, safe_margin)
        
        return line
    
    def to_srt(self, lines: List[SubtitleLine]) -> str:
        """Convert to SRT format."""
        srt_lines = []
        
        for i, line in enumerate(lines, 1):
            start = self._format_srt_time(line.start)
            end = self._format_srt_time(line.end)
            
            srt_lines.append(f"{i}")
            srt_lines.append(f"{start} --> {end}")
            srt_lines.append(line.text)
            srt_lines.append("")
        
        return "\n".join(srt_lines)
    
    def _format_srt_time(self, seconds: float) -> str:
        """Format seconds to SRT time format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def get_ffmpeg_filter(self, srt_path: str) -> str:
        """Generate FFmpeg subtitle filter command."""
        style = self.style.to_ass_style()
        return f"subtitles={srt_path}:force_style='{style}'"
    
    def calculate_readability(self, lines: List[SubtitleLine]) -> float:
        """Calculate average characters per second for readability check."""
        if not lines:
            return 0.0
        
        total_chars = sum(len(line.text) for line in lines)
        total_duration = sum(line.end - line.start for line in lines)
        
        return total_chars / total_duration if total_duration > 0 else 0.0


# Global instance
subtitle_service = SubtitleService()
