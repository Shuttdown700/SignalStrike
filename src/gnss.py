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