import pytest
import tempfile
import shutil
import os
import json
from pathlib import Path
from datetime import datetime, UTC
from unittest import mock

from positioning_service import PositioningService

@pytest.fixture
def temp_log_dir(monkeypatch):
    temp_dir = tempfile.mkdtemp()
    monkeypatch.setattr("positioning_service.Path", lambda *a, **kw: Path(temp_dir))
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_log_filename_generation(temp_log_dir):
    service = PositioningService(interval=2)
    log_file = service.get_log_filename()
    expected_name = f"position_log_{datetime.now(UTC).strftime('%Y-%m-%d')}.jsonl"
    assert expected_name in str(log_file)

def test_latest_position_from_logs(temp_log_dir, monkeypatch):
    service = PositioningService(interval=2)

    log_path = Path(temp_log_dir) / f"position_log_{datetime.now(UTC).strftime('%Y-%m-%d')}.jsonl"
    
    # Patch the get_log_filename method to return our test file path
    monkeypatch.setattr(service, "get_log_filename", lambda: log_path)

    entry1 = {"timestamp": "2025-04-16T00:00:00Z", "data": {"lat": 1.0, "lon": 2.0}}
    entry2 = {"timestamp": "2025-04-16T00:00:30Z", "data": {"lat": 3.0, "lon": 4.0}}

    with open(log_path, 'w') as f:
        f.write(json.dumps(entry1) + '\n')
        f.write(json.dumps(entry2) + '\n')

    result = service.get_latest_position_from_logs()
    assert result == entry2

def test_find_gnss_port_returns_none(monkeypatch):
    monkeypatch.setattr("serial.tools.list_ports.comports", lambda: [])
    service = PositioningService(interval=2)
    assert service.port is None

def test_coordinate_format_conversion():
    service = PositioningService(interval=2)
    lat, lon = service.coordinate_format_conversion("3745.1234", "N", "12228.5678", "W")
    assert abs(lat - 37.7520566667) < 0.0001
    assert abs(lon + 122.47613) < 0.0001
