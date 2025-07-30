#!/usr/bin/env python3

import logging, os, warnings
from typing import List, Dict
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

def adjust_brightness(action) -> int:
    """Adjusts brightness by increasing or decreasing it by 20%."""
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
    
    increment_value = 20  # Brightness increment in percentage
    
    if current_os == "Windows":
        # For Windows, using the screen_brightness_control library
        if sbc:
            current_brightness = sbc.get_brightness(display=0)[0]  # Get the brightness for the first display
            
            if action == "increase":
                new_brightness = min(current_brightness + increment_value, 100)  # Ensure brightness does not exceed 100%
            elif action == "decrease":
                new_brightness = max(current_brightness - increment_value, 0)   # Ensure brightness is not less than 0%
            else:
                return current_brightness
            sbc.set_brightness(new_brightness, display=0)
            return new_brightness
    
    elif current_os == "Linux":
        # For Linux, using xrandr (brightness value between 0 and 1)
        get_brightness_cmd = os.popen("xrandr --verbose | grep -i brightness").read()
        current_brightness = float(get_brightness_cmd.split()[1])  # Extract the current brightness
        if action == "increase":
            new_brightness = min(current_brightness + increment_value / 100, 1.0)
        elif action == "decrease":
            new_brightness = max(current_brightness - increment_value / 100, 0.0)
        else:
            return current_brightness
        os.system(f"xrandr --output eDP-1 --brightness {new_brightness}")
        return new_brightness
    
    elif current_os == "Darwin":  # macOS
        # For macOS, using the brightness command-line tool
        get_brightness_cmd = os.popen("brightness -l | grep brightness").read()
        current_brightness = float(get_brightness_cmd.split()[1])  # Extract the current brightness
        if action == "increase":
            new_brightness = min(current_brightness + increment_value / 100, 1.0)
        elif action == "decrease":
            new_brightness = max(current_brightness - increment_value / 100, 0.0)
        else:
            return current_brightness
        os.system(f"brightness {new_brightness}")
        return new_brightness

def read_csv(file_path: str, unescape_newlines: bool = False) -> List[Dict]:
    """Reads a CSV file and returns the data as a list of dictionaries.

    Args:
        file_path: Path to the CSV file.
        unescape_newlines: If True, converts '\\n' in string fields to '\n'; if False, keeps '\\n' as-is.

    Returns:
        A list of dictionaries containing the CSV data.

    Raises:
        FileNotFoundError: If the file does not exist.
        csv.Error: If the CSV file is malformed.
    """
    import csv
    try:
        with open(file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            csv_data = []
            for row in reader:
                if unescape_newlines:
                    # Unescape \\n to \n in string fields
                    sanitized_row = {
                        key: value.replace('\\n', '\n') if isinstance(value, str) else value
                        for key, value in row.items()
                    }
                else:
                    sanitized_row = dict(row)  # Keep \\n as-is
                csv_data.append(sanitized_row)
        return csv_data
    except FileNotFoundError:
        return []
    except csv.Error as e:
        print(f"Error reading CSV file {file_path}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error reading CSV file {file_path}: {e}")
        return []

def write_csv(file_path: str, data: List[Dict], append: bool = False) -> None:
    """Writes a list of dictionaries to a CSV file.

    Args:
        file_path: Path to the CSV file.
        data: List of dictionaries containing the data.
        append: If True, appends to the file; if False, overwrites.
    """
    import csv
    mode = 'a' if append else 'w'
    with open(file_path, mode=mode, newline='') as file:
        try:
            fieldnames = data[0].keys()
        except (IndexError, AttributeError):
            fieldnames = []
            if not data:
                data = [{k: '' for k in fieldnames}]  # Write empty row with headers

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write header only if file is new or empty
        if not append or not file.tell():
            writer.writeheader()

        # Sanitize data to escape newlines and handle None
        sanitized_data = []
        for row in data:
            sanitized_row = {}
            for key, value in row.items():
                if isinstance(value, str) and '\n' in value:
                    sanitized_row[key] = value.replace('\n', '\\n')  # Escape newlines
                elif value is None:
                    sanitized_row[key] = ''  # Replace None with empty string
                else:
                    sanitized_row[key] = value
            sanitized_data.append(sanitized_row)

        try:
            writer.writerows(sanitized_data)
        except Exception as e:
            print(f"Error writing to CSV file {file_path}: {e}")

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

def parse_dtg(dtg_str):
    """Parses DTG_LOCAL like '301244LJUL2025' to a localized datetime."""
    from datetime import datetime
    from dateutil import tz
    try:
        # Remove only the 'L' or 'Z' before the month — which is at position 6
        if dtg_str[6] in ["L","Z"]: dtg_clean = dtg_str[:6] + dtg_str[7:]  # Keep 301244 + JUL2025
        dt = datetime.strptime(dtg_clean, "%d%H%M%b%Y")
        return dt.replace(tzinfo=tz.tzlocal())
    except Exception as e:
        print(f"[ERROR] Failed to parse DTG '{dtg_str}': {e}")
        return None
