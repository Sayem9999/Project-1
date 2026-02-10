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
