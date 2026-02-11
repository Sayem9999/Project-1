import pytest
from app.services.introspection import IntrospectionService
from pathlib import Path

def test_introspection_scan_detects_app_root():
    service = IntrospectionService()
    # It should have detected the backend/app directory
    assert "app" in service.root_dir
    assert Path(service.root_dir).exists()

def test_introspection_scan_finds_nodes():
    service = IntrospectionService()
    data = service.scan()
    
    assert "nodes" in data
    assert "stats" in data
    
    # Verify we have some endpoints
    endpoints = [n for n in data["nodes"] if n["type"] == "endpoint"]
    assert len(endpoints) > 0
    
    # Verify we have some models
    models = [n for n in data["nodes"] if n["type"] == "model"]
    assert len(models) > 0
    
    # Verify stats
    assert data["stats"]["total_nodes"] == len(data["nodes"])
    assert data["stats"]["source_files"] > 0
    assert data["stats"]["lines_of_code"] > 0

def test_introspection_scan_path_override():
    service = IntrospectionService(root_dir="app")
    assert service.root_dir == "app"


def test_introspection_health_status_after_scan():
    service = IntrospectionService()
    status_before = service.get_health_status()
    assert status_before["stale"] is True

    service.scan(force=True)
    status_after = service.get_health_status()
    assert status_after["scan_failures"] == 0
    assert status_after["last_scan_at_unix"] is not None
    assert status_after["graph_nodes"] > 0


def test_introspection_self_heal_returns_graph():
    service = IntrospectionService()
    result = service.self_heal()
    assert result["status"] in {"healthy", "self_healed"}
    assert "graph" in result
    assert result["graph"]["stats"]["total_nodes"] == len(result["graph"]["nodes"])
