import os
from datetime import datetime

import rasterio

from coords import (
    adjust_coordinate,
    get_distance_between_coords,
    get_bearing_between_coordinates,
    convert_coords_to_mgrs,
    format_readable_mgrs,
)


def get_dted_file(lat: float, lon: float) -> str:
    """Constructs the DTED file path based on latitude and longitude."""
    lat_dir = f'n{int(lat):02d}' if lat >= 0 else f's{abs(int(lat)):02d}'
    lon_dir = f'e{int(lon):03d}' if lon >= 0 else f'w{abs(int(lon)):03d}'
    dted_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "dted"
    )
    file_path = os.path.join(dted_dir, lon_dir, f"{lat_dir}.dt2")
    return file_path


def get_elevation(coord: list[float]) -> float:
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
            row, col = dted.index(lon, lat)
            elevation = dted.read(1)[row, col]
    except Exception as e:
        raise RuntimeError(f"Error reading elevation data: {e}")

    return elevation


def generate_coordinates_of_interest(
    sensor_coord: list[float],
    target_coord: list[float],
    farside_target_distance_km: float
) -> list[float]:
    farside_target_distance_m = farside_target_distance_km * 1000
    offset_distance_m = farside_target_distance_m * 0.2
    bearing = get_bearing_between_coordinates(sensor_coord, target_coord)
    farside_coord = adjust_coordinate(
        sensor_coord,
        bearing,
        farside_target_distance_m + offset_distance_m
    )
    return farside_coord


def get_elevation_profile(
    start: list[float],
    end: list[float],
    interpoint_distance_m: int = 30
) -> list[tuple[float, float, int, float]]:
    """Returns a list of elevations along a line between two points."""
    assert isinstance(start, list) and len(start) == 2
    assert isinstance(end, list) and len(end) == 2
    assert isinstance(interpoint_distance_m, int) and interpoint_distance_m > 0

    lat1, lon1 = start
    lat2, lon2 = end

    assert -90 <= lat1 <= 90 and -90 <= lat2 <= 90
    assert -180 <= lon1 <= 180 and -180 <= lon2 <= 180

    max_points = 50
    file_path1 = get_dted_file(lat1, lon1)
    file_path2 = get_dted_file(lat2, lon2)

    if not os.path.exists(file_path1):
        raise FileNotFoundError(f"DTED file not found: {file_path1}")
    if not os.path.exists(file_path2):
        raise FileNotFoundError(f"DTED file not found: {file_path2}")

    num_points = int(get_distance_between_coords(start, end, 'm') / interpoint_distance_m)
    num_points = min(num_points, max_points)

    try:
        lats = [lat1 + (lat2 - lat1) * i / num_points for i in range(num_points)]
        lons = [lon1 + (lon2 - lon1) * i / num_points for i in range(num_points)]
        elevation_data = []

        for lat, lon in zip(lats, lons):
            elevation = get_elevation([lat, lon])
            distance_km = get_distance_between_coords(start, [lat, lon], 'km')
            elevation_data.append((lat, lon, int(elevation), distance_km))
    except Exception as e:
        raise RuntimeError(f"Error reading elevation data: {e}")

    return elevation_data


def get_elevation_plot_filename(target_class: str = "LOB") -> str:
    date_str = datetime.now().strftime('%Y-%m-%d')
    logs_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'logs', 'elevation_plots', date_str)
    )
    os.makedirs(logs_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Hh%Mm%Ss')
    base_name = f"{target_class}_elevation-plot_{date_str}_{timestamp}"

    counter = 0
    filename = os.path.join(logs_dir, f"{base_name}.png")
    while os.path.exists(filename):
        counter += 1
        filename = os.path.join(logs_dir, f"{base_name}_{counter}.png")

    return filename


def plot_elevation_profile(
    elevation_data: list[tuple[float, float, int, float]],
    sensor_coord: list[float],
    nearside_target_distance_km: float,
    target_coord: list[float],
    farside_target_distance_km: float
) -> None:
    """Plots the elevation profile with visual enhancements."""
    import matplotlib.pyplot as plt
    import numpy as np
    from utilities import generate_DTG

    elevations = [e[2] for e in elevation_data]
    distances = [e[3] for e in elevation_data]

    distances = np.array(distances)
    elevations = np.array(elevations)

    target_distance = get_distance_between_coords(sensor_coord, target_coord, 'km')

    dtg = generate_DTG()
    date_str = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%H%ML')
    plot_title = f"LOB Target Elevation Profile | {date_str} at {timestamp}"

    fig, ax = plt.subplots()
    ax.plot(distances, elevations, color="black", label="Elevation Profile")

    ax.plot(distances[0], elevations[0], 'bo', label="Sensor Position")

    target_elevation = get_elevation(target_coord)
    formatted_mgrs = format_readable_mgrs(convert_coords_to_mgrs(target_coord))
    ax.plot(target_distance, target_elevation, 'ro', label="Est. Target Location")

    ax.annotate(
        f"MGRS: {formatted_mgrs}",
        xy=(target_distance, target_elevation),
        xytext=(10, 10),
        textcoords="offset points",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.9),
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
        fontsize=9
    )

    y_min = max(0, min(elevations) - 100)
    y_max = max(elevations) + 100
    ax.set_ylim(y_min, y_max)
    ax.set_xlim(min(distances), max(distances))

    ax.fill_between(distances, elevations, y_min, color='#d2b48c', alpha=0.5)
    ax.fill_between(distances, elevations, y_max, color='#add8e6', alpha=0.3)

    in_target_zone = (
        (distances >= nearside_target_distance_km) &
        (distances <= farside_target_distance_km)
    )
    ax.fill_between(
        distances[in_target_zone],
        elevations[in_target_zone],
        y_max,
        color='lightcoral',
        alpha=0.3,
        label="Target Area of Error"
    )

    ax.set_xlabel("Distance (km) from Sensor")
    ax.set_ylabel("Elevation (m) AMSL")
    ax.set_title(plot_title)
    ax.legend(loc='upper left')
    plt.tight_layout()
    save_path = get_elevation_plot_filename()
    plt.savefig(save_path)
    plt.show()
    plt.close()
