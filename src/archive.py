# -*- coding: utf-8 -*-
"""
Created on Sat Jun  8 12:35:45 2024

@author: brend
"""

# def add_title(m,df_heatmap=False):
#     import datetime
#     if df_heatmap:
#         min_date = min(list(df_heatmap['Datetime']))
#         max_date = max(list(df_heatmap['Datetime']))
#     else:
#         min_date = max_date = str(datetime.date.today())
#     location = 'AL ASAD AIRBASE'
#     prefix = '***DEMO***'; suffix = '***DEMO***'
#     if min_date == max_date and ':' in min_date:
#         map_title = f'{prefix} ELECTROMAGNETIC SPECTRUM (EMS) SURVEY: {location.upper()}, IRAQ at {min_date} {suffix}'
#     elif min_date == max_date:
#         map_title = f'{prefix} ELECTROMAGNETIC SPECTRUM (EMS) SURVEY: {location.upper()}, IRAQ on {min_date} {suffix}'
#     else:
#         map_title = f'{prefix} ELECTROMAGNETIC SPECTRUM (EMS) SURVEY: {location.upper()}, IRAQ from {min_date} to {max_date} {suffix}'
#     title_html = f'''
#                  <h3 align="center" style="font-size:32px;background-color:yellow;color=black;font-family:arial"><b>{map_title}</b></h3>
#                  ''' 
#     m.get_root().html.add_child(folium.Element(title_html))
#     return m

# def create_circle(center_coord,circle_radius_m,circle_color='green',circle_name=None,circle_opacity=1,circle_fill_opacity=0.4,fill_bool=True):
#     circle = folium.Circle(
#         location=center_coord,
#         color=circle_color,
#         radius=circle_radius_m,
#         fill=fill_bool,
#         opacity=circle_opacity,
#         fill_opacity=circle_fill_opacity,
#         tooltip=circle_name)
#     return circle

# def create_line(points,line_color='black',line_weight=5,line_popup=None,dash_weight=None):
#     line = folium.PolyLine(locations = points,
#                     color = line_color,
#                     weight = line_weight,
#                     dash_array = dash_weight,
#                     tooltip = line_popup
#                     )
#     return line

# def create_gradient_map(min_value=0,max_value=1,colors=['lightyellow','yellow','orange','red','darkred'],tick_labels = ['None','Poor','Moderate','Good','Excellent'],steps=20):
#     assert len(colors) == len(tick_labels), 'Number of colors must equal number of labels'
#     index = [min_value,
#              np.average([min_value,np.average([min_value,max_value])]),
#              np.average([min_value,max_value]),
#              np.average([np.average([min_value,max_value]),max_value]),
#              max_value]
#     assert len(tick_labels) == len(index), 'Index list be equal length number to labels list'
#     colormap = cm.LinearColormap(
#         colors = colors,
#         index = index,
#         vmin = int(min_value),
#         vmax = int(max_value),
#         tick_labels = tick_labels
#         )
#     gradient_map=defaultdict(dict)
#     for i in range(steps):
#         gradient_map[1/steps*i] = colormap.rgb_hex_str(min_value + ((max_value-min_value)/steps*i))
#     return colormap, gradient_map

