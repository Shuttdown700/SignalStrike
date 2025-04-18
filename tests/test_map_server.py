import pytest
import os
from http.client import HTTPConnection
from pathlib import Path
from unittest.mock import patch
from map_server import MapServer, MapRequestHandler
import logging
import tempfile
import threading
import time
import socket

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

@pytest.fixture
def map_server(temp_dir):
    """Create a MapServer instance with a temporary directory."""
    queue_file = temp_dir / "queue_files" / "test_queue.csv"  # Match MapServer's queue file path
    queue_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    server = MapServer(
        host="localhost",
        port=0,
        directory=str(temp_dir),
        queue_file=str(queue_file)
    )
    return server

@pytest.fixture
def running_server(map_server):
    """Start the server in a separate thread and clean up after."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 0))
        _, port = s.getsockname()
    map_server.port = port

    server_thread = threading.Thread(target=map_server.run, daemon=True)
    server_thread.start()
    time.sleep(0.5)
    yield map_server
    map_server.shutdown()

def test_map_server_initialization(temp_dir):
    """Test MapServer initialization."""
    queue_file = temp_dir / "queue_files" / "test_queue.csv"
    queue_file.parent.mkdir(parents=True, exist_ok=True)
    server = MapServer(
        host="localhost",
        port=1234,
        directory=str(temp_dir),
        queue_file=str(queue_file)
    )
    assert server.host == "localhost"
    assert server.port == 1234
    assert server.directory == temp_dir.resolve()
    assert server.queue_file == queue_file.resolve()
    assert server.logger.name == "map_server"

def test_append_tile_to_queue(temp_dir):
    """Test appending a tile to the queue CSV."""
    queue_file = temp_dir / "queue_files" / "test_queue.csv"
    queue_file.parent.mkdir(parents=True, exist_ok=True)
    server = MapServer(directory=str(temp_dir), queue_file=str(queue_file))
    tile = [1, 2, 3]
    map_name = "test_map"

    server.append_tile_to_queue(map_name, tile)

    assert queue_file.exists()
    with open(queue_file, 'r') as f:
        content = f.read()
        assert "Map,Z,X,Y" in content
        assert f"{map_name},1,2,3" in content

def test_append_tile_to_queue_invalid_tile(temp_dir):
    """Test appending an invalid tile to the queue."""
    queue_file = temp_dir / "queue_files" / "test_queue.csv"
    queue_file.parent.mkdir(parents=True, exist_ok=True)
    server = MapServer(directory=str(temp_dir), queue_file=str(queue_file))
    with patch.object(server.logger, 'warning') as mock_warning:
        server.append_tile_to_queue("test_map", [])
        mock_warning.assert_called_once_with("Invalid or empty tile: []")

def test_do_get_existing_file(running_server, temp_dir):
    """Test GET request for an existing file."""
    test_file = temp_dir / "test.png"
    with open(test_file, 'wb') as f:
        f.write(b"test content")

    conn = HTTPConnection("localhost", running_server.port)
    conn.request("GET", "/test.png")
    response = conn.getresponse()

    assert response.status == 200
    assert response.getheader("Content-type") == "application/octet-stream"
    assert response.read() == b"test content"
    conn.close()

def test_map_server_shutdown(map_server):
    """Test server shutdown."""
    with patch.object(map_server.logger, 'info') as mock_info:
        map_server.shutdown()
        mock_info.assert_called_once_with("Shutting down server")
