#!/usr/bin/env python3

# folium icons: https://fontawesome.com/icons?d=gallery
# folium icon colors: ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
# folium tiles: OpenStreetMap , Stamen Terrain, Stamen Toner

def import_libraries(libraries):
    """
    Helps load/install required libraries when running from cmd prompt

    Returns
    -------
    None.

    """
    import subprocess, warnings
    warnings.filterwarnings("ignore")
    exec('warnings.filterwarnings("ignore")')
    aliases = {'numpy':'np','pandas':'pd','matplotlib.pyplot':'plt',
               'branca.colormap':'cm','haversine':'hs'}
    for s in libraries:
        try:
            exec(f"import {s[0]} as {aliases[s[0]]}") if s[0] in list(aliases.keys()) else exec(f"import {s[0]}")
        except ImportError:
            print(f'Installing... {s[0].split(".")[0]}')
            cmd = f'python -m pip install {s[0].split(".")[0]}'
            subprocess.call(cmd, shell=True, stdout=subprocess.PIPE)
        except ModuleNotFoundError as mnfe:
            print(f"Module error: {mnfe}"); continue
        if len(s) == 1: continue
        for sl in s[1]:
            try:
                exec(f'from {s[0]} import {sl}')
            except ImportError:
                pass

libraries = [['math',['sin','cos','pi']],['collections',['defaultdict']],
             ['datetime',['date']],['jinja2'],['numpy'],
             ['warnings'],['mgrs'],['haversine',['Unit']]]

import_libraries(libraries)
import numpy as np
import warnings
import os
import shutil
import requests
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
    
    import csv, shutil
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

def read_queue(queue_file_name: str) -> None:
    """
    Reads a queue csv file

    Parameters
    ----------
    queue_file_name : str
        File path to queue csv file.

    Returns
    -------
    tile_queue : list of tuples
        list of rows, with each row in tuple form.

    """
    import csv
    # remove_empty_csv_rows(queue_file_name)
    with open(queue_file_name, mode='r') as file:
        csv_reader = csv.reader(file)
        tile_queue = []
        for row in csv_reader:
            if row == []: continue
            tile_queue.append(tuple(row))
    return tile_queue