# def plot_grid_lines(center_coord,num_gridlines = 10,precision = 5, adj_increment_m = 1000):
#     def round_to_nearest_km(num):
#         km = str(round(int(num)*10**(-1*(len(num)-2)),0)).replace('.','')
#         if num[0] == '0' and len(km) < 5: km = '0' + km
#         while len(km) < len(num):
#             km += '0'
#         return km
#     def round_coord_to_nearest_mgrs_km2(center_coord,precision=5):
#         center_coord_preamble = convert_coords_to_mgrs(center_coord,precision)[:precision*-2]
#         easting = convert_coords_to_mgrs(center_coord,precision)[precision*-2:precision*-1]
#         northing = convert_coords_to_mgrs(center_coord,precision)[precision*-1:]
#         return center_coord_preamble+round_to_nearest_km(easting)+round_to_nearest_km(northing)
#     def adjust_mgrs(starting_mgrs,direction,distance_m):
#         starting_coord = convert_mgrs_to_coords(starting_mgrs)
#         if direction == 'e':
#             azimuth = 90
#         elif direction == 'w':
#             azimuth = 270
#         elif direction == 'n':
#             azimuth = 0
#         elif direction == 's':
#             azimuth = 180
#         try:
#             raise
#         except:
#             coord = adjust_coordinate(starting_coord,azimuth,distance_m)
#             mgrs = round_coord_to_nearest_mgrs_km2(coord)
#             if mgrs == starting_mgrs:
#                 new_mgrs = convert_coords_to_mgrs(coord)
#                 adjust_mgrs(new_mgrs,direction,distance_m)
#         return mgrs, coord
#     def incremental_points(starting_mgrs,orientation,increment_vector,num_increments):
#         running_mgrs = starting_mgrs
#         running_coord= convert_mgrs_to_coords(starting_mgrs)      
#         point_list = [(running_coord,running_mgrs)]           
#         for i in range(num_increments):
#             # distance = (i+1)*increment_vector
#             running_mgrs, running_coord = adjust_mgrs(running_mgrs,orientation,increment_vector)
#             point_list.append((running_coord,running_mgrs))
#         return point_list
#     def realign_points(item_list):
#         new_list = []
#         mgrs_list = []
#         for item in item_list:
#             mgrs = round_coord_to_nearest_mgrs_km2(item[0])
#             if mgrs in mgrs_list:
#                 continue
#             coord = convert_mgrs_to_coords(mgrs)
#             mgrs_list.append(mgrs)
#             new_list.append((coord,mgrs))
#         return new_list
#     center_mgrs = round_coord_to_nearest_mgrs_km2(center_coord)
#     center_coord = convert_mgrs_to_coords(center_mgrs)
#     base_points_hl = [(center_coord,center_mgrs)]
#     base_points_vl = [(center_coord,center_mgrs)]
#     base_points_hl = incremental_points(center_mgrs,'e',adj_increment_m,num_gridlines)+incremental_points(center_mgrs,'w',adj_increment_m,num_gridlines)
#     base_points_vl = incremental_points(center_mgrs,'n',adj_increment_m,num_gridlines)+incremental_points(center_mgrs,'s',adj_increment_m,num_gridlines)    
#     base_points_hl = sorted(base_points_hl,key = lambda x: x[0][1])
#     base_points_vl = sorted(base_points_vl,key = lambda x: x[0][0])
#     east_center_mgrs = base_points_hl[-1][1]
#     west_center_mgrs = base_points_hl[0][1]
#     north_center_mgrs = base_points_vl[-1][1]
#     south_center_mgrs = base_points_vl[0][1]
#     e_boundary_points = incremental_points(east_center_mgrs,'n',adj_increment_m,num_gridlines)+incremental_points(east_center_mgrs,'s',adj_increment_m,num_gridlines)
#     e_boundary_points = sorted(e_boundary_points,key = lambda x: x[0][0])
#     w_boundary_points = incremental_points(west_center_mgrs,'n',adj_increment_m,num_gridlines)+incremental_points(west_center_mgrs,'s',adj_increment_m,num_gridlines)
#     w_boundary_points = sorted(w_boundary_points,key = lambda x: x[0][0])
#     s_boundary_points = incremental_points(south_center_mgrs,'e',adj_increment_m,num_gridlines)+incremental_points(south_center_mgrs,'w',adj_increment_m,num_gridlines)
#     s_boundary_points = sorted(s_boundary_points,key = lambda x: x[0][1])
#     n_boundary_points = incremental_points(north_center_mgrs,'e',adj_increment_m,num_gridlines)+incremental_points(north_center_mgrs,'w',adj_increment_m,num_gridlines)
#     n_boundary_points = sorted(n_boundary_points,key = lambda x: x[0][1])
#     n_boundary_points = realign_points(n_boundary_points)
#     s_boundary_points = realign_points(s_boundary_points)
#     w_boundary_points = realign_points(w_boundary_points)
#     e_boundary_points = realign_points(e_boundary_points)
#     lines = []
#     previous_nbp = []
#     for sbp in s_boundary_points:
#         easting = sbp[1][precision*-2:precision*-1]
#         best_lon_diff = np.inf
#         opposite_north_coord = ''
#         for nbp in n_boundary_points:
#             lon_diff = abs(sbp[0][1] - nbp[0][1])
#             if lon_diff < best_lon_diff and nbp[0] not in previous_nbp:
#                 best_lon_diff = lon_diff
#                 opposite_north_coord = nbp[0]
#         previous_nbp.append(opposite_north_coord)    
#         line = create_line([sbp[0],opposite_north_coord],'black',2,f'Easting: {easting}')
#         lines.append(line)
#     previous_wbp = []
#     for ebp in e_boundary_points:
#         northing = ebp[1][precision*-1:]
#         best_lat_diff = np.inf
#         opposite_west_coord = ''
#         for wbp in w_boundary_points:
#             lat_diff = abs(ebp[0][0] - wbp[0][0])
#             if lat_diff < best_lat_diff and wbp[0] not in previous_wbp:
#                 best_lat_diff = lat_diff
#                 opposite_west_coord = wbp[0]
#         previous_wbp.append(opposite_west_coord)
#         line = create_line([ebp[0],opposite_west_coord],'black',2,f'Northing: {northing}')
#         lines.append(line)               
#     return lines

