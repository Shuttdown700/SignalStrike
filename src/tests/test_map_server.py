import unittest
from unittest.mock import patch, mock_open, MagicMock
import os, sys
from http.server import HTTPServer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from map_server import append_tile_to_queue, SimpleHTTPRequestHandler, run

class TestMapServer(unittest.TestCase):

    @patch('map_server.write_csv')
    @patch('map_server.read_csv', return_value=[])
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.isfile', return_value=False)
    def test_append_tile_to_queue(self, mock_isfile, mock_open, mock_read_csv, mock_write_csv):
        map_name = "ESRI"
        tile = [1, 2, 3]
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'queue_files','batch_tile_queue.csv'))
        
        append_tile_to_queue(map_name, tile, file_path)
        
        mock_open.assert_called_once_with(file_path, mode='w', newline='')
        mock_read_csv.assert_called_once_with(file_path)
        mock_write_csv.assert_called_once()
        self.assertEqual(mock_write_csv.call_args[0][1], [{'Map': map_name, 'Z': 1, 'Y': 3, 'X': 2}])

    @patch('map_server.append_tile_to_queue')
    @patch('os.path.exists', return_value=False)
    @patch('os.path.isfile', return_value=False)
    def test_handle_404(self, mock_isfile, mock_exists, mock_append_tile_to_queue):
        handler = SimpleHTTPRequestHandler(MagicMock(), MagicMock(), MagicMock())
        handler.send_response = MagicMock()
        handler.end_headers = MagicMock()
        file_path = "test_map/1/2/3.png"
        
        handler.handle_404(file_path)
        
        handler.send_response.assert_called_once_with(404)
        handler.end_headers.assert_called_once()
        mock_append_tile_to_queue.assert_called_once_with("test_map", ['1', '2', '3'])

    @patch('map_server.SimpleHTTPRequestHandler')
    @patch('http.server.HTTPServer')
    def test_run(self, mock_http_server, mock_handler_class):
        mock_httpd = MagicMock()
        mock_http_server.return_value = mock_httpd
        
        run(host="localhost", port=1234, directory=".")
        
        mock_handler_class.directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','map_tiles'))
        mock_http_server.assert_called_once_with(('localhost', 1234), mock_handler_class)
        mock_httpd.serve_forever.assert_called_once()

    @patch('builtins.open', new_callable=mock_open, read_data=b'test content')
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    def test_serve_file(self, mock_isfile, mock_exists, mock_open):
        handler = SimpleHTTPRequestHandler(MagicMock(), MagicMock(), MagicMock())
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        handler.wfile = MagicMock()
        file_path = "test_file.txt"
        
        handler.serve_file(file_path)
        
        mock_open.assert_called_once_with(file_path, 'rb')
        handler.send_response.assert_called_once_with(200)
        handler.send_header.assert_called_once_with('Content-type', 'application/octet-stream')
        handler.end_headers.assert_called_once()
        handler.wfile.write.assert_called_once_with(b'test content')

if __name__ =='' "__main__":
    unittest.main()