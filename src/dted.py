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

def get_elevation_profile(start: list, end: list, num_points: int = 100) -> list:
    """Returns a list of elevations along a line between two points."""
    assert isinstance(start, list) and len(start) == 2, "Start coordinate must be a list of two floats."
    assert isinstance(end, list) and len(end) == 2, "End coordinate must be a list of two floats."
    assert isinstance(num_points, int) and num_points > 0, "Number of points must be a positive integer."
    lat1, lon1 = start
    lat2, lon2 = end
    assert -90 <= lat1 <= 90 and -90 <= lat2 <= 90, "Latitude must be between -90 and 90 degrees."
    assert -180 <= lon1 <= 180 and -180 <= lon2 <= 180, "Longitude must be between -180 and 180 degrees."
    
    file_path1 = get_dted_file(lat1, lon1)
    file_path2 = get_dted_file(lat2, lon2)
    
    if not os.path.exists(file_path1):
        raise FileNotFoundError(f"DTED file not found: {file_path1}")
    if not os.path.exists(file_path2):
        raise FileNotFoundError(f"DTED file not found: {file_path2}")
    
    try:
        with rasterio.open(file_path1) as dted1, rasterio.open(file_path2) as dted2:
            lats = [lat1 + (lat2 - lat1) * i / num_points for i in range(num_points)]
            lons = [lon1 + (lon2 - lon1) * i / num_points for i in range(num_points)]
            elevations = []
            for lat, lon in zip(lats, lons):
                elevation = get_elevation([lat, lon])
                elevations.append(elevation)
    except Exception as e:
        raise RuntimeError(f"Error reading elevation data: {e}")
    return elevations

def plot_elevation_profile(elevations : list):
    """Plots the elevation profile."""
    import matplotlib.pyplot as plt
    plt.plot(elevations)
    plt.xlabel("Distance (m)")
    plt.ylabel("Elevation (m)")
    plt.title("Elevation Profile")
    plt.show()

if __name__ == "__main__":
    # Example usage of the DTED functions
    coord1 = [49.24818881153634, 11.8154842917353]
    coord2 = [49.22891111693264, 11.84535337003443]
    elevations = get_elevation_profile(coord1, coord2, num_points=10)
    print(f"Elevation profile between {coord1} and {coord2}: {elevations}")
    plot_elevation_profile(elevations)