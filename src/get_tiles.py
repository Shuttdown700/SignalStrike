import argparse
import json
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional, Tuple, Union

from colorama import init, Fore, Style
import shapely
import shapely.geometry
import shapely.ops
import tiletanic
from pyproj import Transformer


def parse_arguments() -> Dict[str, Union[str, Tuple[float, ...], int, bool]]:
    """Parse and validate command-line arguments for the XYZ tile downloader.

    Returns:
        Dictionary containing validated arguments.

    Raises:
        ValueError: If neither extent nor geojson is provided.
    """
    parser = argparse.ArgumentParser(description="XYZ tile download tool")
    parser.add_argument("tile_url", help="XYZ tile URL in {z}/{x}/{y} template")
    parser.add_argument("output_dir", help="Output directory for downloaded tiles")
    parser.add_argument(
        "--extent",
        help="Geographic extent: min_lon min_lat max_lon max_lat (whitespace delimited)",
        nargs=4,
        type=float,
    )
    parser.add_argument(
        "--geojson",
        help="Path to GeoJSON file (Feature or FeatureCollection)",
    )
    parser.add_argument(
        "--minzoom",
        default=0,
        type=int,
        help="Minimum zoom level (default: 0)",
    )
    parser.add_argument(
        "--maxzoom",
        default=16,
        type=int,
        help="Maximum zoom level (default: 16)",
    )
    parser.add_argument(
        "--interval",
        default=100,
        type=int,
        help="Delay between requests in milliseconds (default: 100)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files",
    )
    parser.add_argument(
        "--timeout",
        default=5,
        type=int,
        help="Request timeout in seconds (default: 5)",
    )
    parser.add_argument(
        "--parallel",
        default=1,
        type=int,
        help="Number of parallel requests (default: 1)",
    )
    parser.add_argument(
        "--tms",
        action="store_true",
        help="Parse z/x/y as TMS (Tile Map Service)",
    )

    args = parser.parse_args()

    if args.extent is None and args.geojson is None:
        raise ValueError("Either --extent or --geojson must be provided")

    verified_args = {
        "tile_url": args.tile_url,
        "output_dir": args.output_dir,
        "extent": tuple(args.extent) if args.extent else None,
        "geojson": args.geojson,
        "minzoom": args.minzoom,
        "maxzoom": args.maxzoom,
        "interval": args.interval,
        "overwrite": args.overwrite,
        "timeout": args.timeout,
        "parallel": args.parallel,
        "tms": args.tms,
    }

    return verified_args


def get_geometry(args: Dict) -> shapely.geometry.base.BaseGeometry:
    """Convert extent or GeoJSON input to a Shapely geometry.

    Args:
        args: Dictionary of parsed arguments.

    Returns:
        Shapely geometry object.

    Raises:
        FileNotFoundError: If GeoJSON file doesn't exist.
        ValueError: If GeoJSON content is invalid.
    """
    if args["extent"]:
        min_lon, min_lat, max_lon, max_lat = args["extent"]
        geometry = shapely.geometry.Polygon([
            (min_lon, min_lat),
            (max_lon, min_lat),
            (max_lon, max_lat),
            (min_lon, max_lat),
            (min_lon, min_lat),
        ])
    else:
        try:
            with open(args["geojson"], "r") as f:
                geojson = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"GeoJSON file not found: {args['geojson']}")

        if "features" in geojson:
            geometries = [
                shapely.geometry.shape(feature["geometry"])
                for feature in geojson["features"]
            ]
            geometry = shapely.ops.unary_union(geometries)
        else:
            geometry = shapely.geometry.shape(geojson["geometry"])

    return geometry


def download_tile(tile: Tuple[int, int, int], 
                  args: Dict
                  ) -> None:
    """Download a single tile and save it to the output directory.

    Args:
        tile: Tuple of (x, y, zoom) coordinates.
        args: Dictionary of parsed arguments.
    """
    tile_x, tile_y, zoom = tile
    base_path = args["tile_url"].split("?")[0].split("/")[-1]
    extension = f".{base_path.split('.')[-1]}" if "." in base_path else ".png"

    write_dir = os.path.join(args["output_dir"], str(zoom), str(tile_x))
    write_filepath = os.path.join(write_dir, f"{tile_y}{extension}")
    map_name = write_dir.split(os.sep)[-3]

    if os.path.exists(write_filepath) and not args["overwrite"]:
        print(f"{Fore.YELLOW}{Style.BRIGHT}Skipping{Style.RESET_ALL}: {map_name}/{zoom}/{tile_x}/{tile_y}{extension} already exists")
        return True

    url = args["tile_url"].format(x=tile_x, y=tile_y, z=zoom)

    try:
        with urllib.request.urlopen(url, timeout=args["timeout"]) as response:
            print(f"{Fore.GREEN}{Style.BRIGHT}Downloading{Style.RESET_ALL}: {map_name}/{zoom}/{tile_x}/{tile_y}{extension}")
            os.makedirs(write_dir, exist_ok=True)
            with open(write_filepath, "wb") as f:
                f.write(response.read())
        time.sleep(args["interval"] / 1000)
    except urllib.error.HTTPError as e:
        print(f"{Fore.RED}{Style.BRIGHT}HTTP Error{Style.RESET_ALL}: {e} for URL: {url}")
        return False
    except Exception as e:
        if "timeout" in str(e).lower():
            print(f"{Fore.YELLOW}{Style.BRIGHT}Timeout, retrying{Style.RESET_ALL}: {url}")
        else:
            print(f"{Fore.RED}{Style.BRIGHT}Error{Style.RESET_ALL}: {e} for URL: {url}")
        return False


def main() -> None:
    """Main function to download XYZ tiles based on provided arguments."""
    args = parse_arguments()
    num_tiles = 0

    # Get geometry and transform to EPSG:3857
    geometry = get_geometry(args)
    transformer = Transformer.from_crs(4326, 3857, always_xy=True)
    geom_3857 = shapely.ops.transform(transformer.transform, geometry)

    # Set up tile scheme
    tile_scheme = (
        tiletanic.tileschemes.WebMercatorBL() if args["tms"]
        else tiletanic.tileschemes.WebMercator()
    )

    # Download tiles
    with ThreadPoolExecutor(max_workers=args["parallel"]) as executor:
        for zoom in range(args["minzoom"], args["maxzoom"] + 1):
            tile_generator = tiletanic.tilecover.cover_geometry(
                tile_scheme, geom_3857, zoom
            )
            for tile in tile_generator:
                future = executor.submit(download_tile, tile, args)
                num_tiles += 1
                if future.exception():
                    print(f"{Fore.RED}{Style.BRIGHT}Error downloading tile{Style.RESET_ALL}: {future.exception()}")

    print(f"{Fore.GREEN}{Style.BRIGHT}Download completed{Style.RESET_ALL}: {num_tiles:,} tiles")


if __name__ == "__main__":
    main()