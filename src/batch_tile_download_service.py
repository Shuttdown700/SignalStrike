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

def batch_map_tile_download_service():
    map_tile_directory = "\\".join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1])+"\\map_tiles\\ESRI"
    min_map_tile_size_kb = 3
    delete_small_files_and_empty_dirs(map_tile_directory, min_map_tile_size_kb)  # Change this to your directory path
    print('Starting Batch Tile Download Service:\n')
    queue_file_name = os.path.dirname(os.path.abspath(__file__))+"\\queue_files\\batch_tile_queue.csv"
    if not os.path.isfile(queue_file_name): 
        with open(queue_file_name, mode='w', newline='') as file:
            print("Creating batch queue file...\n")    
    wait_interval_sec = 10
    offline_indicator = 0
    time.sleep(2)
    while True:
        cmd_complete_list = []
        t1 = datetime.datetime.today()
        try:
            cmd_queue = read_csv(queue_file_name)
        except Exception as e:
            print(f'Error reading batch queue file: {e}',end='\n')
            time.sleep(5)
            continue
        if not check_internet_connection():
            time.sleep(5)
            if not check_internet_connection(): print('No public internet connection... terminating service'); break
        if len(cmd_queue) > 0:
            for cmd in cmd_queue:
                command = cmd[0]
                print(f'Executing the following command:\n\n{command}')
                subprocess.run(command, shell=True, start_new_session=True)
                cmd_complete_list.append(cmd)
            cmd_queue = read_csv(queue_file_name)
            cmd_queue_updated = []
            for cmd in cmd_queue:
                if cmd in cmd_complete_list:
                    continue
                else:
                    cmd_queue_updated.append({'Command':cmd})
            write_csv(queue_file_name,cmd_queue_updated)
        else:
            print('Batch download queue is empty.\n')
        t2 = datetime.datetime.today()
        t_delta = t1 - t2
        if t_delta.total_seconds() < wait_interval_sec:
            print(f'Waiting: {wait_interval_sec - t_delta.total_seconds():,.2f} seconds...',end='\n')
            time.sleep(min(wait_interval_sec - t_delta.total_seconds(),wait_interval_sec))
            wait_interval_sec = 100
        else:
            time.sleep(1)    

if __name__ != "__main__":
    # JMRC
    # lat_lon_top_left = [49.346879624602245, 11.659812747253916]
    # lat_lon_bottom_right = [49.18337189700959, 11.938263364917287]
    # Zagan
    # lat_lon_top_left = [51.67628616890177, 15.211444049242113]
    # lat_lon_bottom_right = [51.36010942835179, 15.607117958891969]
    map_tile_directory = "\\".join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1])+"\\map_tiles\\ESRI"
    min_map_tile_size_kb = 3
    delete_small_files_and_empty_dirs(map_tile_directory, min_map_tile_size_kb)  # Change this to your directory path
    download_tile_batch([49.346879624602245, 11.659812747253916],[49.18337189700959, 11.938263364917287])


time.sleep(5)

"""
Re-design:

CLI-based

arguement optional, with hard-coded defaults


"""