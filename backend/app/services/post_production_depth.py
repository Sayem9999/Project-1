from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def build_audio_post_filter(audio_intel: dict[str, Any] | None, platform: str, mood: str) -> str:
    """Build mastering-grade audio chain with platform-aware loudness target."""
    platform_key = (platform or "youtube").lower()
    mood_key = (mood or "professional").lower()
    target_lufs = {
        "youtube": -14,
        "instagram": -14,
        "tiktok": -16,
        "podcast": -16,
    }.get(platform_key, -14)

    # 1. Dialogue Isolation & Noise Floor Cleanup (Phase 7)
    noise_floor = (audio_intel or {}).get("noise_floor", -60)
    nr_strength = 12 if noise_floor < -50 else 20
    
    chains = [
        f"afftdn=nr={nr_strength}:nf=-25", # Adaptive Noise Reduction
        "highpass=f=75", # Remove sub-bass rumble
        "lowpass=f=15000", # Remove high-end hiss
        "acompressor=threshold=-18dB:ratio=3.5:attack=5:release=80:makeup=2",
    ]

    if mood_key in {"cinematic", "dramatic"}:
        chains.append("firequalizer=gain_entry='entry(120,-2);entry(3000,1.5);entry(9000,0.8)'")
    elif mood_key in {"energetic", "fast"}:
        chains.append("dynaudnorm=f=150:g=7")

    speech_regions = (audio_intel or {}).get("ducking_segments") or []
    if speech_regions:
        # Sidechain compress simulation for speech clarity
        chains.append("alimiter=limit=0.93")
        chains.append("compand=points=-80/-80|-25/-20|-15/-10|0/-7")
    else:
        chains.append("alimiter=limit=0.97")

    chains.append(f"loudnorm=I={target_lufs}:TP=-1.5:LRA=9")
    return ",".join(chains)


def build_color_pipeline_filters(
    mood: str,
    media_intel: dict[str, Any] | None,
    visual_effects: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Build color chain with scene consistency + skin protection defaults."""
    filters: list[str] = []
    mood_key = (mood or "professional").lower()

    if mood_key in {"cinematic", "dramatic"}:
        filters.append("eq=contrast=1.08:saturation=1.12:gamma=0.98")
    elif mood_key in {"energetic", "fast"}:
        filters.append("eq=contrast=1.06:saturation=1.18")
    else:
        filters.append("eq=contrast=1.03:saturation=1.05")

    # Scene-matching baseline normalization.
    filters.append("normalize=blackpt=black:whitept=white:smoothing=20")

    # Skin-tone protection approximation (light desaturation in orange-red range).
    filters.append("hue='if(between(H,20,45),H,S*0.93)'")

    for effect in visual_effects or []:
        if effect.get("type") == "ffmpeg_filter" and effect.get("value"):
            filters.append(str(effect["value"]))

    return filters


def build_subtitle_style(platform: str) -> dict[str, Any]:
    platform_key = (platform or "youtube").lower()
    if platform_key == "tiktok":
        return {"font_size": 28, "outline": 2, "margin_v": 90, "alignment": 2}
    if platform_key == "instagram":
        return {"font_size": 26, "outline": 2, "margin_v": 80, "alignment": 2}
    return {"font_size": 24, "outline": 2, "margin_v": 70, "alignment": 2}


def build_subtitle_filter(srt_path: str, platform: str) -> str:
    style = build_subtitle_style(platform)
    escaped = str(Path(srt_path).absolute()).replace("\\", "/").replace(":", "\\:")
    force_style = (
        f"FontSize={style['font_size']},"
        f"Outline={style['outline']},"
        "Shadow=0,"
        "PrimaryColour=&H00FFFFFF,"
        f"MarginV={style['margin_v']},"
        f"Alignment={style['alignment']}"
    )
    return f"subtitles='{escaped}':force_style='{force_style}'"


def subtitle_qa_report(srt_text: str) -> dict[str, Any]:
    """Basic subtitle QA checks: cps, line length, empty blocks."""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", srt_text or "") if b.strip()]
    issues: list[str] = []
    max_cps = 20.0
    max_line_len = 42

    for idx, block in enumerate(blocks, start=1):
        lines = block.splitlines()
        if len(lines) < 3:
            issues.append(f"block_{idx}: malformed")
            continue

        ts = lines[1]
        text = " ".join(lines[2:])
        if not text.strip():
            issues.append(f"block_{idx}: empty_text")
            continue

        for line in lines[2:]:
            if len(line) > max_line_len:
                issues.append(f"block_{idx}: line_too_long")
                break

        m = re.match(
            r"(\d\d):(\d\d):(\d\d),(\d\d\d)\s+-->\s+(\d\d):(\d\d):(\d\d),(\d\d\d)",
            ts,
        )
        if not m:
            issues.append(f"block_{idx}: bad_timestamp")
            continue

        vals = [int(v) for v in m.groups()]
        start = vals[0] * 3600 + vals[1] * 60 + vals[2] + vals[3] / 1000
        end = vals[4] * 3600 + vals[5] * 60 + vals[6] + vals[7] / 1000
        dur = max(0.01, end - start)
        cps = len(text.replace(" ", "")) / dur
        if cps > max_cps:
            issues.append(f"block_{idx}: high_cps")

    return {
        "total_blocks": len(blocks),
        "issue_count": len(issues),
        "issues": issues[:20],
        "passed": len(issues) == 0,
    }


def build_lower_third_filter(title: str | None, subtitle: str | None = None) -> list[str]:
    """Build an animated lower-third (Phase 8)."""
    if not title:
        return []
    
    safe_title = str(title).replace(":", "\\:").replace("'", "\\'")
    safe_sub = str(subtitle or "").replace(":", "\\:").replace("'", "\\'")
    
    # Slide-in animation: x goes from -w to 40 over 0.5s
    # enable between 0 and 5s
    filters = [
        f"drawtext=text='{safe_title}':fontcolor=white:fontsize=42:fontfile=Montserrat-Bold:x='if(lt(t,0.5),-w+(w+40)*t/0.5,40)':y=h-150:enable='between(t,0,5.5)'"
    ]
    if safe_sub:
        filters.append(
            f"drawtext=text='{safe_sub}':fontcolor=white@0.8:fontsize=28:fontfile=Montserrat-Regular:x='if(lt(t,0.6),-w+(w+40)*(t-0.1)/0.5,40)':y=h-100:enable='between(t,0.1,5.5)'"
        )
    return filters


def build_kinetic_highlight_filters(word_timings: list[dict[str, Any]], highlight_color: str = "#FFFF00") -> list[str]:
    """
    Generate drawtext filters for word-level kinetic highlighting (Phase 8).
    Creates a 'pop-up' effect by scaling or changing color when word is active.
    """
    filters = []
    # Convert hex #RRGGBB to FFmpeg style 0xRRGGBB or name
    color = highlight_color.replace("#", "0x")
    
    for item in word_timings:
        if not item.get("should_highlight"):
            continue
            
        word = str(item["word"]).replace(":", "\\:").replace("'", "\\'")
        start = item["start"]
        end = item["end"]
        
        # Pop-up "highlight" filter: center screen, scale up slightly, bright color
        filters.append(
            f"drawtext=text='{word}':fontcolor={color}:fontsize=70:fontfile=Montserrat-ExtraBold:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,{start},{end})':alpha='if(lt(t,{start}+0.1),(t-{start})/0.1,1)'"
        )
        
    return filters
