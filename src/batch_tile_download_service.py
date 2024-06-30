import datetime, os, subprocess, time
from utilities import check_internet_connection, read_queue, write_queue

if __name__ == "__main__":
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
            cmd_queue = read_queue(queue_file_name)
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
            cmd_queue = read_queue(queue_file_name)
            cmd_queue_updated = []
            for cmd in cmd_queue:
                if cmd in cmd_complete_list:
                    continue
                else:
                    cmd_queue_updated.append([cmd])
            write_queue(queue_file_name,cmd_queue_updated)
        else:
            print('Batch download queue is empty.\n')
        t2 = datetime.datetime.today()
        t_delta = t1 - t2
        if t_delta.total_seconds() < wait_interval_sec:
            print(f'Waiting: {wait_interval_sec - t_delta.total_seconds():,.2f} seconds...',end='\n')
            time.sleep(wait_interval_sec - t_delta.total_seconds())
            wait_interval_sec = 100
        else:
            time.sleep(1)  
time.sleep(5)