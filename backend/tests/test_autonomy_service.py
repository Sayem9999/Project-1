import pytest

from app.services.autonomy_service import AutonomyService
from app.agents.routing_policy import provider_router
from app.config import settings


@pytest.mark.asyncio
async def test_run_once_executes_heal_and_improve_when_idle(monkeypatch):
    service = AutonomyService()

    async def fake_recover():
        return 0

    async def fake_idle():
        return True

    async def fake_heal():
        return {"heal": "ok"}

    async def fake_improve():
        return {"improve": "ok"}

    async def fake_load():
        return {"cpu_percent": 5.0, "memory_percent": 10.0}

    monkeypatch.setattr(service, "_recover_stuck_jobs", fake_recover)
    monkeypatch.setattr(service, "_is_system_idle", fake_idle)
    monkeypatch.setattr(service, "_run_heal_cycle", fake_heal)
    monkeypatch.setattr(service, "_run_improve_cycle", fake_improve)
    monkeypatch.setattr(service, "_get_system_load", fake_load)

    result = await service.run_once(force_improve=False)
    assert result["idle"] is True
    assert result["heal_ran"] is True
    assert result["improve_ran"] is True
    assert result["heal"] == {"heal": "ok"}
    assert result["improve"] == {"improve": "ok"}


@pytest.mark.asyncio
async def test_run_once_skips_when_not_idle(monkeypatch):
    service = AutonomyService()

    async def fake_recover():
        return 1

    async def fake_idle():
        return False

    async def fake_load():
        return {"cpu_percent": 5.0, "memory_percent": 10.0}

    monkeypatch.setattr(service, "_recover_stuck_jobs", fake_recover)
    monkeypatch.setattr(service, "_is_system_idle", fake_idle)
    monkeypatch.setattr(service, "_get_system_load", fake_load)

    result = await service.run_once(force_improve=False)
    assert result["idle"] is False
    assert result["recovered_stuck_jobs"] == 1
    assert result["heal_ran"] is False
    assert result["improve_ran"] is False


def test_heal_provider_routing_opens_circuit_for_unhealthy_provider():
    service = AutonomyService()
    state = provider_router.health["gemini"]
    original = (state.circuit_open, state.circuit_open_until)
    try:
        state.circuit_open = False
        state.circuit_open_until = None
        actions = service._heal_provider_routing(
            {
                "gemini": {
                    "configured": True,
                    "success_rate": 0.2,
                    "failure_count": 10,
                    "is_healthy": True,
                }
            }
        )
        assert actions
        assert actions[0]["provider"] == "gemini"
        assert actions[0]["action"] == "open_circuit"
        assert state.circuit_open is True
    finally:
        state.circuit_open, state.circuit_open_until = original


@pytest.mark.asyncio
async def test_run_once_skips_on_high_load(monkeypatch):
    service = AutonomyService()

    async def fake_recover():
        return 0

    async def fake_idle():
        return True

    async def fake_load():
        return {"cpu_percent": 99.0, "memory_percent": 95.0}

    monkeypatch.setattr(service, "_recover_stuck_jobs", fake_recover)
    monkeypatch.setattr(service, "_is_system_idle", fake_idle)
    monkeypatch.setattr(service, "_get_system_load", fake_load)

    result = await service.run_once()
    assert result["high_load"] is True
    assert result["heal_ran"] is False
    assert result["improve_ran"] is False
    assert service.get_status()["metrics"]["skip_high_load_count"] >= 1


def test_set_profile_updates_mode_and_profile():
    service = AutonomyService()
    status = service.set_profile("aggressive")
    assert status["profile_mode"] == "aggressive"
    assert status["profile"]["poll_seconds"] == 10


def test_set_profile_rejects_invalid_mode():
    service = AutonomyService()
    with pytest.raises(ValueError):
        service.set_profile("invalid-mode")


def test_profile_mode_uses_config_default(monkeypatch):
    monkeypatch.setattr(settings, "autonomy_profile_mode", "aggressive", raising=False)
    service = AutonomyService()
    assert service.get_status()["profile_mode"] == "aggressive"


@pytest.mark.asyncio
async def test_force_heal_runs_even_on_high_load(monkeypatch):
    service = AutonomyService()

    async def fake_recover():
        return 0

    async def fake_idle():
        return True

    async def fake_load():
        return {"cpu_percent": 99.0, "memory_percent": 95.0}

    async def fake_heal():
        return {"heal": "ok"}

    monkeypatch.setattr(service, "_recover_stuck_jobs", fake_recover)
    monkeypatch.setattr(service, "_is_system_idle", fake_idle)
    monkeypatch.setattr(service, "_get_system_load", fake_load)
    monkeypatch.setattr(service, "_run_heal_cycle", fake_heal)

    result = await service.run_once(force_heal=True)
    assert result["high_load"] is True
    assert result["heal_ran"] is True
