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
             ['datetime',['date']],['jinja2'],['numpy'],['statistics',['mean']],
             ['warnings'],['mgrs'],['haversine',['Unit']],['pyserial'],['screen_brightness_control']]

import_libraries(libraries)
import warnings
warnings.filterwarnings("ignore")

def is_port_in_use(port: int) -> bool:
    """
    Assesses if there's an active service on a specified port

    Parameters:
    ----------
    port : int
        Port number of specified port
    
    Returns:
    ----------
    status : bool
        Boolean status of port availability (TRUE = not in use)

    """
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        status = s.connect_ex(('localhost', port)) == 0
        return status
    
def check_internet_connection() -> bool:
    """
    Assesses connectivity to the public internet

    Parameters:
    ----------
    None
    
    Returns:
    ----------
    status : bool
        Boolean status of public internet connectivity (TRUE = connected)
        
    """
    from urllib.request import urlopen
    try:
        urlopen('https://www.google.com/', timeout=10)
        return True
    except:
        return False

def adjust_brightness(action):
    """
    Adjusts brightness by increasing or decreasing it by 10%
    
    Only acceptable actions are 'increase' and 'decrease'
    """
    import platform
    import os

    # Import Windows-specific library
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

def remove_empty_csv_rows(csv_file: str) -> None:
    """
    Removes empty rows from csv file

    Parameters
    ----------
    csv_file : str
        Path to csv file.

    Returns
    -------
    None.

    """
    
    '''
    Experiencing access errors... two simualtanious tempfile instances
    '''
    
    import csv, os, shutil
    # create temp file
    temp_file = open(csv_file[:-4]+"_temp.csv",mode='w', newline='', encoding='utf-8')
    # open csv and temp file
    with open(csv_file, mode='r', newline='', encoding='utf-8') as infile, \
         open(temp_file.name, mode='w', newline='', encoding='utf-8') as outfile:
        # create csv reader,writer object
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        # write non-empty rows to the temp file
        for row in reader:
            if any(field.strip() for field in row):
                writer.writerow(row)
    # move temp file to csv file
    shutil.move(temp_file.name, csv_file)
    temp_file.close()
    os.remove(temp_file)

def read_csv(file_path: str) -> list[dict]:
    """
    Reads a csv file

    Parameters
    ----------
    file_path : str
        File path to csv file.

    Returns
    -------
    csv_data : list of dict rows
        list of rows, with each row in dict form.

    """
    import csv
    with open(file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        csv_data = [row for row in reader]
    return csv_data

def write_csv(file_path: str,csv_data: list) -> None:
    """
    Writes a csv file

    Parameters
    ----------
    file_path : str
        File path to csv file.
    csv_data : list
        list of rows, with each row in dict form.

    Returns
    -------
    None.

    """
    import csv
    with open(file_path, mode='w', newline='') as file:
        try:
            fieldnames = csv_data[0].keys()
        except IndexError:
            if 'dynamic_tile_queue' in file_path:
                fieldnames = {'Z':'','Y':'','X':''}.keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)

