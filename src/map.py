def remove_rows_from_marker_csv(file_path : str, marker_type_value : str, marker_num_value : int) -> None:
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

        except FileNotFoundError as e:
            print(f"Error: {e}")
        except PermissionError:
            print(f"Error: Permission denied while trying to read or write '{file_path}'.")
        except KeyError as e:
            print(f"Error: {e}. Please check the CSV file structure.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}") 
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
        if marker_type_value != 'EWT': update_marker_num_with_row_number(file_path)
    except FileNotFoundError as e:
        pass
    except PermissionError:
        print(f"Error: Permission denied while trying to read or write '{file_path}'.")
    except KeyError as e:
        print(f"Error: {e}. Please check the CSV file structure.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def remove_ewt_from_marker_csv(file_path: str, ewt_num: str, ewt_coord: str) -> None:
    import csv, os
    if not os.path.isfile(file_path):
        return  # File doesn't exist, nothing to do

    updated_rows = []

    # Read existing data
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        if not fieldnames:
            return  # No headers, skip
        for row in reader:
            if not (row.get('MARKER_NUM') == ewt_num and row.get('LOC_LATLON') == ewt_coord):
                updated_rows.append(row)

    # Overwrite CSV with filtered rows
    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

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
    
def check_for_intersection(sensor1_coord : list[float,float],
                           end_of_lob1 : list[float,float],
                           sensor2_coord : list[float,float],
                           end_of_lob2 : list[float,float]) -> bool:
    """Checks if there is an intersection between two LOBs."""
    if None in [sensor1_coord,end_of_lob1,sensor2_coord,end_of_lob2]: return False
    def ccw(A,B,C):
        return (C[0]-A[0]) * (B[1]-A[1]) > (B[0]-A[0]) * (C[1]-A[1])
    return ccw(sensor1_coord,sensor2_coord,end_of_lob2) != ccw(end_of_lob1,sensor2_coord,end_of_lob2) and ccw(sensor1_coord,end_of_lob1,sensor2_coord) != ccw(sensor1_coord,end_of_lob1,end_of_lob2)

def check_if_point_in_polygon(point ,polygon):
    from shapely.geometry import Point, Polygon
    area = Polygon([tuple(x) for x in polygon])
    coord_candidate = Point((point[0],point[1]))
    return area.contains(coord_candidate)

def get_polygon_area(shape_coords): # returns area in acres
    def convert_coordinates_to_meters(coord_element: float) -> float:
        """Converts coodinate distance to meters."""
        assert isinstance(coord_element,(float,int)), 'Input needs to be a float.'
        return coord_element * 111139
    import numpy as np
    x = [convert_coordinates_to_meters(sc[0]) for sc in shape_coords]
    y = [convert_coordinates_to_meters(sc[1]) for sc in shape_coords]    
    return (0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1))))/4046.856422