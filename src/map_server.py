from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from download_tiles import download_tile
import os
import sys
import csv

def append_tile_to_queue(tile,file_path=os.path.dirname(os.path.abspath(__file__))+"/tile_queue.csv"):
    if tile == "" or tile == []: return
    row_to_append = tile
    with open(file_path, mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(row_to_append)
    

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        # Remove leading slash to get the file path
        if path.startswith("/"):
            path = path[1:]
        
        # Check if the file exists within the specified directory
        file_path = os.path.join(SimpleHTTPRequestHandler.directory, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            # Open and read the file
            with open(file_path, 'rb') as file:
                content = file.read()
            self.send_response(200)
            self.send_header('Content-type', 'application/octet-stream')
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()
            missing_tile = file_path.split('\\')[-1].split('.')[0].split('/')
            for mt in missing_tile:
                if int(mt) < 0:
                    return
            append_tile_to_queue(missing_tile)
            # message_404 = f'File with path: {file_path}'
            # self.wfile.write(message_404.encode('utf-8'))

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, host="localhost", port=1234, directory="."):
    SimpleHTTPRequestHandler.directory = directory
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on {host}:{port}, serving files from directory: {directory}")
    httpd.serve_forever()

if __name__ == "__main__":
    # Check command-line arguments
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = "localhost"
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    else:
        port = 8000
    if len(sys.argv) > 3:
        directory = sys.argv[3]
    else:
        directory = "."
    run(host=host, port=port, directory=directory)

# python map_server.py localhost 1234 ../map_tiles/ESRI