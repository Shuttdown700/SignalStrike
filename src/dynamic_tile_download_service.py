import datetime, os, time, ssl
from utilities import check_internet_connection, read_csv, write_csv

def download_tile(tile,
             output_dir="\\".join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1])+'/map_tiles/ESRI/',
             tileurl='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png',
             bool_overwrite=False,
             timeout_num=5,
             interval_num=100):
    import os, time, urllib, urllib.request
    basepath = tileurl.split("/")[-1]  # ?foo=bar&z={z}.ext
    segments = basepath.split(".")
    ext = "." + segments[-1] if len(segments) > 1 else ".png"
    val_z = str(tile["Z"])
    val_y = str(tile["Y"])
    val_x = str(tile['X'])
    # for tkintermapview, tile segment order is Z, X, Y !!! (must save in z/x/y.png format)
    write_dir = os.path.join(output_dir, val_z, val_x)
    write_filepath = os.path.join(write_dir, val_y) + ext

    if os.path.exists(write_filepath) and not bool_overwrite:
        # skip if already exists when not-overwrite mode
        return
    
    url = (
        tileurl
        .replace(r"{x}", val_x)
        .replace(r"{y}", val_y)
        .replace(r"{z}", val_z)
    )
    
    data = None
    while True:
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            data = urllib.request.urlopen(url, timeout=timeout_num, context=ctx)
            # data = requests.get(url, verify=False)
            break
        except urllib.error.HTTPError as e:
            raise Exception(str(e) + ":" + url)
        except Exception as e:
            if (
                str(e.args)
                == "(timeout('_ssl.c:1091: The handshake operation timed out'),)"
            ):
                print("timeout, retrying... :" + url)
            else:
                raise Exception(str(e) + ":" + url)
    if data is not None:
        # print(f'Downloading {tile[2]}/{tile[0]}/{tile[1]}.png')
        os.makedirs(write_dir, exist_ok=True)
        with open(write_filepath, mode="wb") as f:
            f.write(data.read())
        time.sleep(interval_num / 1000)

if __name__ == "__main__":
    print('Starting Dynamic Tile Download Service:\n')
    queue_file_name = os.path.dirname(os.path.abspath(__file__))+"\\queue_files\\dynamic_tile_queue.csv"
    if not os.path.isfile(queue_file_name): 
        with open(queue_file_name, mode='w', newline='') as file:
            print("Creating batch queue file...\n") 
    wait_interval_sec = 10
    time.sleep(2)
    while True:
        downloaded_tile_list = []
        t1 = datetime.datetime.today()
        try:
            tile_queue = read_csv(queue_file_name)
        except Exception as e:
            print(f'Error reading batch queue file: {e}',end='\n')
            time.sleep(5)
            continue
        if not check_internet_connection():
            time.sleep(5)
            if not check_internet_connection(): print('No public internet connection... terminating service'); break
        if len(tile_queue) > 0:
            print(tile_queue)
            for tile in tile_queue:
                download_tile(tile)
                print(f"Tile {tile} downloaded")
                downloaded_tile_list.append(tile)
            tile_queue = read_csv(queue_file_name)
            tile_queue_updated = []
            for tile in tile_queue:
                if tile in downloaded_tile_list:
                    continue
                else:
                    tile_queue_updated.append(tile)
            write_csv(queue_file_name,tile_queue_updated)
        else:
            print('Dynamic download queue is empty.\n')
        t2 = datetime.datetime.today()
        t_delta = t1 - t2
        if t_delta.total_seconds() < wait_interval_sec:
            print(f'Waiting: {wait_interval_sec - t_delta.total_seconds():,.2f} seconds...',end='\n')
            time.sleep(min(wait_interval_sec - t_delta.total_seconds(),10))
        else:
            time.sleep(1)              
time.sleep(5)   

