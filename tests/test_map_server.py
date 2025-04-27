# test_map_server.py
import io
import os
import tempfile
import pytest
from http.server import HTTPServer
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path

from map_server import MapServer, MapRequestHandler

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def map_server(temp_dir):
    server = MapServer(host="localhost", port=8080, directory=temp_dir)
    return server

def test_append_valid_tile_to_queue(tmp_path, map_server):
    tile = [5, 10, 20]
    map_name = "test_map"
    queue_file = tmp_path / "queue_files" / "dynamic_tile_queue.csv"
    map_server.queue_file = queue_file

    with patch("map_server.read_csv", return_value=[]), \
         patch("map_server.write_csv") as mock_write_csv:
        map_server.append_tile_to_queue(map_name, tile)
        mock_write_csv.assert_called_once()
        assert mock_write_csv.call_args[0][1] == [{
            "Map": "test_map", "Z": 5, "X": 10, "Y": 20
        }]

def test_append_invalid_tile_to_queue(map_server):
    map_server.logger = MagicMock()
    map_server.append_tile_to_queue("map", ["a", "b", "c"])
    map_server.logger.warning.assert_called()

def test_do_get_successful_file_response(map_server, tmp_path):
    # Setup: create a file to serve
    test_file_path = tmp_path / "tiles" / "5" / "10" / "20.png"
    test_file_path.parent.mkdir(parents=True, exist_ok=True)
    test_file_path.write_bytes(b"tile data")
    map_server.directory = tmp_path

    request_handler = setup_handler("/tiles/5/10/20.png", map_server)
    request_handler.do_GET()

    assert request_handler._response_code == 200
    assert request_handler._written_data == b"tile data"

def test_do_get_missing_tile_queued(map_server, tmp_path):
    map_server.logger = MagicMock()
    map_server.append_tile_to_queue = MagicMock()
    map_server.directory = tmp_path

    request_handler = setup_handler("/test_map/5/10/20.png", map_server)
    request_handler.do_GET()

    map_server.append_tile_to_queue.assert_called_once_with("test_map", [5, 10, 20])
    assert request_handler._response_code == 404

def test_do_get_invalid_tile_format(map_server, tmp_path):
    map_server.logger = MagicMock()
    map_server.append_tile_to_queue = MagicMock()
    map_server.directory = tmp_path

    # Missing coordinate parts
    request_handler = setup_handler("/5/10.png", map_server)
    request_handler.do_GET()

    map_server.logger.error.assert_called()
    map_server.append_tile_to_queue.assert_not_called()
    assert request_handler._response_code == 404

def test_run_and_shutdown(map_server):
    with patch.object(HTTPServer, 'serve_forever', side_effect=KeyboardInterrupt), \
         patch.object(MapServer, 'shutdown') as mock_shutdown:
        with pytest.raises(KeyboardInterrupt):
            map_server.run()
        mock_shutdown.assert_not_called()  # Since KeyboardInterrupt is caught inside run()

    map_server.logger = MagicMock()
    map_server.shutdown()
    map_server.logger.info.assert_called_with("Shutting down server")

# Utility to simulate BaseHTTPRequestHandler without running an actual server
def setup_handler(path, map_server):
    class DummySocket(io.BytesIO):
        def makefile(self, *args, **kwargs):
            return self

    handler = MapRequestHandler(DummySocket(), ("127.0.0.1", 12345), None)
    handler.path = path
    handler.map_server = map_server
    handler.wfile = io.BytesIO()
    handler._response_code = None
    handler._written_data = None

    def send_response(code):
        handler._response_code = code

    def send_header(key, val):
        pass

    def end_headers():
        pass

    def write(data):
        handler._written_data = data

    handler.send_response = send_response
    handler.send_header = send_header
    handler.end_headers = end_headers
    handler.wfile.write = write

    return handler
