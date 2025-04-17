#!/usr/bin/env python3

#!/usr/bin/env python

def import_libraries(libraries):
    """
    Helps load/install required libraries when running from cmd prompt

    Returns
    -------
    None.

    """
    def install_missing_module(missing_module):
        print(f'Installing... {missing_module.split(".")[0]}')
        cmd = f'python -m pip install {missing_module.split(".")[0]}'
        subprocess.call(cmd, shell=True, stdout=subprocess.PIPE)
    import subprocess, warnings
    warnings.filterwarnings("ignore")
    exec('warnings.filterwarnings("ignore")')
    aliases = {'numpy':'np','pandas':'pd','matplotlib.pyplot':'plt',
               'branca.colormap':'cm','haversine':'hs'}
    for s in libraries:
        try:
            exec(f"import {s[0]} as {aliases[s[0]]}") if s[0] in list(aliases.keys()) else exec(f"import {s[0]}")
        except ImportError:
            if s[0] == 'pyserial':
                try:
                    exec("import serial")
                    continue
                except ImportError:
                    install_missing_module(s[0])
            else:
                install_missing_module(s[0])
        except ModuleNotFoundError as mnfe:
            print(f"Module error: {mnfe}"); continue
        if len(s) == 1: continue
        for sl in s[1]:
            try:
                exec(f'from {s[0]} import {sl}')
            except ImportError:
                pass

libraries = [['math',['sin','cos','pi']],['collections',['defaultdict']],
             ['datetime',['date']],['numpy'],['statistics',['mean']],
             ['warnings'],['mgrs'],['haversine',['Unit']],['pyserial'],['screen_brightness_control']]

import_libraries(libraries)
import logging, os, warnings
warnings.filterwarnings("ignore")

