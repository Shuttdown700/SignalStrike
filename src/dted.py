import os
import rasterio

def get_dted_file(lat: float, lon: float) -> str:
    """Constructs the DTED file path based on latitude and longitude."""
    lat_dir = f'n{int(lat):02d}' if lat >= 0 else f's{abs(int(lat)):02d}'
    lon_dir = f'e{int(lon):03d}' if lon >= 0 else f'w{abs(int(lon)):03d}'
    dted_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","dted")
    file_path = os.path.join(dted_dir, lon_dir, f"{lat_dir}.dt2")
    return file_path

def get_elevation(coord: list) -> float:
    """Returns the elevation for a given coordinate from the DTED files."""
    assert isinstance(coord, list) and len(coord) == 2, "Coordinate must be a list of two floats."
    lat, lon = coord
    assert isinstance(lat, (int, float)) and isinstance(lon, (int, float)), "Latitude and Longitude must be numeric values."
    assert -90 <= lat <= 90, "Latitude must be between -90 and 90 degrees."
    assert -180 <= lon <= 180, "Longitude must be between -180 and 180 degrees."
    file_path = get_dted_file(lat, lon)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"DTED file not found: {file_path}")
    
    try:
        with rasterio.open(file_path) as dted:
            row, col = dted.index(lon, lat)  # Rasterio uses (longitude, latitude)
            elevation = dted.read(1)[row, col]
    except Exception as e:
        raise RuntimeError(f"Error reading elevation data: {e}")
    
    return elevation