# def create_lob_cluster(lob_cluster,points_lob_polygons,azimuths,sensor_error,min_distance_m,max_distance_m):
#     for index,plp in enumerate(points_lob_polygons):
#         lob_polygon = plot_LOB(plp,azimuths[index],sensor_error,min_distance_m,max_distance_m)
#         lob_cluster.add_child(lob_polygon)
#     return lob_cluster

# def plot_LOB(points_lob_polygon,azimuth,sensor_error,min_distance_m,max_distance_m):
#     lob_description = f'{azimuth}° with {sensor_error}° RMS error from {min_distance_m/1000:.1f} to {max_distance_m/1000:.1f}km ({get_polygon_area(points_lob_polygon):,.0f} acres of error)'
#     lob_polygon = create_polygon(points_lob_polygon,'black','blue',2,lob_description)
#     return lob_polygon

# def get_fix_coords(points_cut_polygons):
#     def get_polygon(points):
#         try:
#             p1, p2, p3, p4 = map(Point, points)
#             poly = Polygon(p1, p2, p3, p4)
#         except ValueError:
#             p1, p2, p3 = map(Point, points)
#             poly = Polygon(p1, p2, p3)
#         return poly
#     def get_intersection_coords(intersection):
#         x_coords = []; y_coords = []
#         for index,ip in enumerate(intersection):
#             try:
#                 x = round(float(intersection[index].x),13)
#                 y = round(float(intersection[index].y),13)
#                 if x not in x_coords and y not in y_coords:
#                     x_coords.append(x)
#                     y_coords.append(y)
#                     # print("x:",x); print("y:",y)
#             except AttributeError:
#                 x1 = float(intersection[index].p1.x)
#                 y1 = float(intersection[index].p1.y)
#                 if x1 not in x_coords and y1 not in y_coords:
#                     x_coords.append(x1)
#                     y_coords.append(y1)
#                     # print("x1:",x); print("y1:",y)
#                 x2 = float(intersection[index].p2.x)
#                 y2 = float(intersection[index].p2.y)
#                 if x2 not in x_coords and y2 not in y_coords:
#                     x_coords.append(x2)
#                     y_coords.append(y2)
#                     # print("x2:",x); print("y2:",y)
#         coords = [[x,y_coords[i]] for i,x in enumerate(x_coords)]
#         return coords
#     poly1 = get_polygon(points_cut_polygons[0])
#     poly2 = get_polygon(points_cut_polygons[1])
#     poly3 = get_polygon(points_cut_polygons[2])
#     print(poly1,poly2,poly3)
#     intersection_1_2 = poly1.intersection(poly2)
#     intersection_1_3 = poly1.intersection(poly3)
#     coords_intersection_1_2 = get_intersection_coords(intersection_1_2)
#     coords_intersection_1_3 = get_intersection_coords(intersection_1_3)
#     int_poly1 = get_polygon(coords_intersection_1_2)
#     int_poly2 = get_polygon(coords_intersection_1_3)
#     fix_intersection = int_poly1.intersection(int_poly2)
#     fix_coords = get_intersection_coords(fix_intersection)
#     return fix_coords

