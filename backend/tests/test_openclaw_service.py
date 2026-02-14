import pytest

from app.services.openclaw_service import OpenClawService
import app.services.openclaw_service as openclaw_module


@pytest.mark.asyncio
async def test_openclaw_generates_strategy_from_dict_outputs(monkeypatch):
    service = OpenClawService()

    async def fake_director(_payload):
        return {
            "directors_vision": "Keep it punchy.",
            "pacing": "fast",
            "mood": "energetic",
            "color_palette": "Teal Orange",
            "instructions": {
                "cutter": "Cut dead space",
                "color": "Boost contrast",
            },
        }

    async def fake_cutter(_payload):
        return {"cuts": [{"start": 0.0, "end": 3.0, "reason": "hook"}]}

    async def fake_color(_payload):
        return {"ffmpeg_color_filter": "eq=contrast=1.1:saturation=1.1"}

    monkeypatch.setattr(openclaw_module, "run_director", fake_director)
    monkeypatch.setattr(openclaw_module, "run_cutter", fake_cutter)
    monkeypatch.setattr(openclaw_module, "run_color", fake_color)

    strategy = await service.get_editing_strategy(
        job_id=99,
        media_intelligence={"visual": {"scenes": []}},
        user_requirements={"mood": "professional", "pacing": "medium"},
    )

    assert strategy["job_id"] == 99
    assert len(strategy["cuts"]) == 1
    assert strategy["vf_filters"] == "eq=contrast=1.1:saturation=1.1"
    assert strategy["metadata"]["mood"] == "energetic"


@pytest.mark.asyncio
async def test_openclaw_survives_specialist_failures(monkeypatch):
    service = OpenClawService()

    async def fake_director(_payload):
        return {
            "directors_vision": "Safe fallback vision",
            "pacing": "medium",
            "mood": "professional",
            "color_palette": "Natural",
            "instructions": {},
        }

    async def failing_cutter(_payload):
        raise RuntimeError("cutter unavailable")

    async def failing_color(_payload):
        raise RuntimeError("color unavailable")

    monkeypatch.setattr(openclaw_module, "run_director", fake_director)
    monkeypatch.setattr(openclaw_module, "run_cutter", failing_cutter)
    monkeypatch.setattr(openclaw_module, "run_color", failing_color)

    strategy = await service.get_editing_strategy(
        job_id=100,
        media_intelligence={},
        user_requirements={"mood": "professional", "pacing": "medium"},
    )

    assert strategy["job_id"] == 100
    assert strategy["cuts"] == []
    assert strategy["vf_filters"] is None
    assert strategy["af_filters"].startswith("loudnorm=")
