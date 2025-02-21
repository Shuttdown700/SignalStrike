import logging
import os
import subprocess

# ANSI color codes
RESET = "\033[0m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"

def delete_small_files_and_empty_dirs(directory: str, size_limit_kb: float, dry_run=False) -> None:
    # Convert size limit from kilobytes to bytes
    size_limit_bytes = size_limit_kb * 1024
    # Check if the provided directory exists
    if not os.path.isdir(directory):
        print(f"{RED}The following directory does not exist: {directory}{RESET}")
        return
    # Set up logging
    src_directory = os.path.dirname(os.path.abspath(__file__))
    log_directory = os.path.join(src_directory,"..","logs")
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
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
        tile_directory:str = "terrain",
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
        assert isinstance(tile_directory, str), "'tile_directory' must be a string."
        assert isinstance(tile_url, str), "'tile_url' must be a string."
        assert isinstance(min_zoom, int)   and 0 <= max_zoom <= max_zoom, "'min_zoom' must be an integer. [0-20]"
        assert isinstance(max_zoom, int)  and min_zoom <= max_zoom <= 20, "'max_zoom' must be an integer. [0-20]"
        assert isinstance(parallel_threads, int) and 1 <= parallel_threads <= 4, "'parallel_threads' must be an integer. [1-4]"
    except AssertionError as ae:
        print(f'{RED}Error with batch tile download function inputs: {ae}{RESET}')
        return
    src_directory = os.path.dirname(os.path.abspath(__file__))
    if tile_directory == "":
        tile_directory = "\\".join(src_directory.split('\\')[:-1])+"\\map_tiles\\Terrain"
    get_tiles_file = os.path.join(src_directory, "get_tiles.py")
    coord_bbox = [lat_lon_top_left[1],lat_lon_bottom_right[0],lat_lon_bottom_right[1],lat_lon_top_left[0]]
    cmd = f'python "{get_tiles_file}" "{tile_url}" "{tile_directory}" --extent {coord_bbox[0]} {coord_bbox[1]} {coord_bbox[2]} {coord_bbox[3]} --minzoom {min_zoom} --maxzoom {max_zoom} --parallel {parallel_threads}'
    print(f'{GREEN}Executing the following command:{RESET}\n\n{cmd}\n')
    subprocess.run(cmd, shell=True, start_new_session=True)
    #delete_small_files_and_empty_dirs(tile_directory, min_map_tile_size_kb=3,dry_run=True)

def main():
    from utilities import read_json
    conf = read_json(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config_files","conf.json"))
    map_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"..",conf["DIR_RELATIVE_MAP_TILES"])
    conf_download_presets = read_json(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config_files","batch_download_presets.json"))
    location_options = list(conf_download_presets["Locations"].keys())
    while True:
        print(f"\n{BLUE}Select a batch download option:{RESET}\n")
        for i,key in enumerate(location_options):
            print(f"{i+1}. {key}")
        print(f"{i+2}. Custom")
        print(f"{RED}0. Exit{RESET}\n")
        choice = input("Enter your choice: ")
        if choice.isdigit():
            choice = int(choice)
            if choice == 0:
                print("Exiting...")
                break
            elif 1 <= choice <= len(location_options):
                response = ""
                while response not in ["y","n"]:
                    map_selection = location_options[choice-1]
                    response = input(f"\n{BLUE}Confirm selection{RESET}:{YELLOW} {map_selection} {RESET}[Y/N] ").lower()
                if response == 'y':
                    response_map_type = "no-response"
                    while response_map_type not in ["terrain","satellite","","blank","t","s"]:
                        response_map_type = input (f"\n{BLUE}Input map type{RESET}:{YELLOW} Terrain [T]{RESET}, {YELLOW}Satellite [S]{RESET}, or {YELLOW}Default [BLANK]{RESET} ").lower()
                    if response_map_type in ["","blank"]:
                        response_map_type = "Terrain"
                    elif response_map_type in ["satellite","Satellite","s","S"]:
                        response_map_type = "EGRI"
                    elif response_map_type in ["terrain","Terrain","t","T"]:
                        response_map_type = "Terrain"
                    print(f"{GREEN}Downloading {YELLOW}{response_map_type}{RESET} map for {YELLOW}{map_selection}{RESET}\n")
                    download_tile_batch(
                        conf_download_presets["Locations"][map_selection]["lat_lon_top_left"],
                        conf_download_presets["Locations"][map_selection]["lat_lon_bottom_right"],
                        os.path.join(map_dir,response_map_type)
                    )
                elif response == 'n':
                    continue
            elif choice == len(location_options)+1:
                print(f"{RED}Custom selection not ready yet{RESET}")
                break
                
            else:
                print(f"{RED}\nInvalid choice. Please enter a number between 1 and {len(location_options)+1}.{RESET}")
        else:
            print(f"{RED}Invalid input. Please enter a number.{RESET}")
    return choice

if __name__ == "__main__":
    main()

"""
    Candidate map tile URLs:
    # https://tile.tracestrack.com/topo_en/{z}/{x}/{y}.png?key=ed9a1d727da81b743cec066617572751&style=contrast-
    # https://opentopomap.org/#map=13/35.32661/-116.54657
    # https://tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey=8242f8cd508342868f3d7d29e472aca9
"""

"""
Re-design:

Create an estimate on completion (# complete / # remaining)

add color

create another file or function to facilitate the copying of map data to storage devices

"""

# xcopy "C:\Users\brend\Documents\Coding Projects\ew_plt_targeting_app\map_tiles" "S:\Coding Projects" /s /e /d