# def create_marker(marker_coords,marker_name,marker_color,marker_icon,marker_prefix='fa'):
#     marker = folium.Marker(marker_coords,
#                   # popup = f'<input type="text" value="{marker_coords[0]}, {marker_coords[1]}" id="myInput"><button onclick="myFunction()">Copy location</button>',
#                   popup = f'<input type="text" value="{convert_coords_to_mgrs(marker_coords)}" id="myInput"><button onclick="copyTextFunction()">Copy MGRS Grid</button>',
#                   tooltip=marker_name,
#                   icon=folium.Icon(color=marker_color,
#                                    icon_color='White',
#                                    icon=marker_icon,
#                                    prefix=marker_prefix)
#                   )
#     return marker

# def add_copiable_markers(m):
#     import jinja2
#     el = folium.MacroElement().add_to(m)
#     el._template = jinja2.Template("""
#         {% macro script(this, kwargs) %}
#         function copyTextFunction() {
#           /* Get the text field */
#           var copyText = document.getElementById("myInput");

#           /* Select the text field */
#           copyText.select();
#           copyText.setSelectionRange(0, 99999); /* For mobile devices */

#           /* Copy the text inside the text field */
#           document.execCommand("copy");
#         }
#         {% endmacro %}
#     """)
#     return m

# def create_polygon(points,line_color='black',shape_fill_color=None,line_weight=5,text=None):
#     iframe = folium.IFrame(text, width=250, height=75)
#     popup = folium.Popup(iframe, max_width=250)
#     polygon = folium.Polygon(locations = points,
#                    color=line_color,
#                    weight=line_weight,
#                    fill_color=shape_fill_color,
#                    popup = popup,
#                    name = 'test',
#                    overlay = False,
#                    control = True,
#                    show=False
#                    )
#     return polygon

# def add_tilelayers(m):
#     """
#     Adds tilelayers to Folium map object

#     Parameters:
#     ----------
#     m : Folium map object
#         Map object
    
#     Returns:
#     ----------
#     m : Folium map object
#         Map object

#     """
#     # folium.TileLayer(
#     #     tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
#     #     attr = 'Esri',
#     #     name = 'Satellite',
#     #     overlay = False,
#     #     control = True,
#     #     ).add_to(m)
#     folium.TileLayer(
#         tiles = 'openstreetmap',
#         name = 'Street Map',
#         overlay = False,
#         control = False,
#         min_zoom = 10,
#         max_zoom = 13,
#         ).add_to(m)
#     # folium.TileLayer(
#     #     tiles = 'Stamen Toner',
#     #     name = 'Black & White',
#     #     overlay = False,
#     #     control = True
#     #     ).add_to(m)
#     return m

# def create_map(center_coordinate,zs=16,min_z=0,max_z=18):
#     """
#     Creates a folium basemap for map product development.

#     Parameters
#     ----------
#     center_coordinate : list
#         Grid coordinate. Example: [lat,long]
#     zs : int, optional
#         Initial zoom level [0-18]. The default is 14.
#     min_z: int, optional
#         Minimum zoom level [0-18]. The default is 0.
#     max_z: int, optional
#         Maximum zoom level [0-18]. The default is 18

#     Returns
#     -------
#     m : Folium Map Obj
#         Folium basemap with satellite tile.

#     """
#     assert isinstance(center_coordinate,list), 'Coordinate input must be a list.'
#     assert len(center_coordinate) == 2, 'Coordinate input must be of length 2.'
#     assert min_z <= max_z, 'The max zoom must be greater than the min zoom'
#     m = folium.Map(
#         location=center_coordinate,
#         tiles = None,
#         attr = '2ABCT CEMA',
#         zoom_start=zs,
#         min_zoom = 10,
#         max_zoom = 13,
#         control_scale = True,
#         control_zoom = False,)
#     return m

# def get_path_loss_description(path_loss_coeff):
#     """
#     Return description of RF path-loss situation given a coefficient

#     Parameters:
#     ----------
#     path_loss_coeff : float
#         Path-Loss Coefficient, at least 2
    
#     Returns:
#     ----------
#     path_loss_description : str
#         Description of RF path-loss situation

#     """   
#     if path_loss_coeff <= 3:
#         path_loss_description = 'Open Terrain'
#     elif path_loss_coeff <= 4:
#         path_loss_description = 'Moderate Foliage'
#     elif path_loss_coeff > 4:
#         path_loss_description = 'Dense Foliage'
#     return path_loss_description

