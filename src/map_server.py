from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from utilities import read_csv, write_csv
import os, sys

def append_tile_to_queue(map_name,tile,file_path=os.path.dirname(os.path.abspath(__file__))+"\\queue_files\\dynamic_tile_queue.csv"):
    """Appends tile row to queue csv file."""
    # end function if tile to append is blank
    if tile == "" or tile == []: return
    # open csv file
    if not os.path.isfile(file_path): 
        with open(file_path, mode='w', newline=''):
            print("Creating batch queue file...\n")
    tile_data = {
                "Map":map_name,
                "Z":tile[0],
                 "Y":tile[2],
                 "X":tile[1]
                 }
    # for tkintermapview, tile segment order is Z, X, Y !!!
    # print('Tile Data: ',tile_data)
    queue_data = read_csv(file_path)
    queue_data.append(tile_data)
    write_csv(file_path,queue_data)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        # remove leading slash to get the file path
        if path.startswith("/"):
            path = path[1:]
        # check if the file exists within the specified directory
        file_path = os.path.join(SimpleHTTPRequestHandler.directory, path)
        print(file_path)
        # check if requested filepath exists
        if os.path.exists(file_path) and os.path.isfile(file_path):
            # open and read the requested file
            with open(file_path, 'rb') as file:
                content = file.read()
            # send HTTP OK response
            self.send_response(200)
            # set content header request
            self.send_header('Content-type', 'application/octet-stream')
            # send end content header
            self.end_headers()
            # send requested file as HTTP content
            self.wfile.write(content)
        else:
            # send HTTP Bad Request response
            self.send_response(404)
            # send end content header
            self.end_headers()
            # identify missing tile from request
            missing_tile = file_path.split('\\')[-1].split('.')[0].split('/')
            # loop through missing tile to verify components
            if len(missing_tile) > 3:
                map_name = missing_tile[0]
                missing_tile = missing_tile[-3:]
            for mt in missing_tile:
                # check if tile component is less than zero / invalid
                if int(mt) < 0:
                    # end function
                    return
            # append missing tile to missing tile queue
            append_tile_to_queue(map_name,missing_tile)

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, host="localhost", port=1234, directory="."):
    """
    Run HTTP Map Tile Server with dynamic missing tile identifer

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
    # set base directory
    SimpleHTTPRequestHandler.directory = directory
    # set server network attributes
    server_address = (host, port)
    # set HTTP server structure
    httpd = server_class(server_address, handler_class)
    # display that HTTP server is operational
    print(f"Server running on {host}:{port}, serving files from directory: {directory}")
    # start HTTP server
    httpd.serve_forever()

if __name__ == "__main__":
    # checks for command-line arguments and set defaults, as required
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
    # initiates map server
    run(host=host, port=port, directory=directory)

# example CLI command
# python map_server.py localhost 1234 ../map_tiles/ESRI