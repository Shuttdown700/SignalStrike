from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path
from typing import List, Dict, Optional
import sys
import os
import logging
from logger import LoggerManager
from utilities import read_csv, write_csv

class MapRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for map tile server with logging."""
    def log_message(self, format, *args):
        pass
    map_server: Optional['MapServer'] = None  # Class-level attribute to hold MapServer instance

    def do_GET(self) -> None:
        """Handle GET requests for map tiles, logging requests and missing tiles."""
        if not self.map_server:
            raise RuntimeError("MapServer instance not set")
        
        logger = self.map_server.logger
        parsed_url = urlparse(self.path)
        path = parsed_url.path.lstrip('/')
        file_path = self.map_server.directory / path
               
        try:
            if file_path.exists() and file_path.is_file():
                with file_path.open('rb') as file:
                    content = file.read()
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.end_headers()
                logger.warning(f"Map Tile not found: {path}")
                
                # Extract map name and tile from path
                parts = path.split('/')
                logger.debug(f"Path parts: {parts}")
                
                # Remove the file extension (e.g., .png)
                if parts and '.' in parts[-1]:
                    parts[-1] = parts[-1].split('.')[0]
                
                # Ensure at least 3 parts for tile coordinates
                if len(parts) < 3:
                    logger.error(f"Invalid tile path format, need at least 3 components: {path}")
                    return
                
                # Extract tile (last 3 parts) and map name (first part if more than 3 parts)
                tile = parts[-3:]
                map_name = parts[0] if len(parts) > 3 else 'default'
                
                try:
                    tile = [int(t) for t in tile]
                    if any(t < 0 for t in tile):
                        return
                    self.map_server.append_tile_to_queue(map_name, tile)
                    logger.info(f"Queued missing tile for dynamic download: {map_name}, {tile}")
                except ValueError as e:
                    logger.error(f"Failed to parse tile coordinates {tile}: {str(e)}")
        
        except (IOError, OSError) as e:
            self.send_response(500)
            self.end_headers()
            logger.error(f"Error processing request for {path}: {str(e)}")

class MapServer:
    """HTTP map tile server with dynamic missing tile queue and logging."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 1234,
        directory: str = os.path.dirname(os.path.abspath(__file__)),
        queue_file: str = "dynamic_tile_queue.csv"
    ) -> None:
        """
        Initialize the map server.
        
        Args:
            host (str): Server address (default: "localhost").
            port (int): Server port (default: 1234).
            directory (str): Base directory for serving files (default: ".").
            queue_file (str): Path to tile queue CSV file (default: "queue_files/dynamic_tile_queue.csv").
        """
        self.host = host
        self.port = port
        self.directory = Path(directory).resolve()
        # Set queue_file relative to map_server.py in ./queue_files
        self.queue_file = Path(__file__).parent / "queue_files" / queue_file
        self.logger = LoggerManager.get_logger(
            name="map_server",
            category="map_server",
            level=logging.INFO
        )
        self.logger.info(f"Initializing server at {host}:{port}, directory: ./{os.path.basename(os.path.normpath(self.directory))}")

    def append_tile_to_queue(self, map_name: str, tile: List[int]) -> None:
        """
        Append a tile to the queue CSV file.
        
        Args:
            map_name (str): Name of the map.
            tile (List[int]): Tile coordinates [Z, X, Y].
        """
        if not tile or not all(isinstance(t, int) for t in tile):
            self.logger.warning(f"Invalid or empty tile: {tile}")
            return

        tile_data = {
            "Map": map_name,
            "Z": tile[0],
            "X": tile[1],
            "Y": tile[2]
        }
        
        try:
            if not self.queue_file.exists():
                self.queue_file.parent.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created queue file directory: {self.queue_file.parent}")
            
            queue_data = read_csv(self.queue_file) if self.queue_file.exists() else []
            queue_data.append(tile_data)
            write_csv(self.queue_file, queue_data)
        
        except (IOError, OSError) as e:
            self.logger.error(f"Failed to append tile to queue: {str(e)}")

    def run(self) -> None:
        """Start the HTTP map tile server."""
        try:
            server_address = (self.host, self.port)
            # Create a new handler class with map_server set
            handler_class = type(
                'MapRequestHandler',
                (MapRequestHandler,),
                {'map_server': self}
            )
            httpd = HTTPServer(server_address, handler_class)
            self.logger.info(f"Server running on {self.host}:{self.port}, serving files from: ./{os.path.basename(os.path.normpath(self.directory))}")
            httpd.serve_forever()
        
        except Exception as e:
            self.logger.error(f"Server failed to start: {str(e)}")
            raise

    def shutdown(self) -> None:
        """Clean up resources and close logger."""
        self.logger.info("Shutting down server")
        LoggerManager.clear_cache()

if __name__ == "__main__":
    # Parse command-line arguments
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 1234
    directory = sys.argv[3] if len(sys.argv) > 3 else "."
    
    # Start the server
    server = MapServer(host=host, port=port, directory=directory)
    try:
        server.run()
    except KeyboardInterrupt:
        server.shutdown()