# def get_accuracy_improvement_of_cut(lob1_error,lob2_error,cut_error):
#     return 1 - (cut_error/(lob1_error+lob2_error-cut_error))

# def get_accuracy_improvement_of_fix(fix_area,cut_areas):
#     return 1-(fix_area/(cut_areas[0] + cut_areas[1] + cut_areas[2] - 2*fix_area))

# def get_elevation_data(coord_list):
#     import csv, time
#     def read_elevation_data(src_file):
#         with open(src_file,mode='r',newline='') as elev_data_file:
#             csv_reader = csv.reader(elev_data_file)
#             csv_data = []
#             for row in csv_reader:
#                 csv_data.append(row)
#         return csv_data
#     def save_elevation_data(save_file,csv_data):
#         with open(save_file,mode='w',newline='') as elev_data_file:
#             csv_writer = csv.writer(elev_data_file)
#             csv_writer.writerows(csv_data)
#     coord_elev_data=[]
#     src_file = rf'{os.path.realpath(os.path.dirname(__file__))}\elevation\elev_data.csv'
#     cp_file = rf'{os.path.realpath(os.path.dirname(__file__))}\elevation\elev_data_preop_copy.csv'
#     if os.path.getsize(src_file) >= os.path.getsize(cp_file):
#         shutil.copyfile(src_file, cp_file)
#     request_string = ''; request_list = []; request_list_conmprehension = []
#     csv_data = read_elevation_data(src_file)
#     if len(csv_data) > 1:
#         mgrs_list = [d[-2] for d in csv_data[1:]]
#         elevation_list = [d[-1] for d in csv_data[1:]]
#     else:
#         mgrs_list = []; elevation_list = []
#     num_coords_in_request = 0; max_request_length = 50; num_stored = 0; num_requested = 0
#     for i,coord in enumerate(coord_list):
#         mgrs = convert_coords_to_mgrs(coord,precision=4)
#         if mgrs in mgrs_list:
#             elevation = elevation_list[mgrs_list.index(mgrs)]
#             coord_elev_data.append([coord[0],coord[1],mgrs,elevation])
#             num_stored += 1
#             continue
#         else:
#             request_list.append(','.join([str(c) for c in coord]))
#             num_coords_in_request += 1
#             num_requested += 1
#         if num_coords_in_request >= max_request_length:
#             request_list_conmprehension.append(request_list)
#             request_list = []
#             num_coords_in_request = 0
#             max_request_length = np.random.uniform(48,52)
#     if num_requested + num_stored > 0: print(f'{num_stored:,.2f} ({num_stored/(num_requested + num_stored)*100:,.2f}%) tiles already in database')
#     if num_requested > num_stored and not check_internet_connection(): return []
#     if len(request_list) > 0: request_list_conmprehension.append(request_list)
#     if len(request_list_conmprehension) > 0 and len(request_list_conmprehension[0]) > 0:
#         for i,requested_coords in enumerate(request_list_conmprehension):
#             print(f"Request {i+1} of {len(request_list_conmprehension)}")
#             csv_data = read_elevation_data(src_file)
#             request_string = '|'.join(requested_coords)
#             request = f"https://api.open-elevation.com/api/v1/lookup?locations={request_string}"
#             try:
#                 response = requests.get(request)
#                 for result in response.json()['results']:
#                     latitude = result['latitude']
#                     longitude = result['longitude']
#                     elevation = result['elevation']
#                     mgrs_8digit = convert_coords_to_mgrs([latitude,longitude],precision=4)
#                     coord_elev_data.append([latitude,longitude,mgrs_8digit,elevation])
#                     csv_data.append([latitude,longitude,mgrs_8digit,elevation])
#                 print(f'Success: {len(requested_coords)} datapoints added to elevation database')
#             except:
#                 print(f"Elevation request {i+1} failed.")
#             save_elevation_data(src_file,csv_data)
#             time.sleep(np.random.exponential(0.125))
#     return coord_elev_data

