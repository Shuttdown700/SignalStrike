import datetime, logging, os, subprocess, time
from utilities import check_internet_connection, read_csv, write_csv

def delete_small_files_and_empty_dirs(directory: str, size_limit_kb: float, dry_run=False) -> None:
    # Convert size limit from kilobytes to bytes
    size_limit_bytes = size_limit_kb * 1024
    # Check if the provided directory exists
    if not os.path.isdir(directory):
        print(f"The directory '{directory}' does not exist.")
        return
    # Set up logging
    src_directory = os.path.dirname(os.path.abspath(__file__))
    log_directory = "\\".join(src_directory.split('\\')[:-1])+"\\logs"
    filepath_log = os.path.join(log_directory,'deleted_files_and_dirs.log')
    logging.basicConfig(filename=filepath_log, level=logging.INFO, format='%(asctime)s - %(message)s')
    # First directory walk: Delete small files
    for root, dirs, files in os.walk(directory, topdown=False):
        for filename in files:
            file_path = os.path.join(root, filename)
            # Get the size of the file
            file_size = os.path.getsize(file_path)
            # Check if the file size is less than the specified limit
            if file_size < size_limit_bytes:
                if dry_run:
                    print(f"Would delete '{file_path}' (size: {file_size} bytes)")
                else:
                    # Delete the file
                    os.remove(file_path)
                    logging.info(f"Deleted file '{file_path}' (size: {file_size} bytes)")
                    print(f"Deleted file '{file_path}' (size: {file_size} bytes)")
            else:
                continue
    # Second directory walk: Delete empty directories
    for root, dirs, files in os.walk(directory, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):  # Check if the directory is empty
                if dry_run:
                    print(f"Would delete empty directory '{dir_path}'")
                else:
                    # Delete the empty directory
                    os.rmdir(dir_path)
                    logging.info(f"Deleted empty directory '{dir_path}'")
                    print(f"Deleted empty directory '{dir_path}'")

def download_tile_batch(
        lat_lon_top_left:list[float],
        lat_lon_bottom_right:list[float],
        tile_directory:str = "",
        tile_url: str = "https://tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey=8242f8cd508342868f3d7d29e472aca9",
        min_zoom: int = 0,
        max_zoom: int = 18,
        parallel_threads: int = 4
):
    # input variable assertations
    try:
        assert isinstance(lat_lon_top_left, list), "'lat_lon_top_left' must be a list."
        assert len(lat_lon_top_left) == 2, "'lat_lon_top_left' list must contain exactly two elements."
        assert all(isinstance(item, float) for item in lat_lon_top_left), "All elements in the 'lat_lon_top_left' list must be floats."
        assert isinstance(lat_lon_bottom_right, list), "'lat_lon_bottom_right' must be a list."
        assert len(lat_lon_bottom_right) == 2, "'lat_lon_bottom_right' list must contain exactly two elements."
        assert all(isinstance(item, float) for item in lat_lon_bottom_right), "All elements in the 'lat_lon_bottom_right' list must be floats."
    except AssertionError as ae:
        print(f'Error with batch tile download function inputs: {ae}')
        return
    src_directory = os.path.dirname(os.path.abspath(__file__))
    if tile_directory == "":
        tile_directory = "\\".join(src_directory.split('\\')[:-1])+"\\map_tiles\\Terrain"
    get_tiles_file = os.path.join(src_directory, "get_tiles.py")
    coord_bbox = [lat_lon_top_left[1],lat_lon_bottom_right[0],lat_lon_bottom_right[1],lat_lon_top_left[0]]
    cmd = f'python "{get_tiles_file}" "{tile_url}" "{tile_directory}" --extent {coord_bbox[0]} {coord_bbox[1]} {coord_bbox[2]} {coord_bbox[3]} --minzoom {min_zoom} --maxzoom {max_zoom} --parallel {parallel_threads}'
    print(f'Executing the following command:\n\n{cmd}\n')
    subprocess.run(cmd, shell=True, start_new_session=True)

if __name__ == "__main__":
    # lat_lon_top_left_jmrc = [49.346879624602245, 11.659812747253916]
    # lat_lon_bottom_right_jmrc = [49.18337189700959, 11.938263364917287]
    # lat_lon_top_left_zagan = [51.67628616890177, 15.211444049242113]
    # lat_lon_bottom_right_zagan = [51.36010942835179, 15.607117958891969]
    # lat_lon_top_left_fsga = [32.17298556737781, -81.92483248818199]
    # lat_lon_bottom_right_fsga = [31.844968894681053, -81.34921614575053]
    lat_lon_top_left_ntc = [35.51647615855687, -116.85645436651438]
    lat_lon_bottom_right_ntc = [35.18817526937803, -116.3086324976313]

    # https://tile.tracestrack.com/topo_en/{z}/{x}/{y}.png?key=ed9a1d727da81b743cec066617572751&style=contrast-
    # https://opentopomap.org/#map=13/35.32661/-116.54657
    # https://tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey=8242f8cd508342868f3d7d29e472aca9

    from utilities import read_json
    conf = read_json(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config_files","conf.json"))
    queue_file_name = os.path.join("\\".join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1]),conf["DIR_RELATIVE_QUEUE"],"dynamic_tile_queue.csv")
    output_dir= os.path.join("\\".join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1]),conf["DIR_RELATIVE_MAP_TILES"])


    map_tile_directory = os.path.join(output_dir,"Terrain")
    min_map_tile_size_kb = 3
    # delete_small_files_and_empty_dirs(map_tile_directory, min_map_tile_size_kb,dry_run=True)  # Change this to your directory path
    download_tile_batch(lat_lon_top_left_ntc,lat_lon_bottom_right_ntc,map_tile_directory)


time.sleep(5)

"""
Re-design:

CLI-based

arguement optional, with hard-coded defaults

default options presented

Create a config with the various regions

Create an estimate on completion (# complete / # remaining)

add color

create another file or function to facilitate the copying of map data to storage devices

"""

# xcopy "C:\Users\brend\Documents\Coding Projects\ew_plt_targeting_app\map_tiles" "S:\Coding Projects" /s /e /d