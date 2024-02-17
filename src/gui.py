#!/usr/bin/env python3

import customtkinter
from CTkMessagebox import CTkMessagebox
import numpy as np
import os
from PIL import Image, ImageTk
import sys
import threading
import tkinter
from tkinter import END
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from tkintermapview import TkinterMapView
from main import get_coords_from_LOBs, get_emission_distance, get_polygon_area, get_distance_between_coords, get_line, get_center_coord, plot_elevation_data, check_internet_connection
from main import convert_mgrs_to_coords, organize_polygon_coords, convert_coords_to_mgrs, check_for_intersection, get_intersection, get_elevation_data, is_port_in_use

customtkinter.set_default_color_theme("dark-blue")

import sys
import trace
import time
import concurrent.futures


class App(customtkinter.CTk):
    """
    Custom Tkinter Application Class for GUI support
    """
    # preset application name
    APP_NAME = "2ABCT CEMA Electromagnetic Warfare Targeting Application"
    # preset aspect ratio of application display
    ASPECT_RATIO = 16/9
    # preset width of GUI dislay
    WIDTH = 1200
    # preset height of GUI display (dependent on WIDTH and ASPECT_RATIO)
    HEIGHT = int(WIDTH/ASPECT_RATIO)
    # preset local port that is hosting the map server
    MAP_SERVER_PORT = 8080
    # preset default input values
    DEFAULT_VALUES = {
        "Sensor 1 MGRS": "11SNV4178910362",
        "Sensor 1 PWR Received": -75,
        "Sensor 1 LOB": 105,
        "Sensor 2 MGRS": "11SNV4314711067",
        "Sensor 2 PWR Received": -78,
        "Sensor 2 LOB": 165,
        "Sensor 3 MGRS": "X",
        "Sensor 3 PWR Received": -79,
        "Sensor 3 LOB": 275,
        "Frequency":32,
        "Min ERP":0.005,
        "Max ERP":50,
        "Path-Loss Coefficient":4,
        "Path-Loss Coefficient Description":"Moderate Foliage"
    }

    def __init__(self, *args, **kwargs):
        """
        Defines application initialization attributes
        """
        super().__init__(*args, **kwargs)
        # set title of application 
        self.title(App.APP_NAME)
        # set geometry of GUI display to presets
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        # set minimum allowed size of GUI display as presets
        self.minsize(App.WIDTH, App.HEIGHT)
        # call window delete protocol upon app closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # bind Control-q keystroke to close the application
        self.bind("<Control-q>", self.on_closing)
        # add Apple MAC compatability to quit command
        self.createcommand('tk::mac::Quit', self.on_closing)
        # define source file directory
        self.src_directory = os.path.dirname(os.path.abspath(__file__))
        # define icon file directory
        self.icon_directory = "\\".join(self.src_directory.split('\\')[:-1])+"\\icons"
        # define map tile directory
        self.tile_directory = "\\".join(self.src_directory.split('\\')[:-1])+"\\maptiles\\ESRI"
        # start map server thread if map server is not currently running
        if not is_port_in_use(App.MAP_SERVER_PORT):
            # create map server thread
            self.map_server_thread = threading.Thread(target=self.map_server,args=([self.tile_directory]))
            # set daemon attribute to True
            self.map_server_thread.daemon = True
            # start map server thread
            self.map_server_thread.start()
        # define target image icon
        self.target_image = ImageTk.PhotoImage(Image.open(os.path.join(self.icon_directory, "suspected_hostile.png")).resize((40, 40)))
        # define generic EWT icon
        self.ew_team_image = ImageTk.PhotoImage(Image.open(os.path.join(self.icon_directory, "ew_team.png")).resize((40, 40)))
        # define EWT 1 icon
        self.ew_team1_image = ImageTk.PhotoImage(Image.open(os.path.join(self.icon_directory, "ew_team_1.png")).resize((40, 40)))
        # define EWT 2 icon
        self.ew_team2_image = ImageTk.PhotoImage(Image.open(os.path.join(self.icon_directory, "ew_team_2.png")).resize((40, 40)))
        # define EWT 3 icon
        self.ew_team3_image = ImageTk.PhotoImage(Image.open(os.path.join(self.icon_directory, "ew_team_3.png")).resize((40, 40)))
        # define blank image
        self.blank_image = ImageTk.PhotoImage(Image.open(os.path.join(self.icon_directory, "empty.png")).resize((40, 40)))
        # define initial marker list
        self.marker_list = []
        # define initial polygon list
        self.polygon_list = []
        # define initial EW marker list
        self.ewt_marker_list = []
        # define initial target marker list
        self.target_marker_list = []
        # define path list
        self.path_list = []
        # define default path loss coefficient
        self.path_loss_coeff = 4
        # define default receiver gains
        self.sensor1_receiver_gain_dBi = 0
        self.sensor2_receiver_gain_dBi = 0
        self.sensor3_receiver_gain_dBi = 0
        # define default sensor errors
        self.sensor1_error = 6
        self.sensor2_error = 6
        self.sensor3_error = 6
        # define default boolean values
        self.single_lob_bool = False
        self.cut_bool = False
        # define default target class
        self.target_class = ''

        # ============ create two CTkFrames ============

        # configure first column
        self.grid_columnconfigure(0, weight=0)
        # configure second column (with prefered weight)
        self.grid_columnconfigure(1, weight=1)
        # configure row
        self.grid_rowconfigure(0, weight=1)
        # define column 1 (input/output column) parameters
        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        # define column 2 (map column) parameters
        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=10, padx=10, sticky="nsew")

        # ============ Input/Ouput Frame ============
        # define frame header attributes
        self.label_header = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"EW TARGETING DATA", 
            text_color='green')
        # assign frame header grid position
        self.label_header.grid(
            row=0,
            rowspan=1,
            column=0,
            columnspan=2, 
            padx=(0,0), 
            pady=(5,5))
        # define sensor option label attributes
        self.label_sensor_option = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"EW Sensor:", 
            text_color='white')
        # assign sensor option label grid position
        self.label_sensor_option.grid(
            row=self.label_header.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define sensor option dropdown attributes
        self.option_sensor = customtkinter.CTkOptionMenu(
            master=self.frame_left, 
            values=["VROD/VMAX","BEAST+"],
            fg_color='blue',
            button_color='blue',
            command=self.change_sensor)
        # assign sensor option dropdown grid position
        self.option_sensor.grid(
            row=self.label_header.grid_info()["row"]+1, 
            column=1, 
            rowspan=1, 
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define sensor 1 mgrs label
        self.label_sensor1_mgrs = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"EWT 1 Location:", 
            text_color='white')
        # assign sensor 1 mgrs label grid position
        self.label_sensor1_mgrs.grid(
            row=self.label_sensor_option.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define sensor 1 mgrs attributes
        self.sensor1_mgrs = customtkinter.CTkEntry(
            master=self.frame_left,
            placeholder_text="MGRS")
        # assign sensor 1 mgrs grid position
        self.sensor1_mgrs.grid(
            row=self.option_sensor.grid_info()["row"]+1, 
            column=1, 
            rowspan=1, 
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define sensor 1 LOB label
        self.label_sensor1_lob = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"EWT 1 LOB:", 
            text_color='white')
        # assign sensor 1 LOB label grid position
        self.label_sensor1_lob.grid(
            row=self.sensor1_mgrs.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define sensor 1 LOB attributes
        self.sensor1_lob = customtkinter.CTkEntry(
            master=self.frame_left,
            placeholder_text="Degrees (°)")
        # assign sensor 1 LOB grid position
        self.sensor1_lob.grid(
            row=self.sensor1_mgrs.grid_info()["row"]+1, 
            column=1, 
            rowspan=1, 
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define sensor 1 received power label attributes
        self.label_sensor1_Rpwr = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"EWT 1 Power Received:", 
            text_color='white')
        # assign sensor 1 received power label grid position
        self.label_sensor1_Rpwr.grid(
            row=self.sensor1_lob.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define sensor 1 received power attributes
        self.sensor1_Rpwr = customtkinter.CTkEntry(
            master=self.frame_left,
            placeholder_text="dBm")
        # define sensor 1 receiver power grid position
        self.sensor1_Rpwr.grid(
            row=self.sensor1_lob.grid_info()["row"]+1, 
            column=1, 
            rowspan=1, 
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define sensor 2 mgrs label attributes
        self.label_sensor2_mgrs = customtkinter.CTkLabel(
            master = self.frame_left, 
            text=f"EWT 2 Location:", 
            text_color='white')
        # assign sensor 3 mgrs label grid position
        self.label_sensor2_mgrs.grid(
            row=self.sensor1_Rpwr.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define sensor 2 mgrs attributes
        self.sensor2_mgrs = customtkinter.CTkEntry(
            master=self.frame_left,
            placeholder_text="MGRS")
        # assign sensor 2 mgrs grid positon
        self.sensor2_mgrs.grid(
            row=self.sensor1_Rpwr.grid_info()["row"]+1, 
            column=1, 
            rowspan=1, 
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define sensor 2 LOB label attributes
        self.label_sensor2_lob = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"EWT 2 LOB:", 
            text_color='white')
        # assign sensor 2 LOB label grid position
        self.label_sensor2_lob.grid(
            row=self.sensor2_mgrs.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define sensor 2 LOB attributes
        self.sensor2_lob = customtkinter.CTkEntry(
            master=self.frame_left,
            placeholder_text="Degrees (°)")
        # assign sensor 2 LOB grid position
        self.sensor2_lob.grid(
            row=self.sensor2_mgrs.grid_info()["row"]+1, 
            column=1, 
            rowspan=1, 
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define sensor 2 received power attributes
        self.label_sensor2_Rpwr = customtkinter.CTkLabel(
            self.frame_left, 
            text=f"EWT 2 Power Received:", 
            text_color='white')
        # assign sensor 2 received power grid position
        self.label_sensor2_Rpwr.grid(
            row=self.sensor2_lob.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define sensor 2 received power attributes
        self.sensor2_Rpwr = customtkinter.CTkEntry(
            master=self.frame_left,
            placeholder_text="dBm")
        # assign sensor 2 received power grid position
        self.sensor2_Rpwr.grid(
            row=self.sensor2_lob.grid_info()["row"]+1, 
            column=1, 
            rowspan=1, 
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define sensor 3 mgrs label attributes
        self.label_sensor3_mgrs = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"EWT 3 Location:", 
            text_color='white')
        # assign sensor 3 mgrs label grid position
        self.label_sensor3_mgrs.grid(
            row=self.sensor2_Rpwr.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define sensor 3 mgrs attributes
        self.sensor3_mgrs = customtkinter.CTkEntry(
            master=self.frame_left,
            placeholder_text="MGRS")
        # assign sensor 3 mgrs grid position
        self.sensor3_mgrs.grid(
            row=self.sensor2_Rpwr.grid_info()["row"]+1, 
            column=1, 
            rowspan=1, 
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define sensor 3 LOB label attributes
        self.label_sensor3_lob = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"EWT 3 LOB:", 
            text_color='white')
        # assign sensor 3 LOB label grid position
        self.label_sensor3_lob.grid(
            row=self.sensor3_mgrs.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define sensor 3 LOB attributes
        self.sensor3_lob = customtkinter.CTkEntry(
            master=self.frame_left,
            placeholder_text="Degrees (°)")
        # assign sensor 3 LOB grid position
        self.sensor3_lob.grid(
            row=self.sensor3_mgrs.grid_info()["row"]+1, 
            rowspan=1,
            column=1, 
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define sensor 3 received power label attributes
        self.label_sensor3_Rpwr = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"EWT 3 Power Received:", 
            text_color='white')
        # assign sensor 3 recieved power label grid position
        self.label_sensor3_Rpwr.grid(
            row=self.sensor3_lob.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define sensor 3 received power attributes
        self.sensor3_Rpwr = customtkinter.CTkEntry(
            master=self.frame_left,
            placeholder_text="dBm")
        # assign sensor 3 received power grid position
        self.sensor3_Rpwr.grid(
            row=self.sensor3_lob.grid_info()["row"]+1, 
            rowspan=1,
            column=1, 
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define target frequency label attributes
        self.label_frequency = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"Frequency:",
            text_color='white')
        # assign target frequency label grid position
        self.label_frequency.grid(
            row=self.sensor3_Rpwr.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define target frequency attributes
        self.frequency = customtkinter.CTkEntry(
            master=self.frame_left,
            placeholder_text="MHz")
        # assign target frequency grid positon
        self.frequency.grid(
            row=self.sensor3_Rpwr.grid_info()["row"]+1, 
            rowspan=1,
            column=1, 
            columnspan=1, 
            padx=(0,), 
            pady=(0,0))
        # define min ERP label attributes
        self.label_min_ERP = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"Minimum ERP:", 
            text_color='white')
        # assign min ERP label grid position
        self.label_min_ERP.grid(
            row=self.frequency.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define min ERP attributes
        self.min_ERP = customtkinter.CTkEntry(
            master=self.frame_left,
            placeholder_text="Wattage (W)")
        # assign min ERP grid position
        self.min_ERP.grid(
            row=self.frequency.grid_info()["row"]+1, 
            rowspan=1,
            column=1, 
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define max ERP label attributes
        self.label_max_ERP = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"Maximum ERP:", 
            text_color='white')
        # assign max ERP grid position
        self.label_max_ERP.grid(
            row=self.min_ERP.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define max ERP attributes
        self.max_ERP = customtkinter.CTkEntry(
            master=self.frame_left,
            placeholder_text="Wattage (W)")
        # assign max ERP grid position
        self.max_ERP.grid(
            row=self.min_ERP.grid_info()["row"]+1, 
            rowspan=1,
            column=1, 
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define path-loss coefficient label attributes
        self.label_path_loss_coeff = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"Path-Loss Coefficient:", 
            text_color='white')
        # assign path-loss coefficient label grid position
        self.label_path_loss_coeff.grid(
            row=self.max_ERP.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define path-loss coefficient option attributes
        self.option_path_loss_coeff = customtkinter.CTkOptionMenu(
            master=self.frame_left, 
            values=["Free Space (Theoretical)","Light Foliage","Light-Moderate Foliage","Moderate Foliage","Moderate-Dense Foliage","Dense Foliage"],
            fg_color='green',
            button_color='green',
            command=self.change_path_loss)
        # assign path-loss coefficient option grid position
        self.option_path_loss_coeff.grid(
            row=self.max_ERP.grid_info()["row"]+1,
            rowspan=1, 
            column=1, 
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define buffer column attributes
        self.buffer = customtkinter.CTkLabel(
            master=self.frame_left,
            text='')
        # assign buffer column grid position
        self.buffer.grid(
            row=self.option_path_loss_coeff.grid_info()["row"]+1,
            column=1,
            columnspan=2, 
            padx=(0,0), 
            pady=(0,0))
        # apply a greater weight to the buffer row to create spacing
        self.frame_left.grid_rowconfigure(self.buffer.grid_info()['row'], weight=2)
        # define target grid label attributes
        self.label_target_grid = customtkinter.CTkLabel(
            self.frame_left, 
            text=f"TARGET GRID {self.target_class}".strip()+":", 
            text_color='red')
        # assign target grid label grid position
        self.label_target_grid.grid(
            row=self.buffer.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define target grid attributes
        self.target_grid = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"NO TARGET",
            text_color='yellow')
        # assign target grid grid position
        self.target_grid.grid(
            row=self.buffer.grid_info()["row"]+1,
            rowspan=1,
            column=1, 
            columnspan=1,
            padx=(0,0), 
            pady=(0,0))
        # define sensor 1 distance label attributes
        self.label_sensor1_distance = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"Distance from EWT 1:",
            text_color='white')
        # assign sensor 1 distance label grid position
        self.label_sensor1_distance.grid(
            row=self.target_grid.grid_info()["row"]+1,
            rowspan=1,
            column=0, 
            columnspan=1,
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define sensor 1 distance attributes
        self.sensor1_distance = customtkinter.CTkLabel(
            master=self.frame_left, 
            text='N/A',
            text_color='white')
        # assign sensor 1 distance grid position
        self.sensor1_distance.grid(
            row=self.target_grid.grid_info()["row"]+1,
            rowspan=1,
            column=1, 
            columnspan=1,
            padx=(0,0), 
            pady=(0,0))
        # define sensor 2 distance label attributes
        self.label_sensor2_distance = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"Distance from EWT 2:",
            text_color='white')
        # assign sensor 2 distance label grid positon
        self.label_sensor2_distance.grid(
            row=self.sensor1_distance.grid_info()["row"]+1,
            rowspan=1,
            column=0, 
            columnspan=1,
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define sensor 2 distance attributes
        self.sensor2_distance = customtkinter.CTkLabel(
            master=self.frame_left, 
            text='N/A',
            text_color='white')
        # assign sensor 2 distance grid position
        self.sensor2_distance.grid(
            row=self.sensor1_distance.grid_info()["row"]+1,
            rowspan=1,
            column=1, 
            columnspan=1,
            padx=(0,0), 
            pady=(0,0))
        # define sensor 3 distance label attributes
        self.label_sensor3_distance = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"Distance from EWT 3:",
            text_color='white')
        # assign sensor 3 distance label grid positon
        self.label_sensor3_distance.grid(
            row=self.sensor2_distance.grid_info()["row"]+1,
            rowspan=1,
            column=0, 
            columnspan=1,
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define sensor 3 distance attributes
        self.sensor3_distance = customtkinter.CTkLabel(
            master=self.frame_left, 
            text='N/A',
            text_color='white')
        # assign sensor 3 distance grid position
        self.sensor3_distance.grid(
            row=self.sensor2_distance.grid_info()["row"]+1,
            rowspan=1,
            column=1, 
            columnspan=1,
            padx=(0,0), 
            pady=(0,0))
        # define target error label attributes
        self.label_target_error = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"Calculation Error:",
            text_color='white')
        # assign target error label grid position
        self.label_target_error.grid(
            row=self.sensor3_distance.grid_info()["row"]+1,
            rowspan=1,
            column=0, 
            columnspan=1,
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define target error attributes
        self.target_error = customtkinter.CTkLabel(
            master=self.frame_left, 
            text=f"N/A",
            text_color='white')
        # assign target error attributes grid position
        self.target_error.grid(
            row=self.sensor3_distance.grid_info()["row"]+1,
            rowspan=1,
            column=1, 
            columnspan=1,
            padx=(0,0), 
            pady=(0,0))
        # define clear entries button 
        self.button_clear_entries = customtkinter.CTkButton(
            master=self.frame_left, 
            text="CLEAR ENTRIES",
            fg_color='red',
            command = self.clear_entries)
        # assign clear entries button grid position
        self.button_clear_entries.grid(
            row=self.target_error.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define calculate button attributes
        self.button_calculate = customtkinter.CTkButton(
            master=self.frame_left, 
            text="CALCULATE",
            fg_color='blue',
            command = self.ewt_function)
        # assign calculate button grid position
        self.button_calculate.grid(
            row=self.target_error.grid_info()["row"]+1,
            rowspan=1,
            column=1,
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define log entries button 
        self.button_log_data = customtkinter.CTkButton(
            master=self.frame_left, 
            text="LOG DATA",
            fg_color='green',
            command = self.log_target_data)
        # assign log entries button grid position
        self.button_log_data.grid(
            row=self.button_clear_entries.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define elevation survey button attributes
        self.button_elevation_survey = customtkinter.CTkButton(
            master=self.frame_left, 
            text="Elevation Survey",
            fg_color='brown',
            command = self.elevation_survey)
        # assign elevation survey button grid position
        self.button_elevation_survey.grid(
            row=self.button_calculate.grid_info()["row"]+1,
            rowspan=1,
            column=1,
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))

        # ============ frame_right ============
        
        # configure first row with low weight
        self.frame_right.grid_rowconfigure(0, weight=0)
        # configure second row with high weight
        self.frame_right.grid_rowconfigure(1, weight=1)
        # configure first column with low weight
        self.frame_right.grid_columnconfigure(0, weight=0)
        # configure second column with high weight
        self.frame_right.grid_columnconfigure(1, weight=1)
        # configure third column with low weight
        self.frame_right.grid_columnconfigure(2, weight=0)
        # configure forth column with low weight
        self.frame_right.grid_columnconfigure(3, weight=0)
        # define map widget attributes
        self.map_widget = TkinterMapView(
            master=self.frame_right, 
            corner_radius=0)
        # assign map widget grid position
        self.map_widget.grid(
            row=1, 
            rowspan=1, 
            column=0, 
            columnspan=4,
            padx=(0, 0), 
            pady=(0, 0),
            sticky="nswe")
        # set map widget default tile server
        self.map_widget.set_tile_server(
            tile_server="http://localhost:8080/{z}/{x}/{y}.png",
            max_zoom=22)
        # set initial zoom level for map tile server
        self.map_widget.set_zoom(14)
        # define mgrs entry form attributes
        self.mgrs_entry = customtkinter.CTkEntry(
            master=self.frame_right,
            placeholder_text="Insert MGRS Grid")
        # assign mgrs entry form grid position
        self.mgrs_entry.grid(
            row=0, 
            column=0, 
            padx=(12, 0), 
            pady=12,
            sticky="we")
        # bind mgrs entry keystroke to search function
        self.mgrs_entry.bind("<Return>", self.search_event)
        # define search button attributes
        self.button_search = customtkinter.CTkButton(
            master=self.frame_right,
            text="Search",
            width=90,
            command=self.search_event)
        # assign search button grid position
        self.button_search.grid(
            row=0,
            rowspan=1,
            column=1, 
            columnspan=1, 
            padx=(12, 0), 
            pady=12,
            sticky="w")
        # define clear markers button attributes
        self.button_clear_markers = customtkinter.CTkButton(
            master=self.frame_right,
            text="Clear Markers",
            command=self.clear_markers)
        # assign clear markers button grid position
        self.button_clear_markers.grid(
            row=0, 
            rowspan=1,
            column=2, 
            columnspan=1, 
            padx=(12, 0), 
            pady=12,
            sticky="e")
        # define map option dropdown attributes
        self.map_option_menu = customtkinter.CTkOptionMenu(
            master=self.frame_right, 
            values=["Local Map Server", "OpenStreetMap", "Google Street", "Google Satellite"],
            command=self.change_map)
        # assign map option dropdown grid position
        self.map_option_menu.grid(
            row=0,
            rowspan=1,
            column=3, 
            columnspan=1, 
            padx=(12, 0), 
            pady=12,
            sticky="e")
        # set map widget default address
        self.map_widget.set_address("Fort Irwin")
        # set map widget default server
        self.map_option_menu.set("Local Map Server")
        # set default path-loss coefficient
        self.option_path_loss_coeff.set('Moderate Foliage')
        # define right-click attributes
        self.map_widget.add_right_click_menu_command(
            label="Add Marker",
            command=self.add_marker_event,
            pass_coords=True)
    def ewt_function(self):
        """
        Function to calculate target location given EWT input(s)
        """
        # resets single lob boolean value to FALSE, allowing multiple EWT input
        self.single_lob_bool = False
        # delete all previous polygons from map widget
        self.map_widget.delete_all_polygon()
        # delete all previous EWTs from map widget
        self.clear_ewt_markers()
        # delete all previous target markers from map widget
        self.clear_target_markers()
        # set values without option for user input 
        sensor1_receiver_height_m = 2
        sensor2_receiver_height_m = 2
        transmitter_gain_dBi = 0
        transmitter_height_m = 2
        temp_f = 70
        # try to read sensor 1 mgrs value
        try:
            # get input from sensor1_mgrs input field
            sensor1_mgrs = str(self.sensor1_mgrs.get()).strip()
            # assess whether the input MGRS value is valid
            if self.check_mgrs_input(sensor1_mgrs):
                # if MGRS value is valid, pass on to next portion of function code
                pass
            else:
                # if MGRS is invalid, give user the option to re-input or use default value
                choice = self.input_error(category='Sensor 1 Grid',msg=f'Invalid Input {sensor1_mgrs}')
                # assess if user wishes to use the default value or end function
                if choice:
                    # clear the previous sensor 1 MGRS input
                    self.sensor1_mgrs.delete(0,END)
                    # insert the default sensor 1 MGRS value
                    self.sensor1_mgrs.insert(0,App.DEFAULT_VALUES['Sensor 1 MGRS'])
                    # set local Sensor 1 MGRS value to default value
                    sensor1_mgrs = App.DEFAULT_VALUES['Sensor 1 MGRS']
                # if user chooses to re-input the sensor 1 MGRS value
                else:
                    # end function
                    return 0
        # exception handling for ValueError
        except ValueError:
            # if value error occurs, set Sensor 1 MGRS value to None
            sensor1_mgrs = None
        # try to read sensor 1 LOB value
        try:
            # get input from Sensor 1 LOB field
            sensor1_grid_azimuth = int(self.sensor1_lob.get())
            # assess feasiblity of Sensor 1 LOB input value
            if sensor1_grid_azimuth < 0 or sensor1_grid_azimuth > 360:
                raise ValueError
        # exception handling for ValueError
        except ValueError:
            # give user option to re-input value or use the default Sensor 1 LOB value
            choice = self.input_error(category='Sensor 1 Grid Azimuth',msg=f'Invalid Input')
            # if user chooses to use the default Sensor 1 LOB value
            if choice:
                # clear Sensor 1 LOB input field
                self.sensor1_lob.delete(0,END)
                # insert default Sensor 1 LOB value
                self.sensor1_lob.insert(0,App.DEFAULT_VALUES['Sensor 1 LOB'])
                # set local Sensor 1 LOB value to default value
                sensor1_grid_azimuth = App.DEFAULT_VALUES['Sensor 1 LOB']
            # if user choose to re-input the Sensor 1 LOB value
            else:
                # end function
                return 0
        # try to read the Sensor 1 PWR Received value
        try:
            # get input from Sensor 1 PWR Received input field
            sensor1_power_received_dBm = int(self.sensor1_Rpwr.get())
            # assess validity of Sensor 1 power received input value
            if sensor1_power_received_dBm > 0:
                # exception handling for ValueError
                raise ValueError
        # exception for ValueError
        except ValueError:
            # give user option to re-input value or use the default Sensor 1 PWR received value
            choice = self.input_error(category='Sensor 1 Power Received',msg=f'Invalid Input')
            # if user chooses to use the default Sensor 1 PWR Received value
            if choice:
                # clear the Sensor 1 PWR Received value
                self.sensor1_Rpwr.delete(0,END)
                # insert the default Sensor 1 PWR Received value
                self.sensor1_Rpwr.insert(0,App.DEFAULT_VALUES['Sensor 1 PWR Received'])
                # set local Sensor 1 PWR Received value to default value 
                sensor1_power_received_dBm = App.DEFAULT_VALUES['Sensor 1 PWR Received']
            # if user chooses to re-input the Sensor 1 PWR Received value
            else:
                # end function
                return 0
        # try to read the Sensor 2 MGRS value
        try:
            # if Single LOB boolean value is FALSE
            if not self.single_lob_bool:
                # get input from Sensor 2 MGRS field
                sensor2_mgrs = str(self.sensor2_mgrs.get()).strip()
                # assess if Sensor 2 MGRS input is valid
                if self.check_mgrs_input(sensor2_mgrs):
                    # if MGRS value is valid, pass on to next portion of function code
                    pass
                else:
                    # if MGRS is invalid, give user the option to re-input or use default value
                    choice = self.input_error(category='Sensor 2 Grid',msg=f'Invalid Input {sensor2_mgrs}',single_lob_option=True)
                    # if user chooses to use default Sensor 2 MGRS value
                    if choice == True:
                        # clear Sensor 2 MGRS input field
                        self.sensor2_mgrs.delete(0,END)
                        # insert default Sensor 2 MGRS value into field
                        self.sensor2_mgrs.insert(0,App.DEFAULT_VALUES['Sensor 2 MGRS'])
                        # set local Sensor 2 MGRS value to default value
                        sensor2_mgrs = App.DEFAULT_VALUES['Sensor 2 MGRS']
                    # if user chooses to re-input the Sensor 2 MGRS value
                    elif choice == False:
                        # end function
                        return 0
                    # if user chooses to utilize only a single LOB
                    elif choice == 'SL':
                        # set Single LOB boolean value to TRUE
                        self.single_lob_bool = True
                        # set Sensor 2 MGRS value to None
                        sensor2_mgrs = None
                        # clear Sensor 2 MGRS input field
                        self.sensor2_mgrs.delete(0,END)
            # if Single LOB Boolean value is TRUE
            else:
                # set all local Sensor 2 values to None
                sensor2_mgrs = None
                sensor2_grid_azimuth = None
                sensor2_power_received_dBm = None
                # clear all Sensor 2 input fields
                self.sensor2_mgrs.delete(0,END) 
                self.sensor2_lob.delete(0,END)
                self.sensor2_Rpwr.delete(0,END)   
        # exception handling for ValueError         
        except ValueError:
            # set local Sensor 2 MGRS value to None
            sensor2_mgrs = None
        # if Single LOB Boolean value is FALSE
        if not self.single_lob_bool:
            # try to read Sensor 2 LOB value
            try:
                # get Sensor 2 LOB value from input field
                sensor2_grid_azimuth = int(self.sensor2_lob.get())
                # assess the validity of Sensor 2 LOB input
                if sensor2_grid_azimuth < 0 or sensor2_grid_azimuth > 360:
                    # exception handling for ValueError
                    raise ValueError
            # exception for ValueError
            except ValueError:
                # if ValueError occurs, give user the option to re-input or use default value
                choice = self.input_error(category='Sensor 2 Grid Azimuth',msg=f'Invalid Input',single_lob_option=True)
                # if users chooses to utilize the default Sensor 2 LOB value
                if choice == True:
                    # clear the Sensor 2 LOB input field
                    self.sensor2_lob.delete(0,END)
                    # insert the default Sensor 2 LOB value 
                    self.sensor2_lob.insert(0,App.DEFAULT_VALUES['Sensor 2 LOB'])   
                    # set local Sensor 2 LOB value to default value
                    sensor2_grid_azimuth = App.DEFAULT_VALUES['Sensor 2 LOB']
                # if user chooses to re-input the Sensor 2 LOB value
                elif choice == False:
                    # end function
                    return 0
                # if user chooses to only utilize a Single LOB
                elif choice == 'SL':
                    # set Single LOB Boolean value to TRUE
                    self.single_lob_bool = True
                    # set local Sensor 2 LOB value to None
                    sensor2_grid_azimuth = None
                    # clear Sensor 2 LOB input field
                    self.sensor2_lob.delete(0,END)
        # if Single LOB Boolean value is TRUE
        else:
            # set all local Sensor 2 input values to None
            sensor2_mgrs = None
            sensor2_grid_azimuth = None
            sensor2_power_received_dBm = None
            # clear all Sensor 2 input fields
            self.sensor2_mgrs.delete(0,END) 
            self.sensor2_lob.delete(0,END)
            self.sensor2_Rpwr.delete(0,END)
        # if Single LOB Boolean value is FALSE
        if not self.single_lob_bool:
            # try to read the Sensor 2 PWR Received value
            try:
                # read the Sensor 2 PWR Received value from the input field
                sensor2_power_received_dBm = int(self.sensor2_Rpwr.get())
                # assess if validity of Sensor 2 PWR Received value
                if sensor2_power_received_dBm > 0:
                    # raise a ValueError exception
                    raise ValueError
            # exception handling for ValueError
            except ValueError:
                # if ValueError occurs, give user the option to re-input or use default value
                choice = self.input_error(category='Sensor 2 Power Received',msg=f'Invalid Input',single_lob_option=True)
                # if user chooses to utilize the default Sensor 2 LOB value
                if choice == True:
                    # clear the Sensor 2 Received PWR input field
                    self.sensor2_Rpwr.delete(0,END)
                    # insert the default Sensor 2 PWR Received value
                    self.sensor2_Rpwr.insert(0,App.DEFAULT_VALUES['Sensor 2 PWR Received'])  
                    # set local Sensor 2 PWR Received value to default value
                    sensor2_power_received_dBm = App.DEFAULT_VALUES['Sensor 2 PWR Received']
                # if user chooses to re-input the Sensor 2 PWR Received value
                elif choice == False:
                    # end function
                    return 0
                # if user chooses to only utilize a single LOB
                elif choice == 'SL':
                    # set Single LOB Boolean to TRUE
                    self.single_lob_bool = True
                    # set local Sensor 2 PWR Received value to None
                    sensor2_power_received_dBm = None
                    # clear Sensor 2 PWR Received input field
                    self.sensor2_Rpwr.delete(0,END)
        else:
            # set all local Sensor 2 values to None
            sensor2_mgrs = None
            sensor2_grid_azimuth = None
            sensor2_power_received_dBm = None
            # clear all Sensor 2 input fields
            self.sensor2_mgrs.delete(0,END) 
            self.sensor2_lob.delete(0,END)
            self.sensor2_Rpwr.delete(0,END)   
        # try to read the input frequency
        try:
            # read the frequency from the frequency input field
            frequency_MHz = float(self.frequency.get())
            # assess if input frequency is feasible
            if frequency_MHz < 0:
                # raise a ValueError exception
                raise ValueError
        # exception handling for ValueError
        except ValueError:
            # if ValueError occurs, give user the option to re-input or use default value
            choice = self.input_error(category='Frequency',msg=f'Invalid Input')
            # if user chooses to use the default frequency value
            if choice:
                # clear frequency input field
                self.frequency.delete(0,END)
                # input default frequency value in input field
                self.frequency.insert(0,App.DEFAULT_VALUES['Frequency'])
                # set local frequency value to default frequency value
                frequency_MHz = App.DEFAULT_VALUES['Frequency']
            # if user chooses to re-input the frequency value
            else:
                # end function
                return 0
        # try to read the input Min ERP value
        try:
            # read the Min ERP value from the input field
            min_wattage = float(self.min_ERP.get())
            # assess validity of input Min ERP value
            if min_wattage < 0:
                # raise a ValueError exception
                raise ValueError
        # exception handling for ValueError
        except ValueError:
            # if ValueError occurs, give user the option to re-input or use default value
            choice = self.input_error(category='Minimum ERP',msg=f'Invalid Input')
            # if user chooses to utilize the default Min ERP value
            if choice:
                # clear Min ERP input field
                self.min_ERP.delete(0,END)
                # insert default Min ERP value in input field
                self.min_ERP.insert(0,App.DEFAULT_VALUES['Min ERP'])
                # set local Min ERP value to default Min ERP value
                min_wattage = App.DEFAULT_VALUES['Min ERP']
            # if user chooses to re-input Min ERP value
            else:
                # end function
                return 0
        # try to read Max ERP from input field
        try:
            # read Max ERP from input field
            max_wattage = float(self.max_ERP.get())
            # assess validity of Max ERP value
            if max_wattage < 0 or max_wattage < min_wattage:
                # raise a ValueError exception
                raise ValueError
        # exception handling for ValueError
        except ValueError:
            # if ValueError occurs, give user the option to re-input or use default value
            choice = self.input_error(category='Maximum ERP',msg=f'Invalid Input')
            # if user chooses to use the default Max ERP value
            if choice:
                # clear Max ERP input field
                self.max_ERP.delete(0,END)
                # insert default Max ERP in input field
                self.max_ERP.insert(0,App.DEFAULT_VALUES['Max ERP'])
                # set local Max ERP value to default value
                max_wattage = App.DEFAULT_VALUES['Max ERP']
            # if user chooses to re-input the Max ERP value
            else:
                # end function
                return 0
        # try to read path-loss coefficient value
        try:
            # set local path-loss coefficient value to global path-loss coefficent value
            path_loss_coeff = self.path_loss_coeff
        # exception handling for ValueError
        except ValueError:
            # if ValueError occurs, give user the option to re-input or use default value
            choice = self.input_error(category='Path-Loss Coefficient',msg=f'Invalid Input')
            # if user chooses to use the default path-loss coefficient
            if choice:
                # set local path-loss coefficient value to default value
                path_loss_coeff = App.DEFAULT_VALUES['Path-Loss Coefficient']
                # set path-loss coefficient input field to default description
                self.option_path_loss_coeff.set(App.DEFAULT_VALUES['Path-Loss Coefficient Description'])
                # set global path-loss coefficient value to default value
                self.path_loss_coeff = App.DEFAULT_VALUES['Path-Loss Coefficient']
            # if user chooses to re-input the path-loss coefficient
            else:
                # end function
                return 0
        sensor1_coord = convert_mgrs_to_coords(sensor1_mgrs)
        self.sensor1_distance.configure(text='')
        sensor1_min_distance_km = get_emission_distance(min_wattage,frequency_MHz,transmitter_gain_dBi,self.sensor1_receiver_gain_dBi,sensor1_power_received_dBm,transmitter_height_m,sensor1_receiver_height_m,temp_f,path_loss_coeff,weather_coeff=4/3,pure_pathLoss=True)
        sensor1_min_distance_m = sensor1_min_distance_km * 1000
        sensor1_max_distance_km = get_emission_distance(max_wattage,frequency_MHz,transmitter_gain_dBi,self.sensor1_receiver_gain_dBi,sensor1_power_received_dBm,transmitter_height_m,sensor1_receiver_height_m,temp_f,path_loss_coeff,weather_coeff=4/3,pure_pathLoss=True)
        sensor1_max_distance_m = sensor1_max_distance_km * 1000  
        sensor1_lob_center, sensor1_lob_near_right_coord, sensor1_lob_near_left_coord, sensor1_lob_near_middle_coord, sensor1_lob_far_right_coord, sensor1_lob_far_left_coord, sensor1_lob_far_middle_coord, sensor1_center_coord_list = get_coords_from_LOBs(sensor1_coord,sensor1_grid_azimuth,self.sensor1_error,sensor1_min_distance_m,sensor1_max_distance_m)
        sensor1_lob_polygon = [sensor1_lob_near_right_coord,sensor1_lob_far_right_coord,sensor1_lob_far_left_coord,sensor1_lob_near_left_coord]
        sensor1_lob_polygon = organize_polygon_coords(sensor1_lob_polygon)
        sensor1_lob_error_acres = get_polygon_area(sensor1_lob_polygon)  
        lob1_center = get_line(sensor1_coord, sensor1_lob_far_middle_coord)
        lob1_right_bound = get_line(sensor1_lob_near_right_coord, sensor1_lob_far_right_coord)
        lob1_left_bound = get_line(sensor1_lob_near_left_coord, sensor1_lob_far_left_coord)
        ew_team1_marker = self.map_widget.set_marker(sensor1_coord[0], sensor1_coord[1], text="", image_zoom_visibility=(10, float("inf")),
                                        marker_color_circle='white',text_color='black',icon=self.ew_team1_image) 
        self.ewt_marker_list.append(ew_team1_marker)
        sensor1_lob = self.map_widget.set_polygon([(sensor1_coord[0],sensor1_coord[1]),
                                        (sensor1_lob_far_middle_coord[0],sensor1_lob_far_middle_coord[1])],
                                    # fill_color=None,
                                    outline_color="red",
                                    # border_width=12,
                                    command=self.polygon_click,
                                    name="Sensor 1 LOB")
        self.polygon_list.append(sensor1_lob)
        sensor1_lob_area = self.map_widget.set_polygon(sensor1_lob_polygon,
                                    # fill_color=None,
                                    outline_color="green",
                                    # border_width=12,
                                    command=self.polygon_click,
                                    name=f"EWT 1 ({sensor1_mgrs}) LOB at bearing {int(sensor1_grid_azimuth)}° between {sensor1_min_distance_m/1000:,.2f}km and {sensor1_max_distance_m/1000:,.2f}km with {sensor1_lob_error_acres:,.0f} acres of error")
        self.polygon_list.append(sensor1_lob_area)
        if sensor2_mgrs != None and sensor2_grid_azimuth != None and sensor2_power_received_dBm != None:
            sensor2_coord = convert_mgrs_to_coords(sensor2_mgrs)
            self.map_widget.set_position(np.average([sensor1_coord[0],sensor2_coord[0]]),np.average([sensor1_coord[1],sensor2_coord[1]]))
            self.sensor2_distance.configure(text='')
            sensor2_min_distance_km = get_emission_distance(min_wattage,frequency_MHz,transmitter_gain_dBi,self.sensor2_receiver_gain_dBi,sensor2_power_received_dBm,transmitter_height_m,sensor2_receiver_height_m,temp_f,path_loss_coeff,weather_coeff=4/3,pure_pathLoss=True)
            sensor2_min_distance_m = sensor2_min_distance_km * 1000    
            sensor2_max_distance_km = get_emission_distance(max_wattage,frequency_MHz,transmitter_gain_dBi,self.sensor2_receiver_gain_dBi,sensor2_power_received_dBm,transmitter_height_m,sensor2_receiver_height_m,temp_f,path_loss_coeff,weather_coeff=4/3,pure_pathLoss=True)
            sensor2_max_distance_m = sensor2_max_distance_km * 1000
            sensor2_lob_center, sensor2_lob_near_right_coord, sensor2_lob_near_left_coord, sensor2_lob_near_middle_coord, sensor2_lob_far_right_coord, sensor2_lob_far_left_coord, sensor2_lob_far_middle_coord, sensor2_center_coord_list = get_coords_from_LOBs(sensor2_coord,sensor2_grid_azimuth,self.sensor2_error,sensor2_min_distance_m,sensor2_max_distance_m)
            sensor2_lob_polygon = [sensor2_lob_near_right_coord,sensor2_lob_far_right_coord,sensor2_lob_far_left_coord,sensor2_lob_near_left_coord]
            sensor2_lob_polygon = organize_polygon_coords(sensor2_lob_polygon) 
            sensor2_lob_error_acres = get_polygon_area(sensor2_lob_polygon)  
            lob2_center = get_line(sensor2_coord, sensor2_lob_far_middle_coord)
            lob2_right_bound = get_line(sensor2_lob_near_right_coord, sensor2_lob_far_right_coord)
            lob2_left_bound = get_line(sensor2_lob_near_left_coord, sensor2_lob_far_left_coord)
            ew_team2_marker = self.map_widget.set_marker(sensor2_coord[0], sensor2_coord[1], text="", image_zoom_visibility=(10, float("inf")),
                                            marker_color_circle='white',text_color='black',icon=self.ew_team2_image)
            self.ewt_marker_list.append(ew_team2_marker)
            sensor2_lob = self.map_widget.set_polygon([(sensor2_coord[0],sensor2_coord[1]),
                                            (sensor2_lob_far_middle_coord[0],sensor2_lob_far_middle_coord[1])],
                                        # fill_color=None,
                                        outline_color="red",
                                        # border_width=12,
                                        command=self.polygon_click,
                                        name="Sensor 2 LOB")
            self.polygon_list.append(sensor2_lob)
            sensor2_lob_area = self.map_widget.set_polygon(sensor2_lob_polygon,
                                        # fill_color=None,
                                        outline_color="green",
                                        # border_width=12,
                                        command=self.polygon_click,
                                        name=f"EWT 2 ({sensor2_mgrs}) LOB at bearing {int(sensor2_grid_azimuth)}° between {sensor2_min_distance_m/1000:,.2f}km and {sensor2_max_distance_m/1000:,.2f}km with {sensor2_lob_error_acres:,.0f} acres of error")
            self.polygon_list.append(sensor2_lob_area)
            if check_for_intersection(sensor1_coord,sensor1_lob_far_middle_coord,sensor2_coord,sensor2_lob_far_middle_coord):
                self.map_widget.set_zoom(15)
                self.target_class = '(CUT)'
                self.label_target_grid.configure(text=f'TARGET GRID {self.target_class}'.strip(),text_color='red')
                intersection_l1_l2 = get_intersection(lob1_center, lob2_center)
                center_coordinate = get_center_coord([intersection_l1_l2])
                intersection_l1r_l2r = get_intersection(lob1_right_bound, lob2_right_bound)
                intersection_l1r_l2l = get_intersection(lob1_right_bound, lob2_left_bound)
                intersection_l1l_l2r = get_intersection(lob1_left_bound, lob2_right_bound)
                intersection_l1l_l2l = get_intersection(lob1_left_bound, lob2_left_bound)
                '''
                Need an improved method to get cut coordinates
                '''
                cut_polygon = [intersection_l1r_l2r,intersection_l1r_l2l,intersection_l1l_l2l,intersection_l1l_l2r]
                cut_polygon = organize_polygon_coords(cut_polygon)
                cut_area_acres = get_polygon_area(cut_polygon)
                cut_center_mgrs = convert_coords_to_mgrs(center_coordinate)
                cut_area = self.map_widget.set_polygon(cut_polygon,
                                            # fill_color=None,
                                            outline_color="blue",
                                            # border_width=12,
                                            command=self.polygon_click,
                                            name=f"Target CUT with {cut_area_acres:,.0f} acres of error")
                dist_sensor1 = int(get_distance_between_coords(sensor1_coord,center_coordinate))
                dist_sensor2 = int(get_distance_between_coords(sensor2_coord,center_coordinate))               
                dist_sensor1_unit = 'm'; dist_sensor2_unit = 'm'
                cut_target_marker = self.map_widget.set_marker(center_coordinate[0], center_coordinate[1], text=f"{convert_coords_to_mgrs(center_coordinate)}", image_zoom_visibility=(10, float("inf")),
                                                marker_color_circle='white',icon=self.target_image)
                self.target_marker_list.append(cut_target_marker)                
                if dist_sensor1 >= 1000:
                    dist_sensor1 /= 1000
                    dist_sensor1_unit = 'km'
                    self.sensor1_distance.configure(text=f'{dist_sensor1:,.2f}{dist_sensor1_unit}',text_color='white')
                else:
                    self.sensor1_distance.configure(text=f'{dist_sensor1}{dist_sensor1_unit}',text_color='white')
                if dist_sensor2 >= 1000:
                    dist_sensor2 /= 1000
                    dist_sensor2_unit = 'km'
                    self.sensor2_distance.configure(text=f'{dist_sensor2:,.2f}{dist_sensor2_unit}',text_color='white')
                else:
                    self.sensor2_distance.configure(text=f'{dist_sensor2}{dist_sensor2_unit}',text_color='white')
                self.target_grid.configure(text=f'{cut_center_mgrs}',text_color='yellow')
                self.target_error.configure(text=f'{cut_area_acres:,.0f} acres',text_color='white')
            else: # output for no intersection
                self.map_widget.set_zoom(15)
                intersection_l1r_l2r = False
                intersection_l1r_l2l = False
                intersection_l1l_l2r = False
                intersection_l1l_l2l = False     
                self.show_info("No LOB intersection detected!")
                sensor1_target_coord = [np.average([sensor1_lob_near_middle_coord[0],sensor1_lob_far_middle_coord[0]]),np.average([sensor1_lob_near_middle_coord[1],sensor1_lob_far_middle_coord[1]])]
                target1_marker = self.map_widget.set_marker(sensor1_target_coord[0], sensor1_target_coord[1], text=f"{convert_coords_to_mgrs(sensor1_target_coord)}", image_zoom_visibility=(10, float("inf")),
                                                marker_color_circle='white',icon=self.target_image)
                self.target_marker_list.append(target1_marker)
                sensor2_target_coord = [np.average([sensor2_lob_near_middle_coord[0],sensor2_lob_far_middle_coord[0]]),np.average([sensor2_lob_near_middle_coord[1],sensor2_lob_far_middle_coord[1]])]
                target2_marker = self.map_widget.set_marker(sensor2_target_coord[0], sensor2_target_coord[1], text=f"{convert_coords_to_mgrs(sensor2_target_coord)}", image_zoom_visibility=(10, float("inf")),
                                                marker_color_circle='white',icon=self.target_image)
                self.target_marker_list.append(target2_marker)
                # cut_center_coord = convert_mgrs_to_coords(cut_center_mgrs)
                dist_sensor1 = int(get_distance_between_coords(sensor1_coord,sensor1_target_coord))
                dist_sensor2 = int(get_distance_between_coords(sensor2_coord,sensor2_target_coord))
                if dist_sensor1 >= 1000:
                    dist_sensor1 /= 1000
                    dist_sensor1_unit = 'km'
                    self.sensor1_distance.configure(text=f'{dist_sensor1:,.2f}{dist_sensor1_unit}',text_color='white')
                else:
                    self.sensor1_distance.configure(text=f'{dist_sensor1}{dist_sensor1_unit}',text_color='white')
                if dist_sensor2 >= 1000:
                    dist_sensor2 /= 1000
                    dist_sensor2_unit = 'km'
                    self.sensor2_distance.configure(text=f'{dist_sensor2:,.2f}{dist_sensor2_unit}',text_color='white')
                else:
                    self.sensor2_distance.configure(text=f'{dist_sensor2}{dist_sensor2_unit}',text_color='white')
                self.target_grid.configure(text='MULTIPLE TGTs',text_color='yellow')
                self.target_error.configure(text=f'{sensor1_lob_error_acres:,.0f} & {sensor2_lob_error_acres:,.0f} acres',text_color='white')
        else:
            self.map_widget.set_zoom(16)
            intersection_l1r_l2r = False
            intersection_l1r_l2l = False
            intersection_l1l_l2r = False
            intersection_l1l_l2l = False
            self.map_widget.set_position(sensor1_coord[0],sensor1_coord[1])
            self.target_class = '(LOB)'
            self.label_target_grid.configure(text=f'TARGET GRID {self.target_class}'.strip(),text_color='red')
            target_coord = [np.average([sensor1_lob_near_middle_coord[0],sensor1_lob_far_middle_coord[0]]),np.average([sensor1_lob_near_middle_coord[1],sensor1_lob_far_middle_coord[1]])]
            target_mgrs = convert_coords_to_mgrs(target_coord)
            single_lob_target_marker = self.map_widget.set_marker(target_coord[0], target_coord[1], text=f"{convert_coords_to_mgrs(target_coord)}", image_zoom_visibility=(10, float("inf")),
                                            marker_color_circle='white',icon=self.target_image)
            self.target_marker_list.append(single_lob_target_marker)   
            self.target_grid.configure(text=f'{target_mgrs}',text_color='yellow')
            dist_sensor1 = int(get_distance_between_coords(sensor1_coord,target_coord))
            dist_sensor1_unit = 'm'
            if dist_sensor1 >= 1000:
                dist_sensor1 /= 1000
                dist_sensor1_unit = 'km'
                self.sensor1_distance.configure(text=f'{dist_sensor1:,.2f}{dist_sensor1_unit}',text_color='white')
            else:
                self.sensor1_distance.configure(text=f'{dist_sensor1}{dist_sensor1_unit}',text_color='white')
            self.sensor2_distance.configure(text='N/A',text_color='white') 
            self.target_error.configure(text=f'{sensor1_lob_error_acres:,.0f} acres',text_color='white')

    def check_mgrs_input(self,mgrs_input):
        """
        Determine if the MGRS input is valid 

        Parameters:
        ----------
        self: App Object
            GUI application object
        mgrs_input : str
            Candidate MGRS input

        Returns:
        ----------
        Boolean
            Determination if MGRS is valid (TRUE) or not (FALSE)

        """
        return mgrs_input[2:5].isalpha() and mgrs_input[:2].isdigit() and mgrs_input[5:].isdigit() and len(mgrs_input[5:]) % 2 == 0
    
    def add_marker_event(self, coords):
        print("Add marker:", coords)
        new_marker = self.map_widget.set_marker(coords[0], coords[1], 
                                                text=f"{convert_coords_to_mgrs(list(coords))}",
                                                image_zoom_visibility=(10, float("inf")))
        self.marker_list.append(new_marker)
        if len(self.marker_list) > 1:
            sequencial_marker_list = self.marker_list[::-1]
            sequencial_coord_list = []
            for i,marker in enumerate(sequencial_marker_list):
                sequencial_coord_list.append(list(marker.position))
            distance_unit = 'm'
            distance = get_distance_between_coords(sequencial_coord_list[0],sequencial_coord_list[1])
            if distance >= 1000:
                distance /= 1000
                distance_unit = 'km'
            dist_line = self.map_widget.set_polygon([(sequencial_coord_list[0][0],sequencial_coord_list[0][1]),
                            (sequencial_coord_list[1][0],sequencial_coord_list[1][1])],outline_color="black")
            coord_x = np.average([sequencial_coord_list[0][0],sequencial_coord_list[1][0]])
            coord_y = np.average([sequencial_coord_list[0][1],sequencial_coord_list[1][1]])
            marker_dist = self.map_widget.set_marker(coord_x,coord_y,text=f'{distance:,.2f}{distance_unit}',
                                                     text_color='black',
                                                     image_zoom_visibility=(10, float('inf')),
                                                     icon=self.blank_image)
            self.path_list.append(dist_line)
            self.path_list.append(marker_dist)
                

    def search_event(self, event=None):
        try:
            mgrs = self.mgrs_entry.get()
        except ValueError:
            self.show_info("Invalid MGRS input!")
        if mgrs[2:5].isalpha() and mgrs[:2].isdigit() and mgrs[5:].isdigit() and len(mgrs[5:]) % 2 == 0:
            entry_coord = convert_mgrs_to_coords(self.mgrs_entry.get())
            self.map_widget.set_position(entry_coord[0],entry_coord[1])
            self.add_marker_event(entry_coord)
        else:
            if mgrs.replace(' ','').isalpha() and len(mgrs) > 2:
                self.map_widget.set_address(mgrs)
            else:
                self.show_info("Invalid MGRS input!")

    def clear_markers(self):
        for marker in self.marker_list:
            marker.delete()
        for path in self.path_list:
            path.delete()
        self.marker_list = []
        self.path_list = []

    def clear_ewt_markers(self):
        for ewt_marker in self.ewt_marker_list:
            ewt_marker.delete()

    def clear_polygons(self):
        for polygon in self.polygon_list:
            polygon.delete()

    def clear_target_markers(self):
        for target in self.target_marker_list:
            target.delete()

    def clear_entries(self):
        self.sensor1_mgrs.delete(0,END)
        self.sensor1_lob.delete(0,END)
        self.sensor1_Rpwr.delete(0,END)
        self.sensor2_mgrs.delete(0,END)
        self.sensor2_lob.delete(0,END)
        self.sensor2_Rpwr.delete(0,END)
        self.sensor3_mgrs.delete(0,END)
        self.sensor3_lob.delete(0,END)
        self.sensor3_Rpwr.delete(0,END)
        self.frequency.delete(0,END)
        self.min_ERP.delete(0,END)
        self.max_ERP.delete(0,END)

    def log_target_data(self):
        pass

    def elevation_survey(self):
        # self.elevation_data_thread1 = threading.Thread(target=self.elevation_plotter,args=(get_coords_from_LOBs(sensor1_coord,sensor1_grid_azimuth,self.sensor1_error,sensor1_min_distance_m,sensor1_max_distance_m*1.25)[-1],[center_coordinate],['EWT 1']))
        # self.elevation_data_thread1.daemon = True
        # self.elevation_data_thread1.start()
        # self.elevation_data_thread2 = threading.Thread(target=self.elevation_plotter,args=(get_coords_from_LOBs(sensor2_coord,sensor2_grid_azimuth,self.sensor2_error,sensor2_min_distance_m,sensor2_max_distance_m*1.25)[-1],[center_coordinate],['EWT 2']))
        # self.elevation_data_thread2.daemon = True
        # self.elevation_data_thread2.start() 
        # self.elevation_data_thread1 = threading.Thread(target=self.elevation_plotter,args=(get_coords_from_LOBs(sensor1_coord,sensor1_grid_azimuth,self.sensor1_error,sensor1_min_distance_m,sensor1_max_distance_m*1.25)[-1],[sensor1_lob_near_middle_coord,target_coord,sensor1_lob_far_middle_coord],['EWT 1']))
        # self.elevation_data_thread1.daemon = True
        # self.elevation_data_thread1.start()
        pass

    def polygon_click(self,polygon):
        self.show_info(msg=polygon.name,box_title='Target Data',icon='info')

    def show_info(self,msg,box_title='Warning Message',icon='warning'):
        CTkMessagebox(title=box_title, message=msg, icon=icon,option_1='Ackowledged')

    def input_error(self,category,msg,single_lob_option=False):
        if not single_lob_option:
            msgBox = CTkMessagebox(title=f"Error in {category}", message=msg, icon='warning',option_1='Re-input',option_2='Use Default')
        else:
            msgBox = CTkMessagebox(title=f"Error in {category}", message=msg, icon='warning',option_1='Re-input',option_2='Use Default', option_3='Single LOB')
        response = msgBox.get()
        if response == 'Re-input':
            return False
        elif response == 'Use Default':
            return True
        elif response == 'Single LOB':
            return 'SL'

    def change_map(self, new_map: str):
        if new_map == 'Local Map Server':
            self.map_widget.set_tile_server("http://127.0.0.1:8080/{z}/{x}/{y}.png", max_zoom=22)
        elif new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google Street":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Google Satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def change_path_loss(self, path_loss_description: str):
        if path_loss_description == 'Free Space (Theoretical)':
            self.path_loss_coeff = 2
        elif path_loss_description == 'Light Foliage':
            self.path_loss_coeff = 3
        elif path_loss_description == 'Light-Moderate Foliage':
            self.path_loss_coeff = 3.5
        elif path_loss_description == 'Moderate Foliage':
            self.path_loss_coeff = 4
        elif path_loss_description == 'Moderate-Dense Foliage':
            self.path_loss_coeff = 4.5
        elif path_loss_description == 'Dense Foliage':
            self.path_loss_coeff = 5
    
    def change_sensor(self,sensor_option):
        if sensor_option == 'VROD/VMAX':
            self.sensor1_receiver_gain_dBi = 0
            self.sensor2_receiver_gain_dBi = 0
            self.sensor1_error = 6
            self.sensor2_error = 6
        elif sensor_option == 'BEAST+':
            self.sensor1_receiver_gain_dBi = 0
            self.sensor2_receiver_gain_dBi = 0
            self.sensor1_error = 4
            self.sensor2_error = 4            
        pass

    def map_server(self,tile_directory):
        server_path = r"C:\Users\shuttdown\Documents\Coding Projects\CEMA\maptiles\ESRI"
        port = 8080
        from subprocess import call, PIPE, DEVNULL
        call(["python3", "-m", "http.server", f"{port}", "--directory", f'"{tile_directory}"'])

    def elevation_plotter(self,coords,targets=None,title_args=None):
        elev_data = get_elevation_data(coords)
        plot_elevation_data(elev_data,targets,title_args)

    def on_closing(self, event=0):
        self.destroy()
        sys.exit()

    def start(self):
        self.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()


"""
DEV NOTES
- Logging feature (csv)
- earth curvature limitation identified on elevation map
- button that return you to last marker
- add additional EWT to get potential for fix
- add 100m to each end of elevation plot to provide better prespective\
- 3D elevation plot
- DTED elevation data source
- button to request elevation survey, not automatic
"""