# def plot_elevation_data(coord_elev_data,target_coords=None,title_args=None):
#     import datetime
#     if coord_elev_data == None or len(coord_elev_data) == 0: return 0
#     def get_dist_interval(target_distance,dist_interval):
#         if target_distance is None: return -1
#         for i, di in enumerate(dist_interval[:-1]):
#             if int(di) <= target_distance < int(dist_interval[i+1]):
#                 return i
#         return -1
#     # input maybe title?, maybe filename?
#     import matplotlib.pyplot as plt
#     elev_list = [float(x[-1]) for x in coord_elev_data]
#     base_reg=0
#     sensor_coord = [coord_elev_data[0][0],coord_elev_data[0][1]]
#     sensor_mgrs = convert_coords_to_mgrs(sensor_coord)
#     far_side_coord = [coord_elev_data[-1][0],coord_elev_data[-1][1]]
#     far_side_coord_mgrs = convert_coords_to_mgrs(far_side_coord)
#     distance = int(get_distance_between_coords(sensor_coord,far_side_coord))
#     coord_interval = int(distance/len(elev_list))
#     dist_interval = list(range(0,distance,coord_interval))
#     target_dist_indices = []
#     if target_coords is not None:
#         for i,target_coord in enumerate(target_coords):
#             if i == len(target_coords)-1: target_dist_indices.append(-1); break
#             target_dist = get_distance_between_coords(sensor_coord,target_coord)
#             target_dist_index = get_dist_interval(target_dist,dist_interval)
#             target_dist_indices.append(target_dist_index)
#     while len(dist_interval) > len(elev_list):
#         dist_interval = dist_interval[:-1]
#     while len(dist_interval) < len(elev_list):
#         dist_interval = dist_interval + [dist_interval[-1]+coord_interval]
#     try:   
#         plt.figure(figsize=(10,4))
#         # plt.style.use('ggplot')
#         plt.style.use('classic')
#         plt.plot(dist_interval,elev_list)
#         min_elev = min(elev_list)
#         max_elev = max(elev_list)
#         plt.plot([0,dist_interval[-1]],[min_elev,min_elev],'--g',label='min: '+str(min_elev)+' m')
#         plt.plot([0,dist_interval[-1]],[max_elev,max_elev],'--r',label='max: '+str(max_elev)+' m')
#         # plt.scatter([0],[elev_list[0]],label='Sensor',color='blue',marker='^',s=100)
#         buffer = int(min_elev *.25)
#         plt.ylim(int(min_elev - buffer), int(max_elev + buffer))
#         plt.xlim(dist_interval[0],dist_interval[-1])
#         if target_coords is not None:
#             target_dists = []; target_elevations = []
#             for i,target_coord in enumerate(target_coords):
#                 if i == len(target_coords)-1: target_dists.append(dist_interval[-1]); target_elevations.append(elev_list[-1]); break
#                 target_dist = get_distance_between_coords(sensor_coord,target_coord)
#                 target_dists.append(target_dist)
#                 target_elevations.append(elev_list[target_dist_indices[i]])
#             plt.vlines(target_dists,[min_elev - buffer for td in target_dists],[max_elev + buffer for td in target_dists],colors=['black' for dt in target_dists],linestyles=['dashed' for dt in target_dists],label='Target Distances')
#             plt.scatter(target_dists,target_elevations,label='Possible Targets',color='red',marker='D',s=100)
#         plt.fill_between(dist_interval,elev_list,base_reg,alpha=0.1,color='green')
#         plt.xlabel("Distance (m)")
#         plt.ylabel("Elevation (m)")
#         plt.grid()
#         plt.legend(fontsize='small')
#         if title_args is None:
#             plt.title(f'Elevation data from {sensor_mgrs} to {far_side_coord_mgrs}')
#         else:
#             if len(title_args) == 1:
#                 plt.title(f'Elevation data from {title_args[0]} to {far_side_coord_mgrs}')
#             elif len(title_args) == 2:
#                 plt.title(f'Elevation data from {title_args[0]} to {title_args[1]}')
#         dt = str(datetime.datetime.today()).split()[0].replace('-','')
#         num = 0
#         output_filename = (rf'{os.path.realpath(os.path.dirname(__file__))}\elevation_plots\{dt}_elevation_data_{num:02}.png')
#         while os.path.exists(output_filename):
#             num +=1 
#             output_filename = (rf'{os.path.realpath(os.path.dirname(__file__))}\elevation_plots\{dt}_elevation_data_{num:02}.png')
#         plt.savefig(output_filename)
#         plt.show()
#     except AttributeError as e:
#         return 0

# '''https://api.open-elevation.com/api/v1/lookup?locations=51.24885624303748,15.570668663974097'''


