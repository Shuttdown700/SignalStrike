from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from utilities import read_csv, write_csv
import os, sys
import argparse

def append_tile_to_queue(map_name: str, tile: list, file_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queue_files", "dynamic_tile_queue.csv")) -> None:
    """
    Appends tile row to queue csv file.

    Parameters
    ----------
    map_name : str
        Name of the map.
    tile : list
        Tile data represented as a [z, y, x] list.
    file_path : str, optional
        CSV file path string. The default is the path to "dynamic_tile_queue.csv" in the "queue_files" directory.

    Returns
    -------
    None
    """
    # End function if tile to append is blank
    if not tile:
        return

    # Open csv file
    if not os.path.isfile(file_path):
        with open(file_path, mode='w', newline='') as file:
            print(f"Creating batch queue file at: {file_path}\n")

    tile_data = {
        "Map": map_name,
        "Z": tile[0],
        "Y": tile[2],
        "X": tile[1]
    }
    # For tkintermapview, tile segment order is Z, X, Y !!!
    # print('Tile Data: ', tile_data)
    queue_data = read_csv(file_path)
    queue_data.append(tile_data)
    write_csv(file_path, queue_data)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    directory = os.path.dirname(os.path.abspath(__file__))

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path.lstrip('/')
        file_path = os.path.normpath(os.path.join(self.directory, path))
        print(file_path)

        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.serve_file(file_path)
        else:
            self.handle_404(file_path)

    def serve_file(self, file_path: str) -> None:
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
            self.send_response(200)
            self.send_header('Content-type', 'application/octet-stream')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {e}")

    def handle_404(self, file_path: str) -> None:
        self.send_response(404)
        self.end_headers()
        missing_tile = file_path.split(os.sep)[-1].split('.')[0].split('/')
        if len(missing_tile) > 3:
            map_name = missing_tile[0]
            missing_tile = missing_tile[-3:]
            append_tile_to_queue(map_name, missing_tile)

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, host="localhost", port=1234, directory="."):
    """
    Run HTTP Map Tile Server with dynamic missing tile identifier.

    Parameters
    ----------
    server_class : class object, optional
        The default is HTTPServer.
    handler_class : class object, optional
        The default is SimpleHTTPRequestHandler.
    host : str, optional
        Address to map server. The default is "localhost".
    port : int, optional
        Logical port to map server. The default is 1234.
    directory : str, optional
        Base directory of HTTP server. The default is ".".

    Returns
    -------
    None.
    """
    try:
        # set base directory
        handler_class.directory = directory
        # set server network attributes
        server_address = (host, port)
        # set HTTP server structure
        httpd = server_class(server_address, handler_class)
        # display that HTTP server is operational
        print(f"Server running on {host}:{port}, serving files from directory: {directory}")
        httpd.serve_forever()
    except Exception as e:
        print(f"Failed to start server: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run HTTP Map Tile Server with dynamic missing tile identifier.")
    parser.add_argument("--host", type=str, default="localhost", help="Address to map server. Default is 'localhost'.")
    parser.add_argument("--port", type=int, default=1234, help="Logical port to map server. Default is 1234.")
    default_server_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','map_tiles'))
    parser.add_argument("--directory", type=str, default=default_server_dir, help="Base directory of HTTP server. Default is current directory.")
    args = parser.parse_args()

    run(host=args.host, port=args.port, directory=args.directory)

# example CLI command
# python map_server.py localhost 1234 ../map_tiles/ESRI