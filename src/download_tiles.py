
def get_coord_box(center_coord,x_dist_m,y_dist_m):
    """
    Generate a coordinate box for the tile downloader.

    Parameters
    ----------
    center_coord : list
        Coordinate in [lat,lon] format
    x_dist_m : float
        Distance from center to box edge along x-axis in meters
    y_dist_m : float
        Distance from center to box edge along y-axis in meters

    Returns
    -------
    str
        Coodinate string in "min_lon, min_lat, max_lon, max_lat" format.

    """
    from main import adjust_coordinate
    import numpy as np
    diag_dist = np.sqrt(x_dist_m**2 + y_dist_m**2)
    tl_coord = adjust_coordinate(center_coord,315,diag_dist)
    br_coord = adjust_coordinate(center_coord,135,diag_dist)
    return f"{tl_coord[1]},{br_coord[0]},{br_coord[1]},{tl_coord[0]}"

import os
src_directory = os.path.dirname(os.path.abspath(__file__))
tile_dir = "\\".join(src_directory.split('\\')[:-1])+"\\maptiles\\ESRI"
get_tiles_file = os.path.join(src_directory, "get_tiles.py")
tile_url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png'

ntc_bbox = "-117.864075,35.056980,-115.996399,36.140093"
ntc_small_bbox = '-116.774368,35.376734,-116.366501,35.570215'
zagan_bbox = "15.205078,51.550546,15.439911,51.664769"
jmrc_bbox = "11.651001,49.207953,11.927376,49.350625"
fsga_bbox = "-81.933975,31.832649,-81.270676,32.113404"
boles_coords = [51.26070109979971, 15.567760588806994]
bpta_coords = [53.73721459690141, 22.05693866784293]
bbox = "-117.148590,35.288227,-116.341095,35.636093" # min_lon, min_lat, max_lon, max_lat
boles_bbox = get_coord_box(boles_coords,8500,8500)
bpta_bbox = get_coord_box(bpta_coords,3000,3000)
min_zoom = 0
max_zoom = 18
parallel_threads = 4
cmd = f'python3 "{get_tiles_file}" "{tile_url}" "{tile_dir}" --extent {bpta_bbox.replace(","," ")} --minzoom {min_zoom} --maxzoom {max_zoom} --parallel {parallel_threads}'
print(cmd)
# import subprocess
# subprocess.call(cmd, shell=True, stdout=subprocess.PIPE)

