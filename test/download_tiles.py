import os

if __name__ == "__main__":
    src_directory = "\\".join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1])+'/src/'
    os.chdir(src_directory)
    from main import get_coord_box
    tile_dir = "\\".join(src_directory.split('\\')[:-1])+"\\map_tiles\\ESRI"
    get_tiles_file = os.path.join(src_directory, "get_tiles.py")
    tile_url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png'
    coords = [51.26070109979971, 15.567760588806994]
    # bbox = "-117.148590,35.288227,-116.341095,35.636093" # min_lon, min_lat, max_lon, max_lat
    bbox = get_coord_box(coords,8500,8500)
    min_zoom = 0
    max_zoom = 18
    parallel_threads = 4
    cmd = f'python "{get_tiles_file}" "{tile_url}" "{tile_dir}" --extent {bbox.replace(","," ")} --minzoom {min_zoom} --maxzoom {max_zoom} --parallel {parallel_threads}'
    # print(cmd)
    import subprocess    
    # subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    subprocess.call(cmd, shell=True)

