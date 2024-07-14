import datetime, logging, os, subprocess, time
from utilities import check_internet_connection, read_csv, write_csv

def delete_small_files_and_empty_dirs(directory, size_limit_kb, dry_run=False):
    # Convert size limit from kilobytes to bytes
    size_limit_bytes = size_limit_kb * 1024
    
    # Check if the provided directory exists
    if not os.path.isdir(directory):
        print(f"The directory '{directory}' does not exist.")
        return
    
    # Set up logging
    logging.basicConfig(filename='deleted_files_and_dirs.log', level=logging.INFO, format='%(asctime)s - %(message)s')
    
    # First pass: Delete small files
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
    
    # Second pass: Delete empty directories
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
            
if __name__ == "__main__":
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
time.sleep(5)