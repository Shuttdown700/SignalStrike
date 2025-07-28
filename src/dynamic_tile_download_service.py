import datetime
import logging
import os
import ssl
import time
import urllib.request
from typing import Dict, List

from colorama import Fore, init
from logger import LoggerManager
from utilities import check_internet_connection, read_csv, read_json, write_csv
from get_tiles import download_tile

init(autoreset=True)

class TileDownloader:
    """A class to manage downloading map tiles dynamically from a queue."""
    
    # Color constants
    RESET = Fore.RESET
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    
    def __init__(self, config_path: str = "config_files/conf.json"):
        """Initialize the TileDownloader with configuration."""
        self.base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        self.config = self._load_config(config_path)
        self.queue_file = os.path.join(self.base_dir, self.config["DIR_RELATIVE_QUEUE"], "dynamic_tile_queue.csv")
        self.output_dir = os.path.join(self.base_dir, self.config["DIR_RELATIVE_MAP_TILES"])
        self.wait_interval_sec = 10
        self.logger = LoggerManager.get_logger(
                    name="tile_downloader",
                    category="tile_downloader",
                    level=logging.INFO
                )
        self._initialize_queue_file()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_path)
        try:
            return read_json(config_file)
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            raise
    
    def _initialize_queue_file(self) -> None:
        """Create queue file if it doesn't exist."""
        if not os.path.isfile(self.queue_file):
            with open(self.queue_file, mode='w', newline='') as file:
                pass
            self.logger.info(f"Created dynamic queue file.")
    
    def _determine_tile_url(self, map_name: str) -> str:
        """Determine tile URL based on map name."""
        map_urls = {
            'Terrain': self.config["TERRAIN_TILE_URL"],
            'ESRI': self.config["SATELLITE_TILE_URL"]
        }
        if map_name not in map_urls:
            self.logger.error(f"Error: {map_name} is not a valid map type")
            return ""
        return map_urls[map_name]
    
    def _process_queue(self) -> List[Dict]:
        """Process all tiles in the queue and return downloaded tiles."""
        downloaded_tiles = []
        try:
            tile_queue = read_csv(self.queue_file)
        except Exception as e:
            self.logger.error(f"Error reading queue file: {e}")
            return downloaded_tiles
        
        for tile in tile_queue:
            map_name = tile["Map"]
            tile_url = self._determine_tile_url(map_name)
            args = {
                "tile_url": tile_url,
                "output_dir": os.path.join(self.output_dir,map_name),
                "overwrite": False,
                "timeout": 5,
                "interval": 100
            }
            tile_coords = (int(tile["X"]), int(tile["Y"]), int(tile["Z"]))
            if tile_url and download_tile(tile_coords, args):
                downloaded_tiles.append(tile)
        
        return downloaded_tiles
    
    def _update_queue(self, downloaded_tiles: List[Dict]) -> None:
        """Update the queue file by removing downloaded tiles."""
        try:
            tile_queue = read_csv(self.queue_file)
            updated_queue = [tile for tile in tile_queue if tile not in downloaded_tiles]
            write_csv(self.queue_file, updated_queue)
        except Exception as e:
            self.logger.error(f"Error updating queue file: {e}")
    
    def run(self) -> None:
        """Main service loop to continuously process the tile queue."""
        self.logger.info("Starting Dynamic Tile Download Service.")
        time.sleep(2)
        while True:
            try:
                t1 = datetime.datetime.now()
                
                if not check_internet_connection():
                    time.sleep(5)
                    if not check_internet_connection():
                        self.logger.warning("No internet connection. Terminating service.")
                        break
                
                downloaded_tiles = self._process_queue()
                
                if not downloaded_tiles and not read_csv(self.queue_file):
                    pass
                    # print(f"{self.YELLOW}Dynamic download queue is empty.{self.RESET}")
                
                self._update_queue(downloaded_tiles)
                
                t2 = datetime.datetime.now()
                t_delta = (t2 - t1).total_seconds()
                
                if t_delta < self.wait_interval_sec:
                    wait_time = self.wait_interval_sec - t_delta
                    time.sleep(min(wait_time, 10))
                else:
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Exception in main loop: {e}")
                time.sleep(5)
                continue

def main():
    """Entry point for the tile downloader service."""
    downloader = TileDownloader()
    downloader.run()

if __name__ == "__main__":
    main()