def update_marker_num_with_row_number(file_path : str) -> None:
    import csv, os
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        # Read the file and update the MARKER_NUM column
        updated_rows = []
        with open(file_path, mode='r') as infile:
            reader = csv.DictReader(infile)

            # Ensure the required column exists
            if 'MARKER_NUM' not in reader.fieldnames:
                raise KeyError("The CSV file must contain a 'MARKER_NUM' column.")

            # Update MARKER_NUM based on row number
            for i, row in enumerate(reader, start=1):
                row['MARKER_NUM'] = str(i)  # Row numbers start at 1
                updated_rows.append(row)

        # Write the updated rows back to the file
        with open(file_path, mode='w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)

        print("MARKER_NUM column updated successfully.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except PermissionError:
        print(f"Error: Permission denied while trying to read or write '{file_path}'.")
    except KeyError as e:
        print(f"Error: {e}. Please check the CSV file structure.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}") 

def remove_rows_from_csv(file_path : str, marker_type_value : str, marker_num_value : int) -> None:
    import csv, os
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
        # Read the file and filter rows
        with open(file_path, mode='r') as infile:
            reader = csv.DictReader(infile)
            # Ensure required columns exist
            if 'MARKER_TYPE' not in reader.fieldnames or 'MARKER_NUM' not in reader.fieldnames:
                raise KeyError("The CSV file must contain 'MARKER_TYPE' and 'MARKER_NUM' columns.")
            rows = []
            for row in reader:
                try:
                    # Ensure MARKER_NUM is an integer and MARKER_TYPE is a string
                    marker_num = int(row['MARKER_NUM'])
                    marker_type = str(row['MARKER_TYPE'])
                    assert isinstance(marker_num, int), "MARKER_NUM must be an integer."
                    assert isinstance(marker_type, str), "MARKER_TYPE must be a string."
                    # Filter rows based on condition
                    if not (marker_type == marker_type_value and marker_num == marker_num_value):
                        rows.append(row)
                except ValueError as e:
                    print(f"Data type error in row {row}: {e}")
                except AssertionError as e:
                    print(f"Assertion error in row {row}: {e}")
        # Write the filtered rows back to the file
        with open(file_path, mode='w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        update_marker_num_with_row_number(file_path)
        print("Rows removed and file saved successfully.")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except PermissionError:
        print(f"Error: Permission denied while trying to read or write '{file_path}'.")
    except KeyError as e:
        print(f"Error: {e}. Please check the CSV file structure.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def read_json(filepath: str) -> dict:
    import json
    with open(filepath, 'r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)
    return json_data

def generate_DTG(timezone='LOCAL') -> str:
    """
    Generate the current date-time group (DTG) in DDTTTTMMMYYYY format

    Returns
    -------
    dtg : str
        DRG in DDTTTTMMMYYYY format.

    """
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
    """
    Formats the datetime grouop (DTG) to be more readable

    Parameters
    ----------
    dtg : str
        DTG in DDTTTTMMMYYYY format.

    Returns
    -------
    str
        DTG in format: "TTTT on DD MMM YYYY"

    """
    return f'{dtg[2:7]} on {dtg[:2]} {dtg[7:10]} {dtg[-4:]}'

def dtg_from_utc_to_local(dtg_utc,timezone_local):
    from datetime import datetime
    import time
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return dtg_utc + offset

def dtg_from_local_to_utc(dtg_local,timezone_local):
    pass

def determine_tile_url(map_name : str,conf : dict) -> str:
    # determine tile URL from map_name input
    if map_name== 'Terrain':
        tile_url = conf["TERRAIN_TILE_URL"]
    elif map_name== 'ESRI':
        tile_url = conf["SATELLITE_TILE_URL"]
    else:
        print(f"Error: {map_name} is not a valid local map")
        tile_url = ""
    return tile_url

def generate_EUD_coordinate(max_time_seconds = 15) -> dict:
    def coordinate_format_conversion(lat,lat_dir,lon,lon_dir):
        lat = str(lat); lon = str(lon)
        lat_var1 = lat[:2]
        lat_var2 = lat[2:]
        lat_var3 = float(lat_var2)/60
        lat_new = lat_var1+'.'+str(lat_var3).split('.')[-1]
        if lat_dir == 'S': lat_new = '-'+str(float(lat_new))
        lon_var1 = lon[:3]
        lon_var2 = lon[3:]
        lon_var3 = float(lon_var2)/60
        lon_new = lon_var1+'.'+str(lon_var3).split('.')[-1]
        if lon_dir == 'W': lon_new = '-'+str(float(lon_new))
        return lat_new, lon_new
        
    import serial, time
    # Define the COM port and baud rate
    port = 'COM4'  # GPS Receiver COM port
    baudrate = 9600  # Replace with your baud rate (typically 9600 for GPS modules)
    # Open serial port
    with serial.Serial(port, baudrate, timeout=1) as ser:
        start_time = time.time()
        try:
            while True:
                line = ser.readline()
                if line:
                    try:
                        line = line.decode('utf-8').strip()  # Decode bytes to UTF-8 string
                    except UnicodeDecodeError:
                        continue  # Skip decoding errors and try to read the next line
                    try:
                        if line.startswith('$GPGGA'):  # Example: NMEA GGA sentence
                            data = line.split(',')
                            if len(data) >= 11:
                                # log_header = str(data[0])
                                utc_hhmmss_ss = str(data[1]) # UTC in hhmmss.ss format
                                lat = str(data[2])  # Latitude in DDmm.mm format
                                lat_direction = str(data[3]) # either N or S (south is negative)
                                lon = str(data[4])  # Longitude in DDDmm.mm format
                                lon_direction = str(data[5]) # either E or W (west is negative)
                                # quality = str(data[6])
                                num_sats = str(data[7]) # number of satellites in use
                                # hdop = str(data[8]) # less than 5 ideal, more than 20 unacceptable
                                alt = str(data[9]) # altitude above/below sea level
                                # alt_units = str(data[10]) # M = meters
                                if lat == '' or lon == '': continue
                                lat, lon = coordinate_format_conversion(lat,lat_direction,lon,lon_direction)
                                # format gps data
                                gps_data = {
                                    'utc':utc_hhmmss_ss,
                                    'lat':lat,
                                    'lon':lon,
                                    'num_sats':num_sats,
                                    'alt_m':alt}
                                print('GPS data: ',gps_data)
                                return gps_data
                    except Exception as e:
                        print(f'GPS Error: {e}')
                elapsed_time = time.time() - start_time
                if elapsed_time >= max_time_seconds:
                    print(f'{max_time_seconds} seconds elapsed without results in GPS function')
                    break
        except serial.SerialException as e:
            print(f"GPS Serial Exception: {e}")
        except FileNotFoundError as e:
            print(f"No GPS Receiver in {port} :{e}")
        except Exception as e:
            print(f"GPS Error: {e}")
        return None

def convert_coordinates_to_meters(coord_element: float) -> float:
    """
    Converts coodinate distance to meters.

    Parameters
    ----------
    coord_element : float
        Coordinate component (either lat or lon).

    Returns
    -------
    float
        Length in coordinates.

    """
    assert isinstance(coord_element,(float,int)), 'Input needs to be a float.'
    return coord_element * 111139

def adjust_coordinate(starting_coord: list,azimuth_degrees: float,shift_m: float) -> list:
    """
    Adjusts input lat-lon coordinate a specified distance in a specified direction

    Parameters:
    ----------
    starting_coord : list
        Coordinate from which adjustments are applied in [lat,lon] format
    azimuth_degrees : float
        Angle of desired adjustment between 0 and 360 degrees
    shift_m : float
        Distance of desired adjustment in meters
    
    Returns:
    ----------
    new_coord : list
        Adjusted coordinate based on input in [lat,lon] format
        
    """
    # import libraries
    import math
    try:
        # input assertations
        assert isinstance(starting_coord,list) and len(starting_coord) == 2, 'Coordinate [lat,lon] needs to be a list of length 2.'
        assert isinstance(shift_m,(float,int)) and shift_m >= 5, 'Adjustment needs to be a float of at least 10m.'
        assert isinstance(azimuth_degrees,(float,int)) and 0 <= azimuth_degrees <= 360, 'Adjustment needs to be a float betwneen 0 and 360.'
    except AssertionError as ae:
        print(f"Assertation Error in Adjust Coordinate method: {ae}")
        return None
    # function to generate lat,lon adjustments
    def func(degrees: float, magnitude: float) -> tuple: # returns in lat,lon format
        return magnitude * math.cos(math.radians(degrees)), magnitude * math.sin(math.radians(degrees))
    # earth radius in meters
    earth_radius_meters = 6371000.0
    # define starting lat,lon
    starting_lat = float(starting_coord[0]); starting_lon = float(starting_coord[1])
    # define adjustments to lat,lon
    lat_adjustment_m, lon_adjustment_m = func(azimuth_degrees,shift_m)
    # generate adjusted latitude
    new_lat = starting_lat  + (lat_adjustment_m / earth_radius_meters) * (180 / math.pi)
    # generate adjusted longitude
    new_lon = starting_lon + (lon_adjustment_m / earth_radius_meters) * (180 / math.pi) / math.cos(starting_lat * math.pi/180)
    # return adjusted coordinate
    return [new_lat,new_lon]

def convert_coords_to_mgrs(coords: list,precision:int = 5) -> str:
    """
    Convert location from coordinates to MGRS.

    Parameters
    ----------
    coords : list of length 2
        Grid coordinate. Example: [lat,long].
    precision : int, optional
        Significant figures per easting/northing value. The default is 5.

    Returns
    -------
    str
        Location in MGRS notation.

    """
    import mgrs
    try:
        assert isinstance(coords,list), 'Coordinate input must be a list.'
        assert len(coords) == 2, 'Coordinate input must be of length 2.'
        return str(mgrs.MGRS().toMGRS(coords[0], coords[1],MGRSPrecision=precision)).strip()
    except AssertionError:
        return None

def convert_mgrs_to_coords(milGrid: str) -> list:
    """
    Convert location from MGRS to coordinates.

    Parameters
    ----------
    milGrid : str
        Location in MGRS notation.

    Returns
    -------
    list
        Grid coordinate. Example: [lat,long].

    """
    import mgrs
    try:
        assert isinstance(milGrid,str), 'MGRS must be a string'
        milGrid = milGrid.replace(" ","").strip()
        return list(mgrs.MGRS().toLatLon(milGrid.encode()))
    except AssertionError:
        return None

def check_mgrs_input(mgrs_input: str) -> bool:
    """
    Determine if the MGRS input is valid 

    Parameters:
    ----------
    mgrs_input : str
        Candidate MGRS input

    Returns:
    ----------
    Boolean
        Determination if MGRS is valid (TRUE) or not (FALSE)

    """
    prefix_len = 5
    mgrs_input = mgrs_input.replace(" ","").strip()
    return mgrs_input[:2].isdigit() and mgrs_input[2:prefix_len].isalpha() and mgrs_input[prefix_len:].isdigit() and len(mgrs_input[prefix_len:]) % 2 == 0

def correct_mgrs_input(mgrs_input: str) -> str:
    """
    Corrects MGRS input format

    Parameters
    ----------
    mgrs_input : str
        MGRS input.

    Returns
    -------
    mgrs_corrected
        Corrected format of MGRS.

    """
    try:
        if check_mgrs_input(mgrs_input):
            mgrs_input = mgrs_input.replace(" ","").strip()
            zone_number = mgrs_input[:2]
            band_letter = mgrs_input[2].upper()
            mgrs_column_letter = mgrs_input[3].upper()
            mgrs_row_letter = mgrs_input[4].upper()
            mgrs_easting_northing = mgrs_input[5:]
            mgrs_corrected = zone_number+band_letter+mgrs_column_letter+mgrs_row_letter+mgrs_easting_northing
            return mgrs_corrected
        return mgrs_input
    except AttributeError:
        return mgrs_input
        
def check_coord_input(coord_input : list) -> bool:
    """
    Determine if the coordinates input is valid

    Parameters
    ----------
    coord_input : str,list,tuple
        Candidate coordinate input

    Returns
    -------
    Boolean
        Determination if coordinate is valid (TRUE) or not (FALSE)

    """
    def coord_list_range_check(coord_list):
        if -90 <= coord_list[0] <= 90 and -180 <= coord_list[1] <= 180:
            return True
        return False
    # check if string input
    if isinstance(coord_input,str):
        if len(coord_input.split(',')) == 2:
            return coord_list_range_check([float(c) for c in coord_input.split(',')])
        elif len(coord_input.split()) == 2:
            return coord_list_range_check([float(c) for c in coord_input.split()])
        return False
    # checkc if list input
    elif isinstance(coord_input, list):
        if coord_input.count(',') == 0 and len(coord_input.strip().split()) == 2:
            coord_input = [float(c) for c in coord_input.split()]
        return coord_list_range_check(coord_input)
    # check if tuple input
    elif isinstance(coord_input, tuple):
        return coord_list_range_check(list(coord_input))

def correct_coord_input(coord):
    """
    Corrects coordinate input formats

    Parameters
    ----------
    coord : list,str,tuple
        User's coordinate input

    Returns
    -------
    list
        Coordinate in correct format

    """
    # if space-seperated string
    if coord.count(',') == 0 and len(coord.strip().split()) == 2: 
        return [float(c) for c in coord.split()]
    # if comma-seperated string
    elif coord.count(',') == 1 and len(coord.strip().split(',')) == 2: 
        return [float(c) for c in coord.split(',')]
    # if list of strings
    elif isinstance(coord,list) and len(coord) == 2 and (isinstance(coord[0],str) or isinstance(coord[1],str)):
        return [float(c) for c in coord.split(',')]
    # if list of strings
    elif isinstance(coord,tuple) and len(coord) == 2:
        return [float(c) for c in list(coord)]
    return coord

def format_readable_mgrs(mgrs:str) -> str:
    """
    Formats a standard MGRS to a more readable MGRS for the purpose of UI

    Parameters
    ----------
    mgrs : str
        The MGRS grid.

    Returns
    -------
    str
        The re-formated, more-readable MGRS grid.

    """
    # determine the MGRS precision level
    prefix_len = 5; mgrs_len = len(mgrs); precision = int((mgrs_len - prefix_len) / 2)
    # if the MGRS is valid, return a more readable MGRS string object
    if check_mgrs_input(mgrs): 
        return f'{str(mgrs[:prefix_len]).upper()} {mgrs[prefix_len:prefix_len+precision]} {mgrs[prefix_len+precision:]}'
    # return the input MGRS if invalid
    return mgrs

def covert_degrees_to_radians(degrees):
    import numpy as np
    """
    Converts angle from degrees to radians.

    Parameters
    ----------
    degrees : float [0-360]
        Angle measured in degrees.

    Returns
    -------
    float
        Angle measured in radians [0-2π].

    """
    assert isinstance(degrees,(float,int)), 'Degrees must be a float [0-360]'
    return (degrees%360) * np.pi/180

def get_coord_box(center_coord,x_dist_m,y_dist_m):
    """
    Generate a coordinate box for the tile downloader.

    Parameters
    ----------
    center_coord : list
        Coordinate in [lat,lon] format
    x_dist_m : float
        Distance from center to box edge along x-axis in meters
    y_dist_m : float
        Distance from center to box edge along y-axis in meters

    Returns
    -------
    str
        Coodinate string in "min_lon, min_lat, max_lon, max_lat" format.

    """
    import numpy as np
    diag_dist = np.sqrt(x_dist_m**2 + y_dist_m**2)
    tl_coord = adjust_coordinate(center_coord,315,diag_dist)
    tl_coord = [round(coord,6) for coord in tl_coord]
    br_coord = adjust_coordinate(center_coord,135,diag_dist)
    br_coord = [round(coord,6) for coord in br_coord]
    return f"{tl_coord[1]},{br_coord[0]},{br_coord[1]},{tl_coord[0]}"

def get_distance_between_coords(coord1,coord2):
    """
    Determines distance between two coordinates in meters

    Parameters
    ----------
    coord1 : list of length 2
        Grid coordinate. Example: [lat,long].
    coord2 : list of length 2
        Grid coordinate. Example: [lat,long].
    Returns
    -------
    float
        Distance between two coordinates in meters.

    """
    import haversine
    if isinstance(coord1,tuple):
        coord1 = list(coord1)
    if isinstance(coord2,tuple):
        coord2 = list(coord2)        
    # assert isinstance(coord1,list), 'Coordinate 1 must be a list.'
    assert len(coord1) == 2, 'Coordinate 1 must be of length 2.'
    # assert isinstance(coord2,list), 'Coordinate 2 must be a list.'
    assert len(coord2) == 2, 'Coordinate 2 must be of length 2.'
    return haversine.haversine(coord1,coord2,unit=haversine.Unit.METERS)

def get_bearing_between_coordinates(coord_origin: list,coord_tgt: list) -> float:
    """
    Determines bearing (in degrees) between origin coordinates and target coordinate

    Parameters
    ----------
    coord_origin : list
        Coordinate in [lat, lon] format
    coord_tgt : list
        Coordinate in [lat, lon] format

    Returns
    -------
    float
        Bearing in range [0-360]

    """
    import math
    import numpy as np
    # define local variables
    long1 = coord_origin[1]; lat1 = coord_origin[0]
    long2 = coord_tgt[1]; lat2 = coord_tgt[0]
    dLon = (long2 - long1)
    # translate coordinate formats
    x = math.cos(math.radians(lat2)) * math.sin(math.radians(dLon))
    y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(dLon))
    # find bearing in radians
    brng_radians = np.arctan2(x,y)
    brng_degrees = np.degrees(brng_radians)
    # adjust negative bearings (below lower bound)
    while brng_degrees < 0:
        brng_degrees += 360
    # adjust large bearings (above upper bound)
    brng_degrees = brng_degrees % 360
    return brng_degrees

def get_center_coord(coord_list):
    """
    Returns the average coordinate from list of coordinates.

    Parameters
    ----------
    coord_list : list comprehension of length n
        List of coordinates. Example: [[lat1,long1],[lat2,long2],...[latN,lonN]]

    Returns
    -------
    list
        Center coordiante.

    """
    from statistics import mean
    assert isinstance(coord_list,list) and len(coord_list) >= 1, "Coordinates must be in a list comprehension of length 1 or greater"
    return [float(mean([c[0] for c in coord_list])),float(mean([c[1] for c in coord_list]))]

def convert_watts_to_dBm(p_watts: float) -> float:
    """
    Converts watts to dBm.

    Parameters
    ----------
    p_watts : float
        Power in watts (W).

    Returns
    -------
    float
        Power in dBm.

    """
    import math
    # input assertation
    assert isinstance(p_watts,(float,int)) and p_watts >= 0, 'Wattage needs to be a float greater than zero.'
    # return power in dBm
    return 10*math.log10(1000*p_watts)

def emission_distance(P_t_watts,f_MHz,G_t,G_r,R_s,path_loss_coeff=3):
    """
    Returns theoretical maximum distance of emission.

    Parameters
    ----------
    P_t_watts : float
        Power output of transmitter in watts (W).
    f_MHz : float
        Operating frequency in MHz.
    G_t : float
        Transmitter antenna gain in dBi.
    G_r : float
        Receiver antenna gain in dBi.
    R_s : float
        Receiver sensitivity in dBm *OR* power received in dBm.
    path_loss_coeff : float, optional
        Coefficient that considers partial obstructions such as foliage. 
        The default is 3.

    Returns
    -------
    float
        Theoretical maximum distance in km.

    """
    import math
    # return 10**((convert_watts_to_dBm(P_t_watts)+(G_t)-32.4-(20*math.log10(f_MHz))+(G_r)-R_s)/(20))
    return 10**((convert_watts_to_dBm(P_t_watts)+(G_t)-32.4-(10*path_loss_coeff*math.log10(f_MHz))+(G_r)-R_s)/(10*path_loss_coeff))

def emission_optical_maximum_distance(t_h,r_h):
    """
    Returns theoretical maximum line-of-sight between transceivers.

    Parameters
    ----------
    t_h : float
        Transmitter height in meters (m).
    r_h : float
        Receiver height in meters (m).

    Returns
    -------
    float
        Maximum line-of-sight due to Earth curvature in km.

    """
    import math
    return (math.sqrt(2*6371000*r_h+r_h**2)/1000)+(math.sqrt(2*6371000*t_h+t_h**2)/1000)

def emission_optical_maximum_distance_with_ducting(t_h,r_h,f_MHz,temp_f,weather_coeff=4/3):
    """
    Returns theoretical maximum line-of-sight between transceivers with ducting consideration.

    Parameters
    ----------
    t_h : float
        Transmitter height in meters (m).
    r_h : float
        Receiver height in meters (m).
    f_MHz : float
        Operating frequency in MHz.
    temp_f : float
        ENV Temperature in fahrenheit.
    weather_coeff : float, optional
        ENV Weather conditions coefficient. The default is 4/3.

    Returns
    -------
    float
        Maximum line-of-sight due to Earth curvature and ducting in km.

    """
    import math
    return (math.sqrt(2*weather_coeff*6371000*r_h+temp_f**2)/1000)+(math.sqrt(2*weather_coeff*6371000*t_h+f_MHz**2)/1000)

def get_emission_distance(P_t_watts,f_MHz,G_t,G_r,R_s,t_h,r_h,temp_f,path_loss_coeff=3,weather_coeff=4/3,pure_pathLoss=False):
    """
    Returns theoretical maximum line-of-sight between transceivers all pragmatic consideration.

    Parameters
    ----------
    P_t_watts : float
        Power output of transmitter in watts (W).
    f_MHz : float
        Operating frequency in MHz.
    G_t : float
        Transmitter antenna gain in dBi.
    G_r : float
        Receiver antenna gain in dBi.
    R_s : float
        Receiver sensitivity in dBm *OR* power received in dBm.
    t_h : float
        Transmitter height in meters (m).
    r_h : float
        Receiver height in meters (m).
    temp_f : TYPE
        DESCRIPTION.
    temp_f : float
        ENV Temperature in fahrenheit.
    weather_coeff : float, optional
        ENV Weather conditions coefficient. The default is 4/3.

    Returns
    -------
    float
        Maximum line-of-sight due to path-loss, Earth curvature and ducting in km.

    """
    path_loss_coeff = float(path_loss_coeff)
    path_loss = emission_distance(P_t_watts,f_MHz,G_t,G_r,R_s,path_loss_coeff)
    # earth_curve = emission_optical_maximum_distance(t_h,r_h)
    earth_curve_with_ducting = emission_optical_maximum_distance_with_ducting(t_h,r_h,f_MHz,temp_f,weather_coeff)
    emissions_distances = [path_loss,earth_curve_with_ducting]
    if pure_pathLoss:
        return path_loss
    else:
        return min(emissions_distances)

def organize_polygon_coords(coord_list):
    def clockwiseangle_and_distance(point,origin,refvec):
        import math
        vector = [point[0]-origin[0], point[1]-origin[1]]
        lenvector = math.hypot(vector[0], vector[1])
        if lenvector == 0:
            return -math.pi, 0
        normalized = [vector[0]/lenvector, vector[1]/lenvector]
        dotprod  = normalized[0]*refvec[0] + normalized[1]*refvec[1]
        diffprod = refvec[1]*normalized[0] - refvec[0]*normalized[1]
        angle = math.atan2(diffprod, dotprod)
        if angle < 0:
            return 2*math.pi+angle, lenvector
        return angle, lenvector
    coord_list = sorted(coord_list, key = lambda x: (x[1],x[0]),reverse=True)
    origin = coord_list[0]; refvec = [0,1]
    # ordered_points = coord_list[0]; coord_list = coord_list[1:]
    ordered_points = sorted(coord_list, key = lambda x: clockwiseangle_and_distance(x,origin,refvec))
    return ordered_points
    
def get_line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, -C

def get_intersection(L1, L2):
    D  = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return [x,y]
    else:
        return False

def check_for_intersection(sensor1_coord,end_of_lob1,sensor2_coord,end_of_lob2):
    """
    Checks if there is an intersection between two LOBs

    Parameters
    ----------
    sensor1_coord : list
        Sensor 1 coordinate in [lat,lon] format
    end_of_lob1 : list
        Furthest coordinate at the end of sensor 1's LOB
    sensor2_coord : list
        Sensor 2 coordinate in [lat,lon] format
    end_of_lob2 : list
        Furthest coordinate at the end of sensor 2's LOB

    Returns
    -------
    bool
        Returns TRUE if intersection exists, FALSE if no intersection or NONEs in input field

    """
    if None in [sensor1_coord,end_of_lob1,sensor2_coord,end_of_lob2]: return False
    def ccw(A,B,C):
        return (C[0]-A[0]) * (B[1]-A[1]) > (B[0]-A[0]) * (C[1]-A[1])
    return ccw(sensor1_coord,sensor2_coord,end_of_lob2) != ccw(end_of_lob1,sensor2_coord,end_of_lob2) and ccw(sensor1_coord,end_of_lob1,sensor2_coord) != ccw(sensor1_coord,end_of_lob1,end_of_lob2)

def check_if_point_in_polygon(point,polygon):
    from shapely.geometry import Point, Polygon
    area = Polygon([tuple(x) for x in polygon])
    coord_candidate = Point((point[0],point[1]))
    return area.contains(coord_candidate)

def get_polygon_area(shape_coords): # returns area in acres
    import numpy as np
    x = [convert_coordinates_to_meters(sc[0]) for sc in shape_coords]
    y = [convert_coordinates_to_meters(sc[1]) for sc in shape_coords]    
    return (0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1))))/4046.856422

def get_coords_from_LOBs(sensor_coord,azimuth,error,min_lob_length,max_lob_length):
    center_coord_list = []
    right_error_azimuth = (azimuth+error) % 360
    left_error_azimuth = (azimuth-error) % 360
    running_coord_left = [list(sensor_coord)[0],list(sensor_coord)[1]]
    running_coord_center = [list(sensor_coord)[0],list(sensor_coord)[1]]
    running_coord_right = [list(sensor_coord)[0],list(sensor_coord)[1]]
    lob_length = 0
    interval_meters = 30
    while interval_meters > max_lob_length and interval_meters > 10:
        interval_meters -= 10
    near_right_coord = []; near_left_coord = []; far_right_coord = []; far_left_coord = []
    while lob_length <= max_lob_length:
        running_coord_left = adjust_coordinate(running_coord_left,left_error_azimuth,interval_meters)
        running_coord_right = adjust_coordinate(running_coord_right,right_error_azimuth,interval_meters)
        running_coord_center = adjust_coordinate(running_coord_center,azimuth,interval_meters)
        center_coord_list.append(running_coord_center)    
        if lob_length > min_lob_length:
            if near_right_coord == []: near_right_coord = list(running_coord_right)
            if near_left_coord == []: near_left_coord = list(running_coord_left)
        lob_length += interval_meters
    far_right_coord = running_coord_right
    far_left_coord = running_coord_left
    center_coord = get_center_coord([near_right_coord,near_left_coord,far_right_coord,far_left_coord])
    near_center_coord = get_center_coord([near_right_coord,near_left_coord])
    center_coord_list = [c for c in center_coord_list if len(c) <= 2]
    return center_coord, near_right_coord, near_left_coord, near_center_coord, far_right_coord, far_left_coord, running_coord_center, center_coord_list





