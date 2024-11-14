import datetime, os, time, ssl
from utilities import check_internet_connection, read_csv, write_csv

RESET = "\033[0m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"

def download_tile(tile,
             output_dir="\\".join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1])+'/map_tiles/',
             tileurl="https://tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey=8242f8cd508342868f3d7d29e472aca9",
             bool_overwrite=False,
             timeout_num=5,
             interval_num=100):
    import os, time, urllib, urllib.request
    basepath = tileurl.split('?')[0].split("/")[-1]  # ?foo=bar&z={z}.ext
    segments = basepath.split(".")
    ext = "." + segments[-1] if len(segments) > 1 else ".png"
    val_map = str(tile["Map"])
    val_z = str(tile["Z"])
    val_y = str(tile["Y"])
    val_x = str(tile['X'])
    # for tkintermapview, tile segment order is Z, X, Y !!! (must save in z/x/y.png format)
    write_dir = os.path.join(output_dir, val_map, val_z, val_x)
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

def main():
    from utilities import read_json, determine_tile_url
    conf = read_json(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config_files","conf.json"))
    queue_file_name = os.path.join("\\".join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1]),conf["DIR_RELATIVE_QUEUE"],"dynamic_tile_queue.csv")
    output_dir= os.path.join("\\".join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1]),conf["DIR_RELATIVE_MAP_TILES"])
    if not os.path.isfile(queue_file_name): 
        with open(queue_file_name, mode='w', newline='') as file:
            print("Creating dynamic queue file...\n")
    wait_interval_sec = 10
    time.sleep(2)
    try:
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
                # print(tile_queue)
                for tile in tile_queue:
                    map_name = tile["Map"]
                    tile_url = determine_tile_url(map_name,conf)
                    download_tile(tile,output_dir,tile_url)
                    print(f"Downloading: {tile['Map']}/{tile['Z']}/{tile['X']}/{tile['Y']}.png")
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
    except:
        main()

if __name__ == "__main__":
    print('Starting Dynamic Tile Download Service:\n')
    main()

time.sleep(5)

"""
The output dir and the map remote sources needs to reflect the specific map selected
- need to pass map name in queue
- need to set config values for URLs & relative file paths

"""