def is_port_in_use(port: int) -> bool:
    """Assesses if there's an active service on a specified port."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        status = s.connect_ex(('localhost', port)) == 0
        return status
    
def check_internet_connection() -> bool:
    """Assesses connectivity to the public internet."""
    from urllib.request import urlopen
    try:
        urlopen('https://www.google.com/', timeout=10)
        return True
    except:
        return False

def adjust_brightness(action):
    """Adjusts brightness by increasing or decreasing it by 10%."""
    import platform
    import os

    # Import Windows-specific library
    assert action in ['increase', 'decrease'], "Invalid action. Use 'increase' or 'decrease'."
    try:
        import screen_brightness_control as sbc  # Only available on Windows
    except ImportError:
        sbc = None
    # Get the current OS
    current_os = platform.system()
    
    increment_value = 10  # Brightness increment in percentage
    
    if current_os == "Windows":
        # For Windows, using the screen_brightness_control library
        if sbc:
            current_brightness = sbc.get_brightness(display=0)[0]  # Get the brightness for the first display
            # print(f"Current brightness: {current_brightness}%")
            
            if action == "increase":
                new_brightness = min(current_brightness + increment_value, 100)  # Ensure brightness does not exceed 100%
            elif action == "decrease":
                new_brightness = max(current_brightness - increment_value, 0)   # Ensure brightness is not less than 0%
            else:
                print("Invalid action. Use 'increase' or 'decrease'.")
                return
            
            sbc.set_brightness(new_brightness, display=0)
            # print(f"Brightness set to {new_brightness}%")
    
    elif current_os == "Linux":
        # For Linux, using xrandr (brightness value between 0 and 1)
        get_brightness_cmd = os.popen("xrandr --verbose | grep -i brightness").read()
        current_brightness = float(get_brightness_cmd.split()[1])  # Extract the current brightness
        # print(f"Current brightness: {current_brightness * 100}%")
        
        if action == "increase":
            new_brightness = min(current_brightness + increment_value / 100, 1.0)
        elif action == "decrease":
            new_brightness = max(current_brightness - increment_value / 100, 0.0)
        else:
            print("Invalid action. Use 'increase' or 'decrease'.")
            return
        
        os.system(f"xrandr --output eDP-1 --brightness {new_brightness}")
        # print(f"Brightness set to {new_brightness * 100}%")
    
    elif current_os == "Darwin":  # macOS
        # For macOS, using the brightness command-line tool
        get_brightness_cmd = os.popen("brightness -l | grep brightness").read()
        current_brightness = float(get_brightness_cmd.split()[1])  # Extract the current brightness
        # print(f"Current brightness: {current_brightness * 100}%")
        
        if action == "increase":
            new_brightness = min(current_brightness + increment_value / 100, 1.0)
        elif action == "decrease":
            new_brightness = max(current_brightness - increment_value / 100, 0.0)
        else:
            print("Invalid action. Use 'increase' or 'decrease'.")
            return
        
        os.system(f"brightness {new_brightness}")
        # print(f"Brightness set to {new_brightness * 100}%")
    
    else:
        print(f"Unsupported operating system: {current_os}")

def read_csv(file_path: str) -> list[dict]:
    """Reads a csv file and returns the data in a list of dict rows."""
    import csv
    with open(file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        csv_data = [row for row in reader]
    return csv_data

def write_csv(file_path: str,data: list) -> None:
    """Writes data to a csv file."""
    import csv
    with open(file_path, mode='w', newline='') as file:
        try:
            fieldnames = data[0].keys()
        except IndexError:
            if 'dynamic_tile_queue' in file_path:
                fieldnames = {'Z':'','Y':'','X':''}.keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def read_json(filepath: str) -> dict:
    """Reads a json file and returns the data as a dictionary."""
    import json
    with open(filepath, 'r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)
    return json_data

def generate_DTG(timezone='LOCAL') -> str:
    """Generate the current date-time group (DTG) in DDTTTTXMMMYYYY format."""
    import calendar, datetime
    # determine which timezone to use
    if timezone == 'LOCAL':
        # generate today's date
        dt = str(datetime.datetime.today())
    tz_id = timezone[0]
    # define today's datetime components
    year = dt.split()[0].split('-')[0]; month = dt.split()[0].split('-')[1]; day = dt.split()[0].split('-')[2]; hour = dt.split()[1].split(':')[0]; minute = dt.split()[1].split(':')[1]
    # log today's DTG
    dtg = f"{day if len(str(day)) == 2 else '0'+day}{hour}{minute}{tz_id}{calendar.month_abbr[int(month)].upper()}{year}"
    return dtg

def format_readable_DTG(dtg: str) -> str:
    """Formats the datetime grouop (DTG) in DDTTTTXMMMYYYY format to be more readable format: "TTTT on DD MMM YYYY"."""
    return f'{dtg[2:7]} on {dtg[:2]} {dtg[7:10]} {dtg[-4:]}'

def get_log_path(base_subdir: str) -> str:
    """Create and return a dated log path inside the given subdirectory."""
    from datetime import datetime
    import os
    date_str = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join("..", "logs", base_subdir, date_str)
    os.makedirs(path, exist_ok=True)
    return path

def setup_logger(log_name: str, log_path: str) -> logging.Logger:
    """Configure and return a logger that logs to both file and stdout."""
    logger = logging.getLogger(log_name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(os.path.join(log_path, f"{log_name}.log"))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger

_logger_cache = {} 

def get_logger(name: str, category: str = "general", level: int = logging.INFO) -> logging.Logger:
    """
    Get a logger by name and category.
    Creates log file in ../logs/<category>/YYYY-MM-DD/<name>.log
    Caches loggers to prevent duplicate handlers.
    
    Args:
        name (str): Name of the logger (used for log file naming).
        category (str): Subdirectory under logs where logs are stored.
        level (int): Logging level, e.g., logging.INFO, logging.DEBUG.
    
    Returns:
        logging.Logger: Configured logger.
    """
    cache_key = f"{category}:{name}"
    if cache_key in _logger_cache:
        return _logger_cache[cache_key]

    log_path = get_log_path(category)
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(os.path.join(log_path, f"{name}.log"))
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        logger.addHandler(stream_handler)

    _logger_cache[cache_key] = logger
    return logger