def write_queue(queue_file_name: str,queue_data: list) -> None:
    """
    Writes a queue csv file

    Parameters
    ----------
    queue_file_name : str
        File path to queue csv file.
    queue_data : list
        list of rows, with each row in list form.

    Returns
    -------
    None.

    """
    import csv
    with open(queue_file_name, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        for row in queue_data:
            csv_writer.writerow(row)

def generate_DTG() -> str:
    """
    Generate the current date-time group (DTG) in DDTTTTMMMYYYY format

    Returns
    -------
    dtg : str
        DRG in DDTTTTMMMYYYY format.

    """
    import calendar, datetime
    # generate today's date
    dt = str(datetime.datetime.today())
    # define today's datetime components
    year = dt.split()[0].split('-')[0]; month = dt.split()[0].split('-')[1]; day = dt.split()[0].split('-')[2]; hour = dt.split()[1].split(':')[0]; minute = dt.split()[1].split(':')[1]
    # log today's DTG
    dtg = f"{day if len(str(day)) == 2 else '0'+day}{hour}{minute}{calendar.month_abbr[int(month)].upper()}{year}"
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
        DTG in TTTT on DD MMM YYYY format..

    """
    return f'At {dtg[2:6]} on {dtg[:2]} {dtg[6:9]} {dtg[-4:]}'

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

def adjust_coordinate(starting_coord: list,azimuth_degrees: (float,int),shift_m: (float,int)) -> list:
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
    def func(degrees: (float,int), magnitude: (float,int)) -> tuple: # returns in lat,lon format
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

def convert_watts_to_dBm(p_watts: (float,int)) -> float:
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
    # input assertation
    assert isinstance(p_watts,(float,int)) and p_watts >= 0, 'Wattage needs to be a float greater than zero.'
    # return power in dBm
    return 10*np.log10(1000*p_watts)

def convert_coords_to_mgrs(coords,precision=5):
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

def convert_mgrs_to_coords(milGrid):
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

def check_mgrs_input(mgrs_input):
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

def check_coord_input(coord_input):
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
        print('string ',coord_input)
        if len(coord_input.split(',')) == 2:
            return coord_list_range_check([float(c) for c in coord_input.split(',')])
        elif len(coord_input.split()) == 2:
            print('here')
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

def format_readable_mgrs(mgrs):
    prefix_len = 5; mgrs_len = len(mgrs); precision = int((mgrs_len - prefix_len) / 2)
    if check_mgrs_input(mgrs): 
        return f'{str(mgrs[:prefix_len]).upper()} {mgrs[prefix_len:prefix_len+precision]} {mgrs[prefix_len+precision:]}'
    return mgrs

def covert_degrees_to_radians(degrees):
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
    from main import adjust_coordinate
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
    assert isinstance(coord_list,list) and len(coord_list) >= 1, "Coordinates must be in a list comprehension of length 1 or greater"
    return [float(np.average([c[0] for c in coord_list])),float(np.average([c[1] for c in coord_list]))]

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
    return 10**((convert_watts_to_dBm(P_t_watts)+(G_t-2.15)-32.4-(10*path_loss_coeff*np.log10(f_MHz))+(G_r-2.15)-R_s)/(10*path_loss_coeff))

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
    return (np.sqrt(2*6371000*r_h+r_h**2)/1000)+(np.sqrt(2*6371000*t_h+t_h**2)/1000)

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
    return (np.sqrt(2*weather_coeff*6371000*r_h+temp_f**2)/1000)+(np.sqrt(2*weather_coeff*6371000*t_h+f_MHz**2)/1000)

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
    path_loss = emission_distance(P_t_watts,f_MHz,G_t,G_r,R_s,path_loss_coeff)
    earth_curve = emission_optical_maximum_distance(t_h,r_h)
    earth_curve_with_ducting = emission_optical_maximum_distance_with_ducting(t_h,r_h,f_MHz,temp_f,weather_coeff)
    emissions_distances = [path_loss,earth_curve,earth_curve_with_ducting]
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

def get_elevation_data(coord_list):
    import csv, time
    def read_elevation_data(src_file):
        with open(src_file,mode='r',newline='') as elev_data_file:
            csv_reader = csv.reader(elev_data_file)
            csv_data = []
            for row in csv_reader:
                csv_data.append(row)
        return csv_data
    def save_elevation_data(save_file,csv_data):
        with open(save_file,mode='w',newline='') as elev_data_file:
            csv_writer = csv.writer(elev_data_file)
            csv_writer.writerows(csv_data)
    coord_elev_data=[]
    src_file = rf'{os.path.realpath(os.path.dirname(__file__))}\elevation\elev_data.csv'
    cp_file = rf'{os.path.realpath(os.path.dirname(__file__))}\elevation\elev_data_preop_copy.csv'
    if os.path.getsize(src_file) >= os.path.getsize(cp_file):
        shutil.copyfile(src_file, cp_file)
    request_string = ''; request_list = []; request_list_conmprehension = []
    csv_data = read_elevation_data(src_file)
    if len(csv_data) > 1:
        mgrs_list = [d[-2] for d in csv_data[1:]]
        elevation_list = [d[-1] for d in csv_data[1:]]
    else:
        mgrs_list = []; elevation_list = []
    num_coords_in_request = 0; max_request_length = 50; num_stored = 0; num_requested = 0
    for i,coord in enumerate(coord_list):
        mgrs = convert_coords_to_mgrs(coord,precision=4)
        if mgrs in mgrs_list:
            elevation = elevation_list[mgrs_list.index(mgrs)]
            coord_elev_data.append([coord[0],coord[1],mgrs,elevation])
            num_stored += 1
            continue
        else:
            request_list.append(','.join([str(c) for c in coord]))
            num_coords_in_request += 1
            num_requested += 1
        if num_coords_in_request >= max_request_length:
            request_list_conmprehension.append(request_list)
            request_list = []
            num_coords_in_request = 0
            max_request_length = np.random.uniform(48,52)
    if num_requested + num_stored > 0: print(f'{num_stored:,.2f} ({num_stored/(num_requested + num_stored)*100:,.2f}%) tiles already in database')
    if num_requested > num_stored and not check_internet_connection(): return []
    if len(request_list) > 0: request_list_conmprehension.append(request_list)
    if len(request_list_conmprehension) > 0 and len(request_list_conmprehension[0]) > 0:
        for i,requested_coords in enumerate(request_list_conmprehension):
            print(f"Request {i+1} of {len(request_list_conmprehension)}")
            csv_data = read_elevation_data(src_file)
            request_string = '|'.join(requested_coords)
            request = f"https://api.open-elevation.com/api/v1/lookup?locations={request_string}"
            try:
                response = requests.get(request)
                for result in response.json()['results']:
                    latitude = result['latitude']
                    longitude = result['longitude']
                    elevation = result['elevation']
                    mgrs_8digit = convert_coords_to_mgrs([latitude,longitude],precision=4)
                    coord_elev_data.append([latitude,longitude,mgrs_8digit,elevation])
                    csv_data.append([latitude,longitude,mgrs_8digit,elevation])
                print(f'Success: {len(requested_coords)} datapoints added to elevation database')
            except:
                print(f"Elevation request {i+1} failed.")
            save_elevation_data(src_file,csv_data)
            time.sleep(np.random.exponential(0.125))
    return coord_elev_data

def plot_elevation_data(coord_elev_data,target_coords=None,title_args=None):
    import datetime
    if coord_elev_data == None or len(coord_elev_data) == 0: return 0
    def get_dist_interval(target_distance,dist_interval):
        if target_distance is None: return -1
        for i, di in enumerate(dist_interval[:-1]):
            if int(di) <= target_distance < int(dist_interval[i+1]):
                return i
        return -1
    # input maybe title?, maybe filename?
    import matplotlib.pyplot as plt
    elev_list = [float(x[-1]) for x in coord_elev_data]
    base_reg=0
    sensor_coord = [coord_elev_data[0][0],coord_elev_data[0][1]]
    sensor_mgrs = convert_coords_to_mgrs(sensor_coord)
    far_side_coord = [coord_elev_data[-1][0],coord_elev_data[-1][1]]
    far_side_coord_mgrs = convert_coords_to_mgrs(far_side_coord)
    distance = int(get_distance_between_coords(sensor_coord,far_side_coord))
    coord_interval = int(distance/len(elev_list))
    dist_interval = list(range(0,distance,coord_interval))
    target_dist_indices = []
    if target_coords is not None:
        for i,target_coord in enumerate(target_coords):
            if i == len(target_coords)-1: target_dist_indices.append(-1); break
            target_dist = get_distance_between_coords(sensor_coord,target_coord)
            target_dist_index = get_dist_interval(target_dist,dist_interval)
            target_dist_indices.append(target_dist_index)
    while len(dist_interval) > len(elev_list):
        dist_interval = dist_interval[:-1]
    while len(dist_interval) < len(elev_list):
        dist_interval = dist_interval + [dist_interval[-1]+coord_interval]
    try:   
        plt.figure(figsize=(10,4))
        # plt.style.use('ggplot')
        plt.style.use('classic')
        plt.plot(dist_interval,elev_list)
        min_elev = min(elev_list)
        max_elev = max(elev_list)
        plt.plot([0,dist_interval[-1]],[min_elev,min_elev],'--g',label='min: '+str(min_elev)+' m')
        plt.plot([0,dist_interval[-1]],[max_elev,max_elev],'--r',label='max: '+str(max_elev)+' m')
        # plt.scatter([0],[elev_list[0]],label='Sensor',color='blue',marker='^',s=100)
        buffer = int(min_elev *.25)
        plt.ylim(int(min_elev - buffer), int(max_elev + buffer))
        plt.xlim(dist_interval[0],dist_interval[-1])
        if target_coords is not None:
            target_dists = []; target_elevations = []
            for i,target_coord in enumerate(target_coords):
                if i == len(target_coords)-1: target_dists.append(dist_interval[-1]); target_elevations.append(elev_list[-1]); break
                target_dist = get_distance_between_coords(sensor_coord,target_coord)
                target_dists.append(target_dist)
                target_elevations.append(elev_list[target_dist_indices[i]])
            plt.vlines(target_dists,[min_elev - buffer for td in target_dists],[max_elev + buffer for td in target_dists],colors=['black' for dt in target_dists],linestyles=['dashed' for dt in target_dists],label='Target Distances')
            plt.scatter(target_dists,target_elevations,label='Possible Targets',color='red',marker='D',s=100)
        plt.fill_between(dist_interval,elev_list,base_reg,alpha=0.1,color='green')
        plt.xlabel("Distance (m)")
        plt.ylabel("Elevation (m)")
        plt.grid()
        plt.legend(fontsize='small')
        if title_args is None:
            plt.title(f'Elevation data from {sensor_mgrs} to {far_side_coord_mgrs}')
        else:
            if len(title_args) == 1:
                plt.title(f'Elevation data from {title_args[0]} to {far_side_coord_mgrs}')
            elif len(title_args) == 2:
                plt.title(f'Elevation data from {title_args[0]} to {title_args[1]}')
        dt = str(datetime.datetime.today()).split()[0].replace('-','')
        num = 0
        output_filename = (rf'{os.path.realpath(os.path.dirname(__file__))}\elevation_plots\{dt}_elevation_data_{num:02}.png')
        while os.path.exists(output_filename):
            num +=1 
            output_filename = (rf'{os.path.realpath(os.path.dirname(__file__))}\elevation_plots\{dt}_elevation_data_{num:02}.png')
        plt.savefig(output_filename)
        plt.show()
    except AttributeError as e:
        return 0

'''https://api.open-elevation.com/api/v1/lookup?locations=51.24885624303748,15.570668663974097'''





