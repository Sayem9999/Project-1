from app.services.workflow_engine import ensure_editing_cuts


def test_ensure_editing_cuts_generates_when_empty():
    cuts = ensure_editing_cuts([], duration=40.0, pacing="medium")
    assert len(cuts) >= 2
    total = sum(c["end"] - c["start"] for c in cuts)
    assert total < 40.0


def test_ensure_editing_cuts_replaces_passthrough():
    passthrough = [{"start": 0.0, "end": 60.0, "reason": "full"}]
    cuts = ensure_editing_cuts(passthrough, duration=60.0, pacing="fast")
    total = sum(c["end"] - c["start"] for c in cuts)
    assert total < 55.0
    assert len(cuts) >= 2


def test_ensure_editing_cuts_keeps_meaningful_ai_cuts():
    ai_cuts = [{"start": 1.0, "end": 4.0}, {"start": 7.0, "end": 12.0}]
    cuts = ensure_editing_cuts(ai_cuts, duration=20.0, pacing="slow")
    assert cuts == [
        {"start": 1.0, "end": 4.0, "reason": "ai-cut"},
        {"start": 7.0, "end": 12.0, "reason": "ai-cut"},
    ]
