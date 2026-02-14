from app.services.post_production_depth import (
    build_audio_post_filter,
    build_color_pipeline_filters,
    build_subtitle_filter,
    subtitle_qa_report,
)


def test_audio_post_filter_includes_loudnorm_and_mastering_chain():
    flt = build_audio_post_filter(
        {"ducking_segments": [(0.0, 1.0)]},
        platform="youtube",
        mood="cinematic",
    )
    assert "loudnorm=I=-14" in flt
    assert "acompressor" in flt
    assert "alimiter" in flt


def test_color_pipeline_filters_include_scene_match_and_skin_protect():
    filters = build_color_pipeline_filters("professional", media_intel={})
    joined = ",".join(filters)
    assert "normalize=" in joined
    assert "hue=" in joined


def test_subtitle_filter_applies_platform_style():
    flt = build_subtitle_filter("storage/outputs/test.srt", "tiktok")
    assert "subtitles='" in flt
    assert "FontSize=28" in flt


def test_subtitle_qa_report_flags_high_cps():
    srt = """1
00:00:00,000 --> 00:00:00,500
This subtitle line is intentionally too long for half a second.
"""
    report = subtitle_qa_report(srt)
    assert report["passed"] is False
    assert report["issue_count"] >= 1
