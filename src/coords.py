def adjust_coordinate(starting_coord: list,azimuth_degrees: float,shift_m: float) -> list:
    """Adjusts input lat-lon coordinate a specified distance in a specified direction."""
    # import libraries
    import math
    try:
        # input assertations
        assert isinstance(starting_coord,list) and len(starting_coord) == 2, 'Coordinate [lat,lon] needs to be a list of length 2.'
        assert all(isinstance(i,(float,int)) for i in starting_coord), 'Coordinate [lat,lon] needs to be a list of floats or integers.'
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

def convert_coords_to_mgrs(coords: list[float,float],precision:int = 5) -> str:
    """Convert location from coordinates to MGRS."""
    import mgrs
    try:
        assert isinstance(coords,list), 'Coordinate input must be a list.'
        assert len(coords) == 2, 'Coordinate input must be of length 2.'
        coords = [float(c) for c in coords]
        return str(mgrs.MGRS().toMGRS(coords[0], coords[1],MGRSPrecision=precision)).strip()
    except AssertionError:
        return None
    
def convert_mgrs_to_coords(milGrid: str) -> list:
    """Convert location from MGRS to coordinates."""
    import mgrs
    try:
        assert isinstance(milGrid,str), 'MGRS must be a string'
        milGrid = milGrid.replace(" ","").strip()
        return list(mgrs.MGRS().toLatLon(milGrid.encode()))
    except AssertionError:
        return None
    
def check_mgrs_input(mgrs_input: str) -> bool:
    """Determine if the MGRS input is valid"""
    prefix_len = 5
    mgrs_input = mgrs_input.replace(" ","").strip()
    return mgrs_input[:2].isdigit() and mgrs_input[2:prefix_len].isalpha() and mgrs_input[prefix_len:].isdigit() and len(mgrs_input[prefix_len:]) % 2 == 0

def correct_mgrs_input(mgrs_input: str) -> str:
    """Corrects MGRS input format"""
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
    """Determine if the coordinates input is valid"""
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
    """Corrects coordinate input formats."""
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
    """Formats a standard MGRS to a more readable MGRS on the UI display."""
     # determine the MGRS precision level
    prefix_len = 5; mgrs_len = len(mgrs); precision = int((mgrs_len - prefix_len) / 2)
    # if the MGRS is valid, return a more readable MGRS string object
    if check_mgrs_input(mgrs): 
        return f'{str(mgrs[:prefix_len]).upper()} {mgrs[prefix_len:prefix_len+precision]} {mgrs[prefix_len+precision:]}'
    # return the input MGRS if invalid
    return mgrs

def get_distance_between_coords(coord1 : list[float,float],coord2 : list[float,float], unit = 'm') -> float:
    """Determines distance between two coordinates in meters."""
    import haversine
    unit = unit.lower()
    assert unit in ['m','km'], 'Unit must be either meters or kilometers.'
    if isinstance(coord1,tuple):
        coord1 = list(coord1)
    if isinstance(coord2,tuple):
        coord2 = list(coord2)        
    # assert isinstance(coord1,list), 'Coordinate 1 must be a list.'
    assert len(coord1) == 2, 'Coordinate 1 must be of length 2.'
    # assert isinstance(coord2,list), 'Coordinate 2 must be a list.'
    assert len(coord2) == 2, 'Coordinate 2 must be of length 2.'
    if unit == 'm':
        return haversine.haversine(coord1,coord2,unit=haversine.Unit.METERS)
    if unit== 'km':
        return haversine.haversine(coord1,coord2,unit=haversine.Unit.KILOMETERS)

def get_bearing_between_coordinates(coord_origin: list,coord_tgt: list) -> float:
    """Determines bearing (in degrees) between origin coordinates and target coordinate."""
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

def get_center_coord(coord_list : list[list[float,float]]) -> list:
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