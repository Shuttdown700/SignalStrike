#!/usr/bin/env python3
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from utilities import import_libraries
libraries = [['customtkinter'],['CTkMessagebox',['CTkMessagebox']],
             ['numpy'],['os'],['PIL',['Image','ImageTK']],
             ['sys'],['threading'],['tkinter',['END']],['tkintermapview',['TkinterMapView']],
             ['alive_progress'],['pandas'],['urllib.request']]
import_libraries(libraries)

import customtkinter
customtkinter.set_default_color_theme(os.path.dirname(os.path.abspath(__file__))+"/config_files/color_theme.json")
class App(customtkinter.CTk):
    """
    Custom Tkinter Application Class for GUI support
    """
    # preset application name
    APP_NAME = "Electromagnetic Warfare Targeting Application"
    # preset aspect ratio of application display
    ASPECT_RATIO = 16/9
    # preset width of GUI dislay
    WIDTH = 1200
    # preset height of GUI display (dependent on WIDTH and ASPECT_RATIO)
    HEIGHT = int(WIDTH/ASPECT_RATIO)
    # preset local port that is hosting the map server
    MAP_SERVER_PORT = 1234
    # present IP address for the map server
    MAP_SERVER_IP = 'localhost'
    # preset maximum map zoom level
    MAX_ZOOM = 19
    # preset default values
    DEFAULT_VALUES = {
        "Sensor 1 MGRS": "11SNV4178910362",
        "Sensor 1 PWR Received": -75,
        "Sensor 1 LOB": 105,
        "Sensor 2 MGRS": "11SNV4314711067",
        "Sensor 2 PWR Received": -78,
        "Sensor 2 LOB": 165,
        "Sensor 3 MGRS": "11SNV4632811020",
        "Sensor 3 PWR Received": -79,
        "Sensor 3 LOB": 247,
        "Frequency":32,
        "Min ERP":0.005,
        "Max ERP":50,
        "Path-Loss Coefficient":4,
        "Path-Loss Coefficient Description":"Moderate Foliage",
        "Border Width":4,
        "LOB Fill Color":"gray95",
        "LOB Center Line Color":"Red",
        "LOB Area Outline Color":"Green",
        "CUT Area Outline Color":"Blue",
        "FIX Area Outline Color":"Yellow"
    }

    def __init__(self, *args, **kwargs):
        """
        Defines application initialization attributes
        """
        super().__init__(*args, **kwargs)
        from tkintermapview import TkinterMapView
        from PIL import Image, ImageTk
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
        self.tile_directory = "\\".join(self.src_directory.split('\\')[:-1])+"\\map_tiles\\ESRI"
        # define icon file directory
        self.log_directory = "\\".join(self.src_directory.split('\\')[:-1])+"\\logs"
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
        # set app icon
        self.iconbitmap(os.path.join(self.icon_directory, "app_icon.ico"))
        # define initial marker list
        self.user_marker_list = []
        # define initial LOB list
        self.lob_list = []
        # define initial CUT list
        self.cut_list = []
        # define initial FIX list
        self.fix_list = []
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
        # define default target value (used as conditional in logging method)
        self.target_mgrs = None

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

        # ============ User Input/Ouput Frame ============
        
        # define frame header attributes
        self.label_header = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="EW TARGETING DATA", 
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
            text="EW Sensor:", 
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
            values=["BEAST+","VROD/VMAX"],
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
            text="EWT 1 Location:", 
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
        # bind EWT function to RETURN keystroke in Sensor 1 MGRS input field
        self.sensor1_mgrs.bind("<Return>", self.ewt_function)
        # define sensor 1 LOB label
        self.label_sensor1_lob = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="EWT 1 LOB:", 
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
        # bind EWT function to RETURN keystroke in Sensor 1 LOB input field
        self.sensor1_lob.bind("<Return>", self.ewt_function)
        # define sensor 1 received power label attributes
        self.label_sensor1_Rpwr = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="EWT 1 Power Received:", 
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
        # bind EWT function to RETURN keystroke in Sensor 1 Rpwr input field
        self.sensor1_Rpwr.bind("<Return>", self.ewt_function)
        # define sensor 2 mgrs label attributes
        self.label_sensor2_mgrs = customtkinter.CTkLabel(
            master = self.frame_left, 
            text="EWT 2 Location:", 
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
        # bind EWT function to RETURN keystroke in Sensor 2 MGRS input field
        self.sensor2_mgrs.bind("<Return>", self.ewt_function)
        # define sensor 2 LOB label attributes
        self.label_sensor2_lob = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="EWT 2 LOB:", 
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
        # bind EWT function to RETURN keystroke in Sensor 2 LOB input field
        self.sensor2_lob.bind("<Return>", self.ewt_function)
        # define sensor 2 received power attributes
        self.label_sensor2_Rpwr = customtkinter.CTkLabel(
            self.frame_left, 
            text="EWT 2 Power Received:", 
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
        # bind EWT function to RETURN keystroke in Sensor 2 Rpwr input field
        self.sensor2_Rpwr.bind("<Return>", self.ewt_function)
        # define sensor 3 mgrs label attributes
        self.label_sensor3_mgrs = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="EWT 3 Location:", 
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
        # bind EWT function to RETURN keystroke in Sensor 3 MGRS input field
        self.sensor3_mgrs.bind("<Return>", self.ewt_function)
        # define sensor 3 LOB label attributes
        self.label_sensor3_lob = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="EWT 3 LOB:", 
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
        # bind EWT function to RETURN keystroke in Sensor 3 LOB input field
        self.sensor3_lob.bind("<Return>", self.ewt_function)
        # define sensor 3 received power label attributes
        self.label_sensor3_Rpwr = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="EWT 3 Power Received:", 
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
        # bind EWT function to RETURN keystroke in Sensor 3 Rpwr input field
        self.sensor3_Rpwr.bind("<Return>", self.ewt_function)
        # define target frequency label attributes
        self.label_frequency = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="Frequency:",
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
        # bind EWT function to RETURN keystroke in Frequency input field
        self.frequency.bind("<Return>", self.ewt_function)
        # define min ERP label attributes
        self.label_min_ERP = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="Minimum ERP:", 
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
        # bind EWT function to RETURN keystroke in Min ERP input field
        self.min_ERP.bind("<Return>", self.ewt_function)
        # define max ERP label attributes
        self.label_max_ERP = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="Maximum ERP:", 
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
        # bind EWT function to RETURN keystroke in Max ERP input field
        self.max_ERP.bind("<Return>", self.ewt_function)
        # define path-loss coefficient label attributes
        self.label_path_loss_coeff = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="Path-Loss Coefficient:", 
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
            text="NO TARGET",
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
            text="Distance from EWT 1:",
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
            text="Distance from EWT 2:",
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
            text="Distance from EWT 3:",
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
            text="Calculation Error:",
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
            text="N/A",
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
        # define TBD button attributes
        self.button_TBD = customtkinter.CTkButton(
            master=self.frame_left, 
            text="TBD Feature",
            fg_color='brown')
        # assign TBD button grid position
        self.button_TBD.grid(
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
        # configure third row with low weight
        self.frame_right.grid_rowconfigure(2, weight=0)        
        # configure first column with low weight
        self.frame_right.grid_columnconfigure(0, weight=1)
        # configure second column with high weight
        self.frame_right.grid_columnconfigure(1, weight=0)
        # configure third column with low weight
        self.frame_right.grid_columnconfigure(2, weight=0)
        # configure forth column with low weight
        self.frame_right.grid_columnconfigure(3, weight=0)
        # configure forth column with low weight
        self.frame_right.grid_columnconfigure(4, weight=0)
        # configure forth column with low weight
        self.frame_right.grid_columnconfigure(5, weight=0)
        # define map widget attributes
        self.map_widget = TkinterMapView(
            master=self.frame_right, 
            corner_radius=0)
        # assign map widget grid position
        self.map_widget.grid(
            row=1, 
            rowspan=1, 
            column=0, 
            columnspan=6,
            padx=(0, 0), 
            pady=(0, 0),
            sticky="nswe")
        # set map widget default tile server
        map_server_url = f'http://{App.MAP_SERVER_IP}:{App.MAP_SERVER_PORT}'
        self.map_widget.set_tile_server(
            tile_server=map_server_url+"/{z}/{x}/{y}.png",
            max_zoom=App.MAX_ZOOM)
        # set initial zoom level for map tile server
        self.map_widget.set_zoom(14)
        # define mgrs entry form attributes
        self.search_mgrs = customtkinter.CTkEntry(
            master=self.frame_right,
            placeholder_text="Insert MGRS Grid")
        # assign mgrs entry form grid position
        self.search_mgrs.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=(12, 0), 
            pady=12,
            sticky="ew")
        # bind mgrs entry RETURN keystroke to search function
        self.search_mgrs.bind("<Return>", self.search_event)
        # define search button attributes
        self.button_search = customtkinter.CTkButton(
            master=self.frame_right,
            text="Search Location",
            width=90,
            command=self.search_event)
        # assign search button grid position
        self.button_search.grid(
            row=0,
            rowspan=1,
            column=2, 
            columnspan=1, 
            padx=(12, 0), 
            pady=12,
            sticky="ew")
        # define clear LOBs button attributes
        self.button_clear_LOBs = customtkinter.CTkButton(
            master=self.frame_right,
            text="Clear TGT Data",
            command=self.clear_target_overlays)
        # assign clear LOBs button grid position
        self.button_clear_LOBs.grid(
            row=0, 
            rowspan=1,
            column=3, 
            columnspan=1, 
            padx=(12, 0), 
            pady=12,
            sticky="ew")
        # define clear markers button attributes
        self.button_clear_markers = customtkinter.CTkButton(
            master=self.frame_right,
            text="Clear Markers",
            command=self.clear_user_markers)
        # assign clear markers button grid position
        self.button_clear_markers.grid(
            row=0, 
            rowspan=1,
            column=4, 
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
            column=5, 
            columnspan=1, 
            padx=(12, 0), 
            pady=12,
            sticky="e")
        # define batch download center MGRS
        self.batch_download_center_mgrs = customtkinter.CTkEntry(
            master=self.frame_right,
            placeholder_text="Insert Center MGRS Grid")
        # assign batch download's center MGRS
        self.batch_download_center_mgrs.grid(
            row=2, 
            column=0,
            columnspan=2,
            padx=(12, 0), 
            pady=12,
            sticky="we")
        # define batch download radius (in m)
        self.batch_download_radius = customtkinter.CTkEntry(
            master=self.frame_right,
            placeholder_text="Radius (in meters)")
        # assign batch download radius 
        self.batch_download_radius.grid(
            row=2, 
            column=2, 
            padx=(12, 0), 
            pady=12,
            sticky="we")
        # define batch download zoom range 
        self.batch_download_zoom_range = customtkinter.CTkEntry(
            master=self.frame_right,
            placeholder_text="Zoom (Ex: 9-12)")
        # assign batch download radius 
        self.batch_download_zoom_range.grid(
            row=2, 
            column=3, 
            padx=(12, 0), 
            pady=12,
            sticky="we")
        # define target error attributes
        self.label_batch_download_time_estimate = customtkinter.CTkLabel(
            master=self.frame_right, 
            text="Est. Download Time: N/A",
            text_color='white')
        # assign target error attributes grid position
        self.label_batch_download_time_estimate.grid(
            row=2,
            rowspan=1,
            column=4, 
            columnspan=1,
            padx=(12,0), 
            pady=(0,0))
        # define batch download button attributes
        self.button_batch_download = customtkinter.CTkButton(
            master=self.frame_right,
            text="Download Map Data",
            command=self.batch_download)
        # assign batch download button grid position
        self.button_batch_download.grid(
            row=2, 
            rowspan=1,
            column=5, 
            columnspan=1, 
            padx=(12, 0), 
            pady=12,
            sticky="we")

        # set initial location
        self.map_widget.set_position(31.8691,-81.6090)
        # set map widget default server
        self.map_option_menu.set("Local Map Server")
        # set default path-loss coefficient
        self.option_path_loss_coeff.set('Moderate Foliage')
        # set default sensor
        self.option_sensor.set('BEAST+')
        # define right-click attributes
        self.map_widget.add_right_click_menu_command(
            label="Add Marker",
            command=self.add_marker_event,
            pass_coords=True)

    def read_ewt_input_fields(self):
        """
        Function to read and ajudicate EWT input
        """
        from tkinter import END
        from utilities import check_mgrs_input
        # resets single lob and cut boolean value to FALSE, allowing multiple EWT input
        self.single_lob_bool = False; self.cut_bool = False
        # reset sensor mgrs/coord reading to None, conditional in log method
        self.sensor1_mgrs_val = None; self.sensor2_mgrs_val = None; self.sensor3_mgrs_val = None
        self.sensor1_coord = None; self.sensor2_coord = None; self.sensor3_coord = None
        self.sensor1_max_distance_m = None; self.sensor2_max_distance_m = None ; self.sensor3_max_distance_m = None
        # set values without option for user input 
        self.sensor1_receiver_height_m_val = 2
        self.sensor2_receiver_height_m_val = 2
        self.sensor3_receiver_height_m_val = 2
        self.transmitter_gain_dBi_val = 0
        self.transmitter_height_m_val = 2
        self.temp_f_val = 70
        # try to read sensor 1 mgrs value
        try:
            # get input from sensor1_mgrs input field
            self.sensor1_mgrs_val = str(self.sensor1_mgrs.get()).strip().replace(" ","")
            # assess whether the input MGRS value is valid
            if check_mgrs_input(self.sensor1_mgrs_val):
                # if MGRS value is valid, pass on to next portion of function code
                pass
            else:
                # if MGRS is invalid, give user the option to re-input or use default value
                choice = self.input_error(category='Sensor 1 Grid',msg=f'Invalid Input {self.sensor1_mgrs_val}')
                # assess if user wishes to use the default value or end function
                if choice:
                    # clear the previous sensor 1 MGRS input
                    self.sensor1_mgrs.delete(0,END)
                    # insert the default sensor 1 MGRS value
                    self.sensor1_mgrs.insert(0,App.DEFAULT_VALUES['Sensor 1 MGRS'])
                    # set local Sensor 1 MGRS value to default value
                    self.sensor1_mgrs_val = App.DEFAULT_VALUES['Sensor 1 MGRS']
                # if user chooses to re-input the sensor 1 MGRS value
                else:
                    # end function
                    return
        # exception handling for ValueError
        except ValueError:
            # if value error occurs, set Sensor 1 MGRS value to None
            self.sensor1_mgrs_val = None
        # try to read sensor 1 LOB value
        try:
            # get input from Sensor 1 LOB field
            self.sensor1_grid_azimuth_val = int(self.sensor1_lob.get())
            # assess feasiblity of Sensor 1 LOB input value
            if self.sensor1_grid_azimuth_val < 0 or self.sensor1_grid_azimuth_val > 360:
                raise ValueError
        # exception handling for ValueError
        except ValueError:
            # give user option to re-input value or use the default Sensor 1 LOB value
            choice = self.input_error(category='Sensor 1 Grid Azimuth',msg='Invalid Input')
            # if user chooses to use the default Sensor 1 LOB value
            if choice:
                # clear Sensor 1 LOB input field
                self.sensor1_lob.delete(0,END)
                # insert default Sensor 1 LOB value
                self.sensor1_lob.insert(0,App.DEFAULT_VALUES['Sensor 1 LOB'])
                # set local Sensor 1 LOB value to default value
                self.sensor1_grid_azimuth_val = App.DEFAULT_VALUES['Sensor 1 LOB']
            # if user choose to re-input the Sensor 1 LOB value
            else:
                # end function
                return
        # try to read the Sensor 1 PWR Received value
        try:
            # get input from Sensor 1 PWR Received input field
            self.sensor1_power_received_dBm_val = int(self.sensor1_Rpwr.get())
            # assess validity of Sensor 1 power received input value
            if self.sensor1_power_received_dBm_val > 0:
                # exception handling for ValueError
                raise ValueError
        # exception for ValueError
        except ValueError:
            # give user option to re-input value or use the default Sensor 1 PWR received value
            choice = self.input_error(category='Sensor 1 Power Received',msg='Invalid Input')
            # if user chooses to use the default Sensor 1 PWR Received value
            if choice:
                # clear the Sensor 1 PWR Received value
                self.sensor1_Rpwr.delete(0,END)
                # insert the default Sensor 1 PWR Received value
                self.sensor1_Rpwr.insert(0,App.DEFAULT_VALUES['Sensor 1 PWR Received'])
                # set local Sensor 1 PWR Received value to default value 
                self.sensor1_power_received_dBm_val = App.DEFAULT_VALUES['Sensor 1 PWR Received']
            # if user chooses to re-input the Sensor 1 PWR Received value
            else:
                # end function
                return
        # try to read the Sensor 2 MGRS value
        try:
            # if Single LOB boolean value is FALSE
            if not self.single_lob_bool:
                # get input from Sensor 2 MGRS field
                self.sensor2_mgrs_val = str(self.sensor2_mgrs.get()).strip().replace(" ","")
                # assess if Sensor 2 MGRS input is valid
                if check_mgrs_input(self.sensor2_mgrs_val):
                    # if MGRS value is valid, pass on to next portion of function code
                    pass
                else:
                    # if MGRS is invalid, give user the option to re-input or use default value
                    choice = self.input_error(category='Sensor 2 Grid',msg=f'Invalid Input {self.sensor2_mgrs_val}',single_lob_option=True)
                    # if user chooses to use default Sensor 2 MGRS value
                    if choice == True:
                        # clear Sensor 2 MGRS input field
                        self.sensor2_mgrs.delete(0,END)
                        # insert default Sensor 2 MGRS value into field
                        self.sensor2_mgrs.insert(0,App.DEFAULT_VALUES['Sensor 2 MGRS'])
                        # set local Sensor 2 MGRS value to default value
                        self.sensor2_mgrs_val = App.DEFAULT_VALUES['Sensor 2 MGRS']
                    # if user chooses to re-input the Sensor 2 MGRS value
                    elif choice == False:
                        # end function
                        return
                    # if user chooses to utilize only a single LOB
                    elif choice == 'SL':
                        # set Single LOB boolean value to TRUE
                        self.single_lob_bool = True
                        # set Sensor 2 MGRS value to None
                        self.sensor2_mgrs_val = None
                        # clear Sensor 2 MGRS input field
                        self.sensor2_mgrs.delete(0,END)
            # if Single LOB Boolean value is TRUE
            else:
                # set all local Sensor 2 values to None
                self.sensor2_mgrs_val = None
                self.sensor2_grid_azimuth_val = None
                self.sensor2_power_received_dBm_val = None
                # clear all Sensor 2 input fields
                self.sensor2_mgrs.delete(0,END) 
                self.sensor2_lob.delete(0,END)
                self.sensor2_Rpwr.delete(0,END)   
        # exception handling for ValueError         
        except ValueError:
            # set local Sensor 2 MGRS value to None
            self.sensor2_mgrs_val = None
            self.sensor2_grid_azimuth_val = None
            self.sensor2_power_received_dBm_val = None
        # if Single LOB Boolean value is FALSE
        if not self.single_lob_bool:
            # try to read Sensor 2 LOB value
            try:
                # get Sensor 2 LOB value from input field
                self.sensor2_grid_azimuth_val = int(self.sensor2_lob.get())
                # assess the validity of Sensor 2 LOB input
                if self.sensor2_grid_azimuth_val < 0 or self.sensor2_grid_azimuth_val > 360:
                    # exception handling for ValueError
                    raise ValueError
            # exception for ValueError
            except ValueError:
                # if ValueError occurs, give user the option to re-input or use default value
                choice = self.input_error(category='Sensor 2 Grid Azimuth',msg='Invalid Input',single_lob_option=True)
                # if users chooses to utilize the default Sensor 2 LOB value
                if choice == True:
                    # clear the Sensor 2 LOB input field
                    self.sensor2_lob.delete(0,END)
                    # insert the default Sensor 2 LOB value 
                    self.sensor2_lob.insert(0,App.DEFAULT_VALUES['Sensor 2 LOB'])   
                    # set local Sensor 2 LOB value to default value
                    self.sensor2_grid_azimuth_val = App.DEFAULT_VALUES['Sensor 2 LOB']
                # if user chooses to re-input the Sensor 2 LOB value
                elif choice == False:
                    # end function
                    return
                # if user chooses to only utilize a Single LOB
                elif choice == 'SL':
                    # set Single LOB Boolean value to TRUE
                    self.single_lob_bool = True
                    # set local Sensor 2 LOB value to None
                    self.sensor2_grid_azimuth_val = None
                    # clear Sensor 2 LOB input field
                    self.sensor2_lob.delete(0,END)
        # if Single LOB Boolean value is TRUE
        else:
            # set all local Sensor 2 input values to None
            self.sensor2_mgrs_val = None
            self.sensor2_grid_azimuth_val = None
            self.sensor2_power_received_dBm_val = None
            # clear all Sensor 2 input fields
            self.sensor2_mgrs.delete(0,END) 
            self.sensor2_lob.delete(0,END)
            self.sensor2_Rpwr.delete(0,END)
        # if Single LOB Boolean value is FALSE
        if not self.single_lob_bool:
            # try to read the Sensor 2 PWR Received value
            try:
                # read the Sensor 2 PWR Received value from the input field
                self.sensor2_power_received_dBm_val = int(self.sensor2_Rpwr.get())
                # assess if validity of Sensor 2 PWR Received value
                if self.sensor2_power_received_dBm_val > 0:
                    # raise a ValueError exception
                    raise ValueError
            # exception handling for ValueError
            except ValueError:
                # if ValueError occurs, give user the option to re-input or use default value
                choice = self.input_error(category='Sensor 2 Power Received',msg='Invalid Input',single_lob_option=True)
                # if user chooses to utilize the default Sensor 2 LOB value
                if choice == True:
                    # clear the Sensor 2 Received PWR input field
                    self.sensor2_Rpwr.delete(0,END)
                    # insert the default Sensor 2 PWR Received value
                    self.sensor2_Rpwr.insert(0,App.DEFAULT_VALUES['Sensor 2 PWR Received'])
                    # set local Sensor 2 PWR Received value to default value
                    self.sensor2_power_received_dBm_val = App.DEFAULT_VALUES['Sensor 2 PWR Received']
                # if user chooses to re-input the Sensor 2 PWR Received value
                elif choice == False:
                    # end function
                    return
                # if user chooses to only utilize a single LOB
                elif choice == 'SL':
                    # set Single LOB Boolean to TRUE
                    self.single_lob_bool = True
                    # set local Sensor 2 PWR Received value to None
                    self.sensor2_power_received_dBm_val = None
                    # clear Sensor 2 PWR Received input field
                    self.sensor2_Rpwr.delete(0,END)
        else:
            # set all local Sensor 2 values to None
            self.sensor2_mgrs_val = None
            self.sensor2_grid_azimuth_val = None
            self.sensor2_power_received_dBm_val = None
            # clear all Sensor 2 input fields
            self.sensor2_mgrs.delete(0,END) 
            self.sensor2_lob.delete(0,END)
            self.sensor2_Rpwr.delete(0,END)
        try:
            # if Single LOB and CUT boolean value are FALSE
            if not self.single_lob_bool and not self.cut_bool:
                # get input from Sensor 3 MGRS field
                self.sensor3_mgrs_val = str(self.sensor3_mgrs.get()).strip().replace(" ","")
                # assess if Sensor 3 MGRS input is valid
                if check_mgrs_input(self.sensor3_mgrs_val):
                    # if MGRS value is valid, pass on to next portion of function code
                    pass
                else:
                    # if MGRS is invalid, give user the option to re-input or use default value
                    choice = self.input_error(category='Sensor 3 Grid',msg=f'Invalid Input {self.sensor3_mgrs_val}',single_lob_option=True,cut_option=True)
                    # if user chooses to use default Sensor 3 MGRS value
                    if choice == True:
                        # clear Sensor 3 MGRS input field
                        self.sensor3_mgrs.delete(0,END)
                        # insert default Sensor 3 MGRS value into field
                        self.sensor3_mgrs.insert(0,App.DEFAULT_VALUES['Sensor 3 MGRS'])
                        # set local Sensor 3 MGRS value to default value
                        self.sensor3_mgrs_val = App.DEFAULT_VALUES['Sensor 3 MGRS']
                    # if user chooses to re-input the Sensor 3 MGRS value
                    elif choice == False:
                        # end function
                        return
                    # if user chooses to utilize only a single LOB
                    elif choice == 'SL':
                        # set Single LOB boolean value to TRUE
                        self.single_lob_bool = True
                        # set CUT boolean value to FALSE
                        self.cut_bool = False
                        # set Sensor 3 MGRS value to None
                        self.sensor3_mgrs_val = None
                        # clear Sensor 3 MGRS input field
                        self.sensor3_mgrs.delete(0,END)
                    elif choice == 'LOB/CUT':
                        # set Single LOB boolean value to FALSE
                        self.single_lob_bool = False
                        # set CUT boolean value to TRUE
                        self.cut_bool = True
                        # set Sensor 3 MGRS value to None
                        self.sensor3_mgrs_val = None
                        # clear Sensor 3 MGRS input field
                        self.sensor3_mgrs.delete(0,END)   
            # if Single LOB Boolean value is TRUE
            else:
                # set all local Sensor 3 values to None
                self.sensor3_mgrs_val = None
                self.sensor3_grid_azimuth_val = None
                self.sensor3_power_received_dBm_val = None
                # clear all Sensor 3 input fields
                self.sensor3_mgrs.delete(0,END) 
                self.sensor3_lob.delete(0,END)
                self.sensor3_Rpwr.delete(0,END)   
        # exception handling for ValueError         
        except ValueError:
            # set local Sensor 3 MGRS value to None
            self.sensor3_mgrs_val = None
        # if Single LOB and CUT Boolean value is FALSE
        if not self.single_lob_bool and not self.cut_bool:
            # try to read Sensor 3 LOB value
            try:
                # get Sensor 3 LOB value from input field
                self.sensor3_grid_azimuth_val = int(self.sensor3_lob.get())
                # assess the validity of Sensor 3 LOB input
                if self.sensor3_grid_azimuth_val < 0 or self.sensor3_grid_azimuth_val > 360:
                    # exception handling for ValueError
                    raise ValueError
            # exception for ValueError
            except ValueError:
                # if ValueError occurs, give user the option to re-input or use default value
                choice = self.input_error(category='Sensor 3 Grid Azimuth',msg='Invalid Input',single_lob_option=True,cut_option=True)
                # if users chooses to utilize the default Sensor 3 LOB value
                if choice == True:
                    # clear the Sensor 3 LOB input field
                    self.sensor3_lob.delete(0,END)
                    # insert the default Sensor 3 LOB value 
                    self.sensor3_lob.insert(0,App.DEFAULT_VALUES['Sensor 3 LOB'])   
                    # set local Sensor 3 LOB value to default value
                    self.sensor3_grid_azimuth_val = App.DEFAULT_VALUES['Sensor 3 LOB']
                # if user chooses to re-input the Sensor 3 LOB value
                elif choice == False:
                    # end function
                    return
                # if user chooses to only utilize a Single LOB
                elif choice == 'LOB/CUT':
                    # set Single LOB boolean value to TRUE
                    self.single_lob_bool = True
                    # set CUT boolean value to FALSE
                    self.cut_bool = False
                    # set Sensor 3 MGRS value to None
                    self.sensor3_mgrs_val = None
                    # clear Sensor 3 MGRS input field
                    self.sensor3_mgrs.delete(0,END) 
        # if Single LOB or CUT Boolean value is TRUE
        else:
            # set all local Sensor 3 input values to None
            self.sensor3_mgrs_val = None
            self.sensor3_grid_azimuth_val = None
            self.sensor3_power_received_dBm_val = None
            # clear all Sensor 3 input fields
            self.sensor3_mgrs.delete(0,END) 
            self.sensor3_lob.delete(0,END)
            self.sensor3_Rpwr.delete(0,END)
        # if Single LOB and CUT Boolean value is FALSE
        if not self.single_lob_bool and not self.cut_bool:
            # try to read the Sensor 3 PWR Received value
            try:
                # read the Sensor 3 PWR Received value from the input field
                self.sensor3_power_received_dBm_val = int(self.sensor3_Rpwr.get())
                # assess if validity of Sensor 3 PWR Received value
                if self.sensor3_power_received_dBm_val > 0:
                    # raise a ValueError exception
                    raise ValueError
            # exception handling for ValueError
            except ValueError:
                # if ValueError occurs, give user the option to re-input or use default value
                choice = self.input_error(category='Sensor 3 Power Received',msg='Invalid Input',single_lob_option=True,cut_option=True)
                # if user chooses to utilize the default Sensor 3 LOB value
                if choice == True:
                    # clear the Sensor 3 Received PWR input field
                    self.sensor3_Rpwr.delete(0,END)
                    # insert the default Sensor 3 PWR Received value
                    self.sensor3_Rpwr.insert(0,App.DEFAULT_VALUES['Sensor 3 PWR Received'])  
                    # set local Sensor 2 PWR Received value to default value
                    self.sensor3_power_received_dBm_val = App.DEFAULT_VALUES['Sensor 3 PWR Received']
                # if user chooses to re-input the Sensor 3 PWR Received value
                elif choice == False:
                    # end function
                    return
                # if user chooses to only utilize a single LOB
                elif choice == 'LOB/CUT':
                    # set Single LOB boolean value to TRUE
                    self.single_lob_bool = True
                    # set CUT boolean value to FALSE
                    self.cut_bool = False
                    # set Sensor 3 MGRS value to None
                    self.sensor3_mgrs_val = None
                    # clear Sensor 3 MGRS input field
                    self.sensor3_mgrs.delete(0,END)
        else:
            # set all local Sensor 3 values to None
            self.sensor3_mgrs_val = None
            self.sensor3_grid_azimuth_val = None
            self.sensor3_power_received_dBm_val = None
            # clear all Sensor 2 input fields
            self.sensor3_mgrs.delete(0,END) 
            self.sensor3_lob.delete(0,END)
            self.sensor3_Rpwr.delete(0,END)  
        # try to read the input frequency
        try:
            # read the frequency from the frequency input field
            self.frequency_MHz_val = float(self.frequency.get())
            # assess if input frequency is feasible
            if self.frequency_MHz_val < 0:
                # raise a ValueError exception
                raise ValueError
        # exception handling for ValueError
        except ValueError:
            # if ValueError occurs, give user the option to re-input or use default value
            choice = self.input_error(category='Frequency',msg='Invalid Input')
            # if user chooses to use the default frequency value
            if choice:
                # clear frequency input field
                self.frequency.delete(0,END)
                # input default frequency value in input field
                self.frequency.insert(0,App.DEFAULT_VALUES['Frequency'])
                # set local frequency value to default frequency value
                self.frequency_MHz_val = App.DEFAULT_VALUES['Frequency']
            # if user chooses to re-input the frequency value
            else:
                # end function
                return
        # try to read the input Min ERP value
        try:
            # read the Min ERP value from the input field
            self.min_wattage_val = float(self.min_ERP.get())
            # assess validity of input Min ERP value
            if self.min_wattage_val < 0:
                # raise a ValueError exception
                raise ValueError
        # exception handling for ValueError
        except ValueError:
            # if ValueError occurs, give user the option to re-input or use default value
            choice = self.input_error(category='Minimum ERP',msg='Invalid Input')
            # if user chooses to utilize the default Min ERP value
            if choice:
                # clear Min ERP input field
                self.min_ERP.delete(0,END)
                # insert default Min ERP value in input field
                self.min_ERP.insert(0,App.DEFAULT_VALUES['Min ERP'])
                # set local Min ERP value to default Min ERP value
                self.min_wattage_val = App.DEFAULT_VALUES['Min ERP']
            # if user chooses to re-input Min ERP value
            else:
                # end function
                return
        # try to read Max ERP from input field
        try:
            # read Max ERP from input field
            self.max_wattage_val = float(self.max_ERP.get())
            # assess validity of Max ERP value
            if self.max_wattage_val < 0 or self.max_wattage_val < self.min_wattage_val:
                # raise a ValueError exception
                raise ValueError
        # exception handling for ValueError
        except ValueError:
            # if ValueError occurs, give user the option to re-input or use default value
            choice = self.input_error(category='Maximum ERP',msg='Invalid Input')
            # if user chooses to use the default Max ERP value
            if choice:
                # clear Max ERP input field
                self.max_ERP.delete(0,END)
                # insert default Max ERP in input field
                self.max_ERP.insert(0,App.DEFAULT_VALUES['Max ERP'])
                # set local Max ERP value to default value
                self.max_wattage_val = App.DEFAULT_VALUES['Max ERP']
            # if user chooses to re-input the Max ERP value
            else:
                # end function
                return
        # try to read path-loss coefficient value
        try:
            # set local path-loss coefficient value to global path-loss coefficent value
            self.path_loss_coeff_val = self.path_loss_coeff
        # exception handling for ValueError
        except ValueError:
            # if ValueError occurs, give user the option to re-input or use default value
            choice = self.input_error(category='Path-Loss Coefficient',msg='Invalid Input')
            # if user chooses to use the default path-loss coefficient
            if choice:
                # set local path-loss coefficient value to default value
                self.path_loss_coeff_val = App.DEFAULT_VALUES['Path-Loss Coefficient']
                # set path-loss coefficient input field to default description
                self.option_path_loss_coeff.set(App.DEFAULT_VALUES['Path-Loss Coefficient Description'])
                # set global path-loss coefficient value to default value
                self.path_loss_coeff = App.DEFAULT_VALUES['Path-Loss Coefficient']
            # if user chooses to re-input the path-loss coefficient
            else:
                # end function
                return

    def plot_cut(self,l1c,l1r,l1l,l2c,l2r,l2l,multi_cut_bool=False):
        from utilities import convert_coords_to_mgrs, format_readable_mgrs, generate_DTG, get_polygon_area, get_distance_between_coords, get_intersection, organize_polygon_coords
        # define target classification
        self.target_class = '(CUT)'
        # set target label with updated target classification
        self.label_target_grid.configure(text=f'TARGET GRID {self.target_class}'.strip(),text_color='red')
        # get intersection of LOB centers
        self.target_coord = get_intersection(l1c, l2c)
        # get intersection of right-bound LOB errors
        intersection_l1r_l2r = get_intersection(l1r, l2r)
        # get intersection of LOB 1 right-bound error and LOB 2 left-bound error
        intersection_l1r_l2l = get_intersection(l1r, l2l)
        # get intersection of LOB 1 left-bound error and LOB 2 right-bound error
        intersection_l1l_l2r = get_intersection(l1l, l2r)
        # get intersection of left-bound LOB errors 
        intersection_l1l_l2l = get_intersection(l1l, l2l)
        # define CUT polygon
        cut_polygon = [intersection_l1r_l2r,intersection_l1r_l2l,intersection_l1l_l2l,intersection_l1l_l2r]
        # organize CUT polygon
        cut_polygon = organize_polygon_coords(cut_polygon)
        # calculate the CUT error (in acres)
        self.target_error_val = get_polygon_area(cut_polygon)
        # define CUT center MGRS grid
        self.target_mgrs = convert_coords_to_mgrs(self.target_coord)
        # define sensor 1 LOB description
        cut_description = f"Target CUT at {format_readable_mgrs(self.target_mgrs)} with {self.target_error_val:,.0f} acres of error"
        # define and set CUT area
        cut_area = self.map_widget.set_polygon(
            position_list=cut_polygon,
            fill_color=App.DEFAULT_VALUES['LOB Fill Color'],
            outline_color=App.DEFAULT_VALUES['CUT Area Outline Color'],
            border_width=App.DEFAULT_VALUES['Border Width'],
            command=self.polygon_click,
            data=cut_description)
        # add CUT polygon to the polygon list
        self.append_object(cut_area,"CUT")
        # calculate distance from sensor 1 and CUT intersection (in meters)
        if self.sensor1_mgrs_val != None: self.sensor1_distance_val = int(get_distance_between_coords(self.sensor1_coord,self.target_coord))
        # calculate distance from sensor 2 and CUT intersection (in meters)
        if self.sensor2_mgrs_val != None: self.sensor2_distance_val = int(get_distance_between_coords(self.sensor2_coord,self.target_coord))    
        # define and set the CUT target marker
        if self.sensor3_mgrs_val != None: self.sensor3_distance_val = int(get_distance_between_coords(self.sensor3_coord,self.target_coord))    
        # define and set the CUT target marker
        cut_target_marker = self.map_widget.set_marker(
            deg_x=self.target_coord[0], 
            deg_y=self.target_coord[1], 
            text=f'{format_readable_mgrs(self.target_mgrs)}',
            image_zoom_visibility=(10, float("inf")),
            marker_color_circle='white',
            icon=self.target_image,
            command=self.marker_click,
            data=f'TGT (CUT)\n{format_readable_mgrs(self.target_mgrs)}\n{generate_DTG()}')
        # add CUT marker to target marker list
        self.append_object(cut_target_marker,"TGT")
        # generate sensor 1 distance from target text     
        if self.sensor1_mgrs_val != None: 
            # generate sensor 1 distance from target text
            dist_sensor1_text = self.generate_sensor_distance_text(self.sensor1_distance_val)
            # set sensor 1 distance field
            if self.sensor1_distance.cget("text") != '' and multi_cut_bool:
                if self.sensor1_distance.cget("text") > dist_sensor1_text:
                    self.sensor1_distance.configure(text=dist_sensor1_text,text_color='white')
            else:
                self.sensor1_distance.configure(text=dist_sensor1_text,text_color='white')
        if self.sensor2_mgrs_val != None: 
            # generate sensor 2 distance from target text
            dist_sensor2_text = self.generate_sensor_distance_text(self.sensor2_distance_val)
            # set sensor 2 distance field
            if self.sensor2_distance.cget("text") != '' and multi_cut_bool:
                if self.sensor2_distance.cget("text") > dist_sensor2_text:
                    self.sensor2_distance.configure(text=dist_sensor2_text,text_color='white')
            else:
                self.sensor2_distance.configure(text=dist_sensor2_text,text_color='white')
        if self.sensor3_mgrs_val != None:
            # generate sensor 3 distance from target text
            dist_sensor3_text = self.generate_sensor_distance_text(self.sensor3_distance_val)
            # set sensor 3 distance field
            if self.sensor3_distance.cget("text") != '' and multi_cut_bool:
                if self.sensor3_distance.cget("text") > dist_sensor3_text:
                    self.sensor3_distance.configure(text=dist_sensor3_text,text_color='white')
            else:
                self.sensor3_distance.configure(text=dist_sensor3_text,text_color='white')
        # set target grid field with CUT center MGRS
        if multi_cut_bool: self.target_grid.configure(text="MULTIPLE CUTS")
        if not multi_cut_bool: self.target_grid.configure(text=f'{format_readable_mgrs(self.target_mgrs)}',text_color='yellow')
        # set target error field
        if multi_cut_bool: self.target_error.configure(text="MULTIPLE CUTS")
        if not multi_cut_bool: self.target_error.configure(text=f'{self.target_error_val:,.0f} acres',text_color='white')
        # set map position at CUT target 
        self.map_widget.set_position(self.target_coord[0],self.target_coord[1])
        
    def plot_lobs(self,s1lnmc,s1lfmc,s2lnmc,s2lfmc,s3lnmc,s3lfmc):
        from utilities import convert_coords_to_mgrs, format_readable_mgrs, generate_DTG, get_distance_between_coords
        import numpy as np
        num_lobs = 3-[self.sensor1_mgrs_val,self.sensor2_mgrs_val,self.sensor3_mgrs_val].count(None)
        # set target class
        self.target_class = f'({num_lobs} {"LOB" if num_lobs == 1 else "LOBs"})'
        # set target grid label to include target classification
        self.label_target_grid.configure(text=f'TARGET GRIDs {self.target_class}'.strip(),text_color='red')
        # display info message that no LOB intersection exists  
        self.show_info("No LOB intersection(s) detected!")
        if self.sensor1_mgrs_val != None:
            # calculate sensor 1 target coordinate
            sensor1_target_coord = [np.average([s1lnmc[0],s1lfmc[0]]),np.average([s1lnmc[1],s1lfmc[1]])]
            # calculate sensor 1 target MGRS
            sensor1_target_mgrs = convert_coords_to_mgrs(sensor1_target_coord)
            # define and set sensor 1 target marker
            target1_marker = self.map_widget.set_marker(
                deg_x=sensor1_target_coord[0], 
                deg_y=sensor1_target_coord[1], 
                text=f'{format_readable_mgrs(sensor1_target_mgrs)}', 
                image_zoom_visibility=(10, float("inf")),
                marker_color_circle='white',
                icon=self.target_image,
                command=self.marker_click,
                data=f'TGT (LOB)\nEWT 1\n{format_readable_mgrs(sensor1_target_mgrs)}\n{generate_DTG()}')
            # add sensor 1 target marker to target marker list
            self.append_object(target1_marker,"TGT")
            # calculate sensor 1 distance to target 1
            self.sensor1_distance_val = int(get_distance_between_coords(self.sensor1_coord,sensor1_target_coord))
            # generate sensor 1 distance from target text     
            dist_sensor1_text = self.generate_sensor_distance_text(self.sensor1_distance_val)
            # set sensor 1 distance field
            self.sensor1_distance.configure(text=dist_sensor1_text,text_color='white')
        else:
            sensor1_target_mgrs = None
            self.sensor1_lob_error_acres = None
            sensor1_target_coord = None
        if self.sensor2_mgrs_val != None:
            # calculate sensor 2 target coordinate
            sensor2_target_coord = [np.average([s2lnmc[0],s2lfmc[0]]),np.average([s2lnmc[1],s2lfmc[1]])]
            # calculate sensor 2 target MGRS
            sensor2_target_mgrs = convert_coords_to_mgrs(sensor2_target_coord)
            # define and set sensor 2 target marker
            target2_marker = self.map_widget.set_marker(
                deg_x=sensor2_target_coord[0], 
                deg_y=sensor2_target_coord[1], 
                text=f'{format_readable_mgrs(sensor2_target_mgrs)}', 
                image_zoom_visibility=(10, float("inf")),
                marker_color_circle='white',
                icon=self.target_image,
                command=self.marker_click,
                data=f'TGT (LOB)\nEWT 2\n{format_readable_mgrs(sensor2_target_mgrs)}\n{generate_DTG()}')
            # add sensor 2 target marker to tarket marker list
            self.append_object(target2_marker,"TGT")
            # calculate sensor 1 distance to target 2
            self.sensor2_distance_val = int(get_distance_between_coords(self.sensor2_coord,sensor2_target_coord))
            # generate sensor 2 distance from target text       
            dist_sensor2_text = self.generate_sensor_distance_text(self.sensor2_distance_val)
            # set sensor 2 distance field
            self.sensor2_distance.configure(text=dist_sensor2_text,text_color='white')
        else:
            sensor2_target_mgrs = None
            self.sensor2_lob_error_acres = None
            sensor2_target_coord = None
        if self.sensor3_mgrs_val != None:
            # calculate sensor 3 target coordinate
            sensor3_target_coord = [np.average([s3lnmc[0],s3lfmc[0]]),np.average([s3lnmc[1],s3lfmc[1]])]
            # calculate sensor 3 target MGRS
            sensor3_target_mgrs = convert_coords_to_mgrs(sensor3_target_coord)
            # define and set sensor 3 target marker
            target3_marker = self.map_widget.set_marker(
                deg_x=sensor3_target_coord[0], 
                deg_y=sensor3_target_coord[1], 
                text=f'{format_readable_mgrs(sensor3_target_mgrs)}', 
                image_zoom_visibility=(10, float("inf")),
                marker_color_circle='white',
                icon=self.target_image,
                command=self.marker_click,
                data=f'TGT (LOB)\nEWT 3\n{format_readable_mgrs(sensor3_target_mgrs)}\n{generate_DTG()}')
            # add sensor 3 target marker to tarket marker list
            self.append_object(target3_marker,"TGT")
            # calculate sensor 3 distance to target 3
            self.sensor3_distance_val = int(get_distance_between_coords(self.sensor3_coord,sensor3_target_coord))
            # generate sensor 3 distance from target text       
            dist_sensor3_text = self.generate_sensor_distance_text(self.sensor3_distance_val)
            # set sensor 3 distance field
            self.sensor3_distance.configure(text=dist_sensor3_text,text_color='white')
        else:
            sensor3_target_mgrs = None
            self.sensor3_lob_error_acres = None
            sensor3_target_coord = None
        nl = "\n"
        # set target grid field
        target_grid_list = [f'{format_readable_mgrs(x)}' for x in [sensor1_target_mgrs,sensor2_target_mgrs,sensor3_target_mgrs] if x != None]
        self.target_grid.configure(text=f'{nl.join(target_grid_list)}',text_color='yellow')
        # set target error field
        self.target_error.configure(text='Multiple LOBs',text_color='white')
        # define multi-target MGRS value
        self.target_mgrs = f'{", ".join(target_grid_list)}'
        # define multi-target coordinates
        target_coord_list = [f'{", ".join(x)}' for x in [str(sensor1_target_coord),str(sensor2_target_coord),str(sensor3_target_coord)] if x != None]
        self.target_coord = f'{" | ".join(target_coord_list)}'

    def ewt_function(self,*args):
        """
        Function to calculate target location given EWT input(s)
        """
        import numpy as np
        from utilities import check_for_intersection, convert_coords_to_mgrs, convert_mgrs_to_coords, format_readable_mgrs, generate_DTG, get_center_coord, get_coords_from_LOBs, get_distance_between_coords, get_emission_distance, get_intersection, get_line, get_polygon_area, organize_polygon_coords
        # reset fields to defaults
        self.label_target_grid.configure(text='')
        self.target_grid.configure(text='')
        self.sensor1_distance.configure(text='')
        self.sensor2_distance.configure(text='')
        self.sensor3_distance.configure(text='')
        self.target_error.configure(text='')
        self.target_class = ''        
        # read the user input fields
        self.read_ewt_input_fields()
        # convert sensor 1 mgrs to coords
        self.sensor1_coord = convert_mgrs_to_coords(self.sensor1_mgrs_val)
        # clear sensor 1 distance
        self.sensor1_distance.configure(text='')
        # calculate minimum distance from sensor 1 to TGT (in km)
        self.sensor1_min_distance_km = get_emission_distance(self.min_wattage_val,self.frequency_MHz_val,self.transmitter_gain_dBi_val,self.sensor1_receiver_gain_dBi,self.sensor1_power_received_dBm_val,self.transmitter_height_m_val,self.sensor1_receiver_height_m_val,self.temp_f_val,self.path_loss_coeff_val,weather_coeff=4/3,pure_pathLoss=True)
        # convert minimum distance from sensor 1 to TGT to meters
        self.sensor1_min_distance_m = self.sensor1_min_distance_km * 1000
        # calculate maximum distance from sensor 1 to TGT (in km)
        self.sensor1_max_distance_km = get_emission_distance(self.max_wattage_val,self.frequency_MHz_val,self.transmitter_gain_dBi_val,self.sensor1_receiver_gain_dBi,self.sensor1_power_received_dBm_val,self.transmitter_height_m_val,self.sensor1_receiver_height_m_val,self.temp_f_val,self.path_loss_coeff_val,weather_coeff=4/3,pure_pathLoss=True)
        # calculate minimum distance from sensor 1 to TGT (in km)
        self.sensor1_max_distance_m = self.sensor1_max_distance_km * 1000
        # calculate sensor 1 LOB boundaries
        sensor1_lob_center, sensor1_lob_near_right_coord, sensor1_lob_near_left_coord, sensor1_lob_near_middle_coord, sensor1_lob_far_right_coord, sensor1_lob_far_left_coord, sensor1_lob_far_middle_coord, sensor1_center_coord_list = get_coords_from_LOBs(self.sensor1_coord,self.sensor1_grid_azimuth_val,self.sensor1_error,self.sensor1_min_distance_m,self.sensor1_max_distance_m)
        # define sensor 1 LOB polygon
        sensor1_lob_polygon = [sensor1_lob_near_right_coord,sensor1_lob_far_right_coord,sensor1_lob_far_left_coord,sensor1_lob_near_left_coord]
        # organize sensor 1 LOB polygon points
        sensor1_lob_polygon = organize_polygon_coords(sensor1_lob_polygon)
        # calculate sensor 1 LOB error (in acres)
        sensor1_lob_error_acres = get_polygon_area(sensor1_lob_polygon)
        # define sensor 1 LOB description
        sensor1_lob_description = f"EWT 1 ({self.sensor1_mgrs_val}) LOB at bearing {int(self.sensor1_grid_azimuth_val)}° between {self.sensor1_min_distance_m/1000:,.2f}km and {self.sensor1_max_distance_m/1000:,.2f}km with {sensor1_lob_error_acres:,.0f} acres of error"
        # define sensor 1 LOB's center line
        lob1_center = get_line(self.sensor1_coord, sensor1_lob_far_middle_coord)
        # define sensor 1 LOB's right-bound error line
        lob1_right_bound = get_line(sensor1_lob_near_right_coord, sensor1_lob_far_right_coord)
        # define sensor 1 LOB's left-bound error line
        lob1_left_bound = get_line(sensor1_lob_near_left_coord, sensor1_lob_far_left_coord)
        # define and set sensor 1 marker on the map
        ew_team1_marker = self.map_widget.set_marker(
            self.sensor1_coord[0], 
            self.sensor1_coord[1],
            text="",
            image_zoom_visibility=(10, float("inf")),
            marker_color_circle='white',
            text_color='black',
            icon=self.ew_team1_image,
            command=self.marker_click,
            data=f'EWT 1\n{format_readable_mgrs(self.sensor1_mgrs_val)}\n{generate_DTG()}')
        # add sensor 1 marker to EWT marker list
        self.append_object(ew_team1_marker,"EWT")
        # define and set sensor 1 center line
        sensor1_lob = self.map_widget.set_polygon(
            position_list=[(self.sensor1_coord[0],self.sensor1_coord[1]),(sensor1_lob_far_middle_coord[0],sensor1_lob_far_middle_coord[1])],
            fill_color=App.DEFAULT_VALUES['LOB Fill Color'],
            outline_color=App.DEFAULT_VALUES['LOB Center Line Color'],
            border_width=App.DEFAULT_VALUES['Border Width'],
            command=self.polygon_click,
            data="(LINE) "+sensor1_lob_description)
        # add sensor 1 LOB center-line to polygon list
        self.append_object(sensor1_lob,"LOB")
        # define and set sensor 1 LOB area
        sensor1_lob_area = self.map_widget.set_polygon(
            position_list=sensor1_lob_polygon,
            fill_color=App.DEFAULT_VALUES['LOB Fill Color'],
            outline_color=App.DEFAULT_VALUES['LOB Area Outline Color'],
            border_width=App.DEFAULT_VALUES['Border Width'],
            command=self.polygon_click,
            data="(AREA) "+sensor1_lob_description)
        # add sensor 1 LOB area to polygon list
        self.append_object(sensor1_lob_area,"LOB")
        # if sensor 2 has non-None input values
        if self.sensor2_mgrs_val != None and self.sensor2_grid_azimuth_val != None and self.sensor2_power_received_dBm_val != None:
            # convert sensor 2 MGRS to coordinates
            self.sensor2_coord = convert_mgrs_to_coords(self.sensor2_mgrs_val)
            # set map position to the middle of sensor 1 and sensor 2
            self.map_widget.set_position(np.average([self.sensor1_coord[0],self.sensor2_coord[0]]),np.average([self.sensor1_coord[1],self.sensor2_coord[1]]))
            # clear sensor 2 distance 
            self.sensor2_distance.configure(text='')
            # calculate sensor 2 minimum distance (in km)
            self.sensor2_min_distance_km = get_emission_distance(self.min_wattage_val,self.frequency_MHz_val,self.transmitter_gain_dBi_val,self.sensor2_receiver_gain_dBi,self.sensor2_power_received_dBm_val,self.transmitter_height_m_val,self.sensor2_receiver_height_m_val,self.temp_f_val,self.path_loss_coeff_val,weather_coeff=4/3,pure_pathLoss=True)
            # convert sensor 2 minimum distance to meters
            self.sensor2_min_distance_m = self.sensor2_min_distance_km * 1000
            # calculate sensor 2 maximum distance (in km)    
            self.sensor2_max_distance_km = get_emission_distance(self.max_wattage_val,self.frequency_MHz_val,self.transmitter_gain_dBi_val,self.sensor2_receiver_gain_dBi,self.sensor2_power_received_dBm_val,self.transmitter_height_m_val,self.sensor2_receiver_height_m_val,self.temp_f_val,self.path_loss_coeff_val,weather_coeff=4/3,pure_pathLoss=True)
            # convert sensor 2 maximum distance to meters
            self.sensor2_max_distance_m = self.sensor2_max_distance_km * 1000
            # calculate sensor 2 LOB boundaries
            sensor2_lob_center, sensor2_lob_near_right_coord, sensor2_lob_near_left_coord, sensor2_lob_near_middle_coord, sensor2_lob_far_right_coord, sensor2_lob_far_left_coord, sensor2_lob_far_middle_coord, sensor2_center_coord_list = get_coords_from_LOBs(self.sensor2_coord,self.sensor2_grid_azimuth_val,self.sensor2_error,self.sensor2_min_distance_m,self.sensor2_max_distance_m)
            # define sensor 2 LOB polygon
            sensor2_lob_polygon = [sensor2_lob_near_right_coord,sensor2_lob_far_right_coord,sensor2_lob_far_left_coord,sensor2_lob_near_left_coord]
            # organize sensor 2 LOB polygon
            sensor2_lob_polygon = organize_polygon_coords(sensor2_lob_polygon)
            # calculate LOB 2 sensor error (in acres)
            sensor2_lob_error_acres = get_polygon_area(sensor2_lob_polygon)
            # define LOB 2 description
            sensor2_lob_description = f"EWT 2 ({self.sensor2_mgrs_val}) LOB at bearing {int(self.sensor2_grid_azimuth_val)}° between {self.sensor2_min_distance_m/1000:,.2f}km and {self.sensor2_max_distance_m/1000:,.2f}km with {sensor2_lob_error_acres:,.0f} acres of error"
            # define sensor 2 LOB center-line
            lob2_center = get_line(self.sensor2_coord, sensor2_lob_far_middle_coord)
            # define sensor 2 LOB right-bound error line
            lob2_right_bound = get_line(sensor2_lob_near_right_coord, sensor2_lob_far_right_coord)
            # define sensor 2 LOB left-bound error line
            lob2_left_bound = get_line(sensor2_lob_near_left_coord, sensor2_lob_far_left_coord)
            # define and set sensor 2 marker on the map
            ew_team2_marker = self.map_widget.set_marker(
                deg_x=self.sensor2_coord[0], 
                deg_y=self.sensor2_coord[1], 
                text="", 
                image_zoom_visibility=(10, float("inf")),
                marker_color_circle='white',
                text_color='black',
                icon=self.ew_team2_image,
                command=self.marker_click,
                data=f'EWT 2\n{format_readable_mgrs(self.sensor1_mgrs_val)}\n{generate_DTG()}')
            # add sensor 2 marker to EWT marker list
            self.append_object(ew_team2_marker,"EWT")
            # define and set sensor 2 LOB area
            sensor2_lob = self.map_widget.set_polygon(
                position_list=[(self.sensor2_coord[0],self.sensor2_coord[1]),(sensor2_lob_far_middle_coord[0],sensor2_lob_far_middle_coord[1])],
                fill_color=App.DEFAULT_VALUES['LOB Fill Color'],
                outline_color=App.DEFAULT_VALUES['LOB Center Line Color'],
                border_width=App.DEFAULT_VALUES['Border Width'],
                command=self.polygon_click,
                data="(LINE) "+sensor2_lob_description)
            # add sensor 2 LOB area to polygon list
            self.append_object(sensor2_lob,"LOB")
            # define and set sensor 2 LOB area
            sensor2_lob_area = self.map_widget.set_polygon(
                position_list=sensor2_lob_polygon,
                fill_color=App.DEFAULT_VALUES['LOB Fill Color'],
                outline_color=App.DEFAULT_VALUES['LOB Area Outline Color'],
                border_width=App.DEFAULT_VALUES['Border Width'],
                command=self.polygon_click,
                data="(AREA) "+sensor2_lob_description)
            # add LOB area to polygon list
            self.append_object(sensor2_lob_area,"LOB")
            # if sensor 3 has non-None input values 
            if self.sensor3_mgrs_val != None and self.sensor3_grid_azimuth_val != None and self.sensor3_power_received_dBm_val != None:
                # define target classification
                self.target_class = '(FIX)'
                # set target label with updated target classification
                self.label_target_grid.configure(text=f'TARGET GRID {self.target_class}'.strip(),text_color='red')
                # convert sensor 3 MGRS to coordinates
                self.sensor3_coord = convert_mgrs_to_coords(self.sensor3_mgrs_val)
                # set map position to the middle of sensor 1, 2, and 3
                self.map_widget.set_position(np.average([self.sensor1_coord[0],self.sensor2_coord[0],self.sensor3_coord[0]]),np.average([self.sensor1_coord[1],self.sensor2_coord[1],self.sensor3_coord[1]]))
                # clear sensor 3 distance field
                self.sensor3_distance.configure(text='')
                # calculate sensor 3 minimum distance (in km)
                self.sensor3_min_distance_km = get_emission_distance(self.min_wattage_val,self.frequency_MHz_val,self.transmitter_gain_dBi_val,self.sensor3_receiver_gain_dBi,self.sensor3_power_received_dBm_val,self.transmitter_height_m_val,self.sensor3_receiver_height_m_val,self.temp_f_val,self.path_loss_coeff_val,weather_coeff=4/3,pure_pathLoss=True)
                # convert sensor 3 minimum distance to meters
                self.sensor3_min_distance_m = self.sensor3_min_distance_km * 1000
                # calculate sensor 3 maximum distance (in km)    
                self.sensor3_max_distance_km = get_emission_distance(self.max_wattage_val,self.frequency_MHz_val,self.transmitter_gain_dBi_val,self.sensor3_receiver_gain_dBi,self.sensor3_power_received_dBm_val,self.transmitter_height_m_val,self.sensor3_receiver_height_m_val,self.temp_f_val,self.path_loss_coeff_val,weather_coeff=4/3,pure_pathLoss=True)
                # convert sensor 3 maximum distance to meters
                self.sensor3_max_distance_m = self.sensor3_max_distance_km * 1000
                # calculate sensor 3 LOB boundaries
                sensor3_lob_center, sensor3_lob_near_right_coord, sensor3_lob_near_left_coord, sensor3_lob_near_middle_coord, sensor3_lob_far_right_coord, sensor3_lob_far_left_coord, sensor3_lob_far_middle_coord, sensor3_center_coord_list = get_coords_from_LOBs(self.sensor3_coord,self.sensor3_grid_azimuth_val,self.sensor3_error,self.sensor3_min_distance_m,self.sensor3_max_distance_m)
                # define sensor 3 LOB polygon
                sensor3_lob_polygon = [sensor3_lob_near_right_coord,sensor3_lob_far_right_coord,sensor3_lob_far_left_coord,sensor3_lob_near_left_coord]
                # organize sensor 3 LOB polygon
                sensor3_lob_polygon = organize_polygon_coords(sensor3_lob_polygon)
                # calculate LOB 3 sensor error (in acres)
                sensor3_lob_error_acres = get_polygon_area(sensor3_lob_polygon)
                # define sensor 3 LOB description
                sensor3_lob_description = f"EWT 3 ({self.sensor3_mgrs_val}) LOB at bearing {int(self.sensor3_grid_azimuth_val)}° between {self.sensor3_min_distance_m/1000:,.2f}km and {self.sensor3_max_distance_m/1000:,.2f}km with {sensor3_lob_error_acres:,.0f} acres of error"
                # define sensor 3 LOB center-line
                lob3_center = get_line(self.sensor3_coord, sensor3_lob_far_middle_coord)
                # define sensor 3 LOB right-bound error line
                lob3_right_bound = get_line(sensor3_lob_near_right_coord, sensor3_lob_far_right_coord)
                # define sensor 3 LOB left-bound error line
                lob3_left_bound = get_line(sensor3_lob_near_left_coord, sensor3_lob_far_left_coord)
                # define and plot sensor 3 marker on the map
                ew_team3_marker = self.map_widget.set_marker(
                    deg_x=self.sensor3_coord[0], 
                    deg_y=self.sensor3_coord[1], 
                    text="", 
                    image_zoom_visibility=(10, float("inf")),
                    marker_color_circle='white',
                    text_color='black',
                    icon=self.ew_team3_image,
                    command=self.marker_click,
                    data=f'EWT 3\n{format_readable_mgrs(self.sensor1_mgrs_val)}\n{generate_DTG()}')
                # add sensor 3 marker to EWT marker list
                self.append_object(ew_team3_marker,"EWT")
                # define and set sensor 3 LOB area
                sensor3_lob = self.map_widget.set_polygon(
                    position_list=[(self.sensor3_coord[0],self.sensor3_coord[1]),(sensor3_lob_far_middle_coord[0],sensor3_lob_far_middle_coord[1])],
                    fill_color=App.DEFAULT_VALUES['LOB Fill Color'],
                    outline_color=App.DEFAULT_VALUES['LOB Center Line Color'],
                    border_width=App.DEFAULT_VALUES['Border Width'],
                    command=self.polygon_click,
                    data="(LINE) "+sensor3_lob_description)
                # add sensor 2 LOB area to polygon list
                self.append_object(sensor3_lob,"LOB")
                # define and set sensor 2 LOB area
                sensor3_lob_area = self.map_widget.set_polygon(
                    position_list=sensor3_lob_polygon,
                    fill_color=App.DEFAULT_VALUES['LOB Fill Color'],
                    outline_color=App.DEFAULT_VALUES['LOB Area Outline Color'],
                    border_width=App.DEFAULT_VALUES['Border Width'],
                    command=self.polygon_click,
                    data="(AREA) "+sensor3_lob_description)
                # add LOB area to polygon list
                self.append_object(sensor3_lob_area,"LOB")
                ewt1_ewt2_intersection_bool = check_for_intersection(self.sensor1_coord,sensor1_lob_far_middle_coord,self.sensor2_coord,sensor2_lob_far_middle_coord)
                ewt2_ewt3_intersection_bool = check_for_intersection(self.sensor2_coord,sensor2_lob_far_middle_coord,self.sensor3_coord,sensor3_lob_far_middle_coord)
                ewt1_ewt3_intersection_bool = check_for_intersection(self.sensor1_coord,sensor1_lob_far_middle_coord,self.sensor3_coord,sensor3_lob_far_middle_coord)
                # assess if fix exists
                if ewt1_ewt2_intersection_bool and ewt2_ewt3_intersection_bool and ewt1_ewt3_intersection_bool:
                    intersection_1_2 = get_intersection(lob1_center,lob2_center)
                    intersection_1_3 = get_intersection(lob1_center,lob3_center)
                    intersection_2_3 = get_intersection(lob2_center,lob3_center)
                    fix_coord = get_center_coord([intersection_1_2,intersection_1_3,intersection_2_3])
                    self.target_coord = fix_coord
                    self.target_mgrs = convert_coords_to_mgrs(self.target_coord)
                    self.sensor1_distance_val = int(get_distance_between_coords(self.sensor1_coord,self.target_coord))
                    self.sensor2_distance_val = int(get_distance_between_coords(self.sensor2_coord,self.target_coord))
                    self.sensor3_distance_val = int(get_distance_between_coords(self.sensor3_coord,self.target_coord))
                    self.target_error_val = 5
                    fix_description = f"Target FIX at {format_readable_mgrs(self.target_mgrs)} with {self.target_error_val:,.0f} acres of error"
                    fix_target_marker = self.map_widget.set_marker(
                        deg_x=self.target_coord[0], 
                        deg_y=self.target_coord[1], 
                        text=f'{format_readable_mgrs(self.target_mgrs)}',
                        image_zoom_visibility=(10, float("inf")),
                        marker_color_circle='white',
                        icon=self.target_image,
                        command=self.marker_click,
                        data=f'TGT {self.target_class}\n{format_readable_mgrs(self.target_mgrs)}\n{generate_DTG()}')
                    # add FIX marker to target marker list
                    self.append_object(fix_target_marker,"TGT")
                    # generate sensor 1 distance from target text     
                    dist_sensor1_text = self.generate_sensor_distance_text(self.sensor1_distance_val)
                    # set sensor 1 distance field
                    self.sensor1_distance.configure(text=dist_sensor1_text,text_color='white')
                    # generate sensor 2 distance from target text       
                    dist_sensor2_text = self.generate_sensor_distance_text(self.sensor2_distance_val)
                    # set sensor 2 distance field
                    self.sensor2_distance.configure(text=dist_sensor2_text,text_color='white')
                    # set target grid field with CUT center MGRS
                    dist_sensor3_text = self.generate_sensor_distance_text(self.sensor3_distance_val)
                    # set sensor 2 distance field
                    self.sensor3_distance.configure(text=dist_sensor3_text,text_color='white')
                    # set target grid field with CUT center MGRS
                    self.target_grid.configure(text=f'{format_readable_mgrs(self.target_mgrs)}',text_color='yellow')
                    # set target error field
                    self.target_error.configure(text=f'{self.target_error_val:,.0f} acres',text_color='white')
                    # set map position at CUT target 
                    self.map_widget.set_position(self.target_coord[0],self.target_coord[1])
                    fix_polygon = [intersection_1_2,intersection_2_3,intersection_1_3]
                    # organize CUT polygon
                    fix_polygon = organize_polygon_coords(fix_polygon)
                    # calculate the FIX error (in acres)
                    self.target_error_val = get_polygon_area(fix_polygon)
                    # define sensor FIX description
                    fix_description = f"Target FIX with {self.target_error_val:,.0f} acres of error"
                    # define and set CUT area
                    fix_area = self.map_widget.set_polygon(
                        position_list=fix_polygon,
                        fill_color=App.DEFAULT_VALUES['LOB Fill Color'],
                        outline_color=App.DEFAULT_VALUES['FIX Area Outline Color'],
                        border_width=App.DEFAULT_VALUES['Border Width'],
                        command=self.polygon_click,
                        data=fix_description)
                    self.append_object(fix_area,"FIX")
                # EWT 1 & 2 CUT, EWT 3 LOB (TOTAL 1 CUT)
                elif ewt1_ewt2_intersection_bool and not ewt2_ewt3_intersection_bool and not ewt1_ewt3_intersection_bool:
                    self.plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob2_center,lob2_right_bound,lob2_left_bound)
                # EWT 2 & 3 CUT, EWT 1 LOB (TOTAL 1 CUT)
                elif not ewt1_ewt2_intersection_bool and ewt2_ewt3_intersection_bool and not ewt1_ewt3_intersection_bool:
                    self.plot_cut(lob2_center,lob2_right_bound,lob2_left_bound,lob3_center,lob3_right_bound,lob3_left_bound)
                # EWT 1 & 3 CUT, EWT 2 LOB (TOTAL 1 CUT)
                elif not ewt1_ewt2_intersection_bool and not ewt2_ewt3_intersection_bool and ewt1_ewt3_intersection_bool:
                    self.plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob3_center,lob3_right_bound,lob3_left_bound)
                # EWT 1 & 2 CUT, EWT 2 & 3 NO CUT, EWT 1 & 3 CUT (TOTAL 2 CUT)
                elif ewt1_ewt2_intersection_bool and not ewt2_ewt3_intersection_bool and ewt1_ewt3_intersection_bool:
                    self.plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob2_center,lob2_right_bound,lob2_left_bound,True)
                    self.plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob3_center,lob3_right_bound,lob3_left_bound,True)
                # EWT 1 & 2 CUT, EWT 2 & 3 CUT, EWT 1 & 3 NO CUT (TOTAL 2 CUT)
                elif ewt1_ewt2_intersection_bool and ewt2_ewt3_intersection_bool and not ewt1_ewt3_intersection_bool:
                    self.plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob2_center,lob2_right_bound,lob2_left_bound,True)
                    self.plot_cut(lob2_center,lob2_right_bound,lob2_left_bound,lob3_center,lob3_right_bound,lob3_left_bound,True) 
                # EWT 1 & 2 NO CUT, EWT 2 & 3 CUT, EWT 1 & 3 CUT (TOTAL 2 CUT)
                elif not ewt1_ewt2_intersection_bool and ewt2_ewt3_intersection_bool and ewt1_ewt3_intersection_bool:
                    self.plot_cut(lob2_center,lob2_right_bound,lob2_left_bound,lob3_center,lob3_right_bound,lob3_left_bound,True)
                    self.plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob3_center,lob3_right_bound,lob3_left_bound,True)
                # No intersections between an EWT LOBs
                elif not ewt1_ewt2_intersection_bool and not ewt2_ewt3_intersection_bool and not ewt1_ewt3_intersection_bool:
                    self.plot_lobs(sensor1_lob_near_middle_coord,sensor1_lob_far_middle_coord,sensor2_lob_near_middle_coord,sensor2_lob_far_middle_coord,sensor3_lob_near_middle_coord,sensor3_lob_far_middle_coord)

                "Need to assess all combinations of cuts to include multiple cuts"
            # only sensor 1 and 2 have non-None input values
            else:
                sensor3_lob_near_middle_coord = None; sensor3_lob_far_middle_coord = None
                # set map zoon level
                self.map_widget.set_zoom(15)
                # assess if cut exists between EWT 1 & EWT 2 LOBs
                ewt1_ewt2_intersection_bool = check_for_intersection(self.sensor1_coord,sensor1_lob_far_middle_coord,self.sensor2_coord,sensor2_lob_far_middle_coord)
                # if there is an intersection between sensor 1 and 2
                if ewt1_ewt2_intersection_bool:
                    self.plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob2_center,lob2_right_bound,lob2_left_bound)
                # if there is no intersection between LOBs
                else:
                    self.plot_lobs(sensor1_lob_near_middle_coord,sensor1_lob_far_middle_coord,sensor2_lob_near_middle_coord,sensor2_lob_far_middle_coord,sensor3_lob_near_middle_coord,sensor3_lob_far_middle_coord)
        # if there is only one LOB
        else:
            sensor2_lob_near_middle_coord = None; sensor2_lob_far_middle_coord = None
            sensor3_lob_near_middle_coord = None; sensor3_lob_far_middle_coord = None
            # set mag zoom level
            self.map_widget.set_zoom(16)
            # define target classification
            self.target_class = '(LOB)'
            # set target grid label to include target classification
            self.label_target_grid.configure(text=f'TARGET GRID {self.target_class}'.strip(),text_color='red')
            # calculate target coord
            self.target_coord = [np.average([sensor1_lob_near_middle_coord[0],sensor1_lob_far_middle_coord[0]]),np.average([sensor1_lob_near_middle_coord[1],sensor1_lob_far_middle_coord[1]])]
            # set map position between sensor 1 coord and target coord
            self.map_widget.set_position(np.average([self.sensor1_coord[0],self.target_coord[0]]),np.average([self.sensor1_coord[1],self.target_coord[1]]))
            # determine target MGRS grid
            self.target_mgrs = convert_coords_to_mgrs(self.target_coord)
            # define and set single LOB target marker
            single_lob_target_marker = self.map_widget.set_marker(
                deg_x=self.target_coord[0], 
                deg_y=self.target_coord[1], 
                text=f'{format_readable_mgrs(self.target_mgrs)}', 
                image_zoom_visibility=(10, float("inf")),
                marker_color_circle='white',
                icon=self.target_image,
                command=self.marker_click,
                data=f'TGT {self.target_class}\n{format_readable_mgrs(self.target_mgrs)}\n{generate_DTG()}')
            # add single LOB target marker to target marker list
            self.append_object(single_lob_target_marker,"TGT")
            # set target grid field
            self.target_grid.configure(text=f'{format_readable_mgrs(self.target_mgrs)}',text_color='yellow')
            # calculate sensor 1 distance to target
            self.sensor1_distance_val = int(get_distance_between_coords(self.sensor1_coord,self.target_coord))
            # generate sensor 1 distance text
            dist_sensor1_text = self.generate_sensor_distance_text(self.sensor1_distance_val)
            # set sensor 1 distance string
            self.sensor1_distance.configure(text=dist_sensor1_text,text_color='white')
            # set sensor 2 distance string to "N/A"
            self.sensor2_distance.configure(text='N/A',text_color='white')
            # set sensor 3 distance string to "N/A"
            self.sensor3_distance.configure(text='N/A',text_color='white')
            # set target error to sensor 1 LOB error
            self.target_error.configure(text=f'{sensor1_lob_error_acres:,.0f} acres',text_color='white')
            # define target error
            self.target_error_val = sensor1_lob_error_acres
    
    def generate_sensor_distance_text(self,distance):
        """
        Generate sensor distance string w/ adjusted units of measurement
        
        Parameters:
        ----------
        self: App Object
            GUI application object
        distance : float
            Sensor distance to target in meters 

        Returns:
        ----------
        String
            Sensor distance string with adjusted units of measurement
        """
        # set default unit of measurement
        distance_unit = 'm'
        # if distance is greater than 1000m
        if distance >= 1000:
            # convert meters to km
            distance /= 1000
            # change unit of measurement to km
            distance_unit = 'km'
        # return distance string
        return f'{distance:,.2f}{distance_unit}'
    
    def check_coord_input(self,coord_input):
        """
        Determine if the coordinates input is valid

        Parameters
        ----------
        self: App Object
            GUI application object
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
            return coord_list_range_check(coord_input)
        # check if tuple input
        elif isinstance(coord_input, tuple):
            return coord_list_range_check(list(coord_input))
        
    def correct_coord_input(self,coord):
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
    
    def log_target_data(self):
        from utilities import generate_DTG
        """
        Logs current input fields and targeting data in a date-specific csv file

        Parameters:
        ----------
        self: App Object
            GUI application object

        Returns:
        ----------
        None

        """        
        import datetime
        import pandas as pd
        # define log columns
        log_columns = ['DTG','TGT_CLASS','TGT_MGRS','TGT_LATLON','TGT_ERROR_ACRES',
                       'EWT_1_MGRS','EWT_1_LATLON','EWT_1_LOB_DEGREES','EWT_1_PWR_REC_DbM','EWT_1_DIST2TGT_KM','EWT_1_MIN_DIST_KM','EWT_1_MAX_DIST_KM',
                       'EWT_2_MGRS','EWT_2_LATLON','EWT_2_LOB_DEGREES','EWT_2_PWR_REC_DbM','EWT_2_DIST2TGT_KM','EWT_2_MIN_DIST_KM','EWT_2_MAX_DIST_KM',
                       'EWT_3_MGRS','EWT_3_LATLON','EWT_3_LOB_DEGREES','EWT_3_PWR_REC_DbM','EWT_3_DIST2TGT_KM','EWT_3_MIN_DIST_KM','EWT_3_MAX_DIST_KM']
        num_ewt_datapoints = 7
        # assess if directory exists
        if not os.path.exists(self.log_directory):
            # create log directory
            os.makedirs(self.log_directory)
        # define log file name
        filename = f"EW-targeting-log-{str(datetime.datetime.today()).split()[0]}.csv"
        # if log file already exists
        if os.path.isfile(os.path.join(self.log_directory, filename)):
            # read current log file
            df_log = pd.read_csv(os.path.join(self.log_directory, filename))
            log_data = list(df_log.to_numpy())
        # if log file does not yet exist
        else:
            # create log file DataFrame
            log_data = []
        row_data = []
        dtg = generate_DTG()
        row_data.append(dtg)
        # if there is target data
        if  self.target_mgrs != None:
            row_data.append(self.target_class.split('(')[-1].split(')')[0])
            if row_data[-1] == '2 LOBs':
                row_data.append(self.target_mgrs)
                row_data.append(self.target_coord)
                row_data.append(self.target_error_val)
            else:
                row_data.append(self.target_mgrs)
                row_data.append(', '.join([str(x) for x in self.target_coord]))
                row_data.append(f'{self.target_error_val:,.2f}')
        # if there is not target data
        else:
            # end function w/o logging
            self.show_info("Insufficient input. No data logged.")
            return
        # if sensor 1 has data in the input fields
        if self.sensor1_mgrs_val != None:
            row_data.append(self.sensor1_mgrs_val)
            row_data.append(', '.join([str(x) for x in self.sensor1_coord]))
            row_data.append(self.sensor1_grid_azimuth_val)
            row_data.append(self.sensor1_power_received_dBm_val)
            row_data.append(f'{self.sensor1_distance_val/1000:,.2f}')
            row_data.append(f'{self.sensor1_min_distance_km:,.2f}')
            row_data.append(f'{self.sensor1_max_distance_km:,.2f}')
        # if sensor 1 has no data in the input fields
        else:
            # end function w/o logging
            self.show_info("Insufficient input. No data logged.")
            return
        # if sensor 2 has data in the input fields
        if self.sensor2_mgrs_val != None:
            row_data.append(self.sensor2_mgrs_val)
            row_data.append(', '.join([str(x) for x in self.sensor2_coord]))
            row_data.append(self.sensor2_grid_azimuth_val)
            row_data.append(self.sensor2_power_received_dBm_val)
            row_data.append(f'{self.sensor2_distance_val/1000:,.2f}')
            row_data.append(f'{self.sensor2_min_distance_km:,.2f}')
            row_data.append(f'{self.sensor2_max_distance_km:,.2f}')
        # if sensor 2 has no data in the input fields
        else:
            # add blank entries to sensor 2 data log
            for i in range(num_ewt_datapoints): row_data.append('')
        # if sensor 2 has data in the input fields
        if self.sensor3_mgrs_val != None:
            row_data.append(self.sensor3_mgrs_val)
            row_data.append(', '.join([str(x) for x in self.sensor3_coord]))
            row_data.append(self.sensor3_grid_azimuth_val)
            row_data.append(self.sensor3_power_received_dBm_val)
            row_data.append(f'{self.sensor3_distance_val/1000:,.2f}')
            row_data.append(f'{self.sensor3_min_distance_km:,.2f}')
            row_data.append(f'{self.sensor3_max_distance_km:,.2f}')
        # if sensor 3 has no data in the input fields
        else:
            # add blank entries to sensor 3 data log
            for i in range(num_ewt_datapoints): row_data.append('')
        log_data.append(row_data)
        df_log = pd.DataFrame(log_data,columns=log_columns).set_index(['DTG'],drop=True)
        # try to save the updated log file
        try:
            df_log.to_csv(os.path.join(self.log_directory, filename))
        # if file permissions prevent log file saving
        except PermissionError:
            # error message if file is currently open
            self.show_info("Log file currently open. Cannot log data!")
            return
        self.show_info("Data successfully logged!!!")    
    
    def add_marker_event(self, coords):
        from utilities import convert_coords_to_mgrs, format_readable_mgrs, get_distance_between_coords
        import numpy as np
        marker_text = f"{format_readable_mgrs(convert_coords_to_mgrs(list(coords)))}"
        print("Added marker:", marker_text)
        new_marker = self.map_widget.set_marker(coords[0], coords[1], 
                                                text=marker_text,
                                                image_zoom_visibility=(10, float("inf")),
                                                command=self.marker_click,
                                                data=marker_text)
        self.append_object(new_marker,"USER")
        if len(self.user_marker_list) > 1:
            sequencial_marker_list = self.user_marker_list[::-1]
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
        from utilities import check_mgrs_input, convert_mgrs_to_coords
        try:
            search_mgrs = self.search_mgrs.get().replace(" ","")
        except ValueError:
            self.show_info("Invalid MGRS input!")
            return
        if check_mgrs_input(search_mgrs):
            search_coord = convert_mgrs_to_coords(search_mgrs)
            self.map_widget.set_position(search_coord[0],search_coord[1])
            self.add_marker_event(search_coord)
        elif self.check_coord_input(search_mgrs):
            search_coord = self.correct_coord_input(search_mgrs)
            self.map_widget.set_position(search_coord[0],search_coord[1])
            self.add_marker_event(search_coord)
        else:
            self.show_info("Invalid MGRS input!")
            return

    def check_if_object_in_object_list(self,map_object,map_object_list):
        # got to assess marker details... not just the object
        map_object_data = map_object.data
        object_data_list = [mo.data for mo in map_object_list]
        if map_object_data in object_data_list:
            # print(f"denied marker to object list: {object_data_list}")
            # delete redudant map object
            map_object.delete()
            return True
        else:
            # print(f"allowed marker to object list: {object_data_list}")
            return False

    def append_object(self,map_object,map_object_list_name):
        # check if map object is a EWT marker
        if map_object_list_name.upper() == 'EWT':
            # check if EWT marker already exists in the EWT marker list
            if not self.check_if_object_in_object_list(map_object,self.ewt_marker_list):
                # append the EWT marker to the EWT marker list
                self.ewt_marker_list.append(map_object)
        # check if map object is a target marker
        elif map_object_list_name.upper() == 'TGT':
            # check if target marker already exists in the target marker list
            if not self.check_if_object_in_object_list(map_object,self.target_marker_list):
                # append the target marker to the target marker list
                self.target_marker_list.append(map_object)
        # check if map object is a USER marker
        if map_object_list_name.upper() == 'USER':
            # check if EWT marker already exists in the EWT marker list
            if not self.check_if_object_in_object_list(map_object,self.user_marker_list):
                # append the EWT marker to the EWT marker list
                self.user_marker_list.append(map_object)
        # check if map object is a LOB
        elif map_object_list_name.upper() == 'LOB':
            # check if LOB already exists in the LOB list
            if not self.check_if_object_in_object_list(map_object,self.lob_list):
                # append the LOB to the LOB list
                self.lob_list.append(map_object)
        # check if map object is a CUT
        elif map_object_list_name.upper() == 'CUT':
            # check if CUT already exists in the CUT list
            if not self.check_if_object_in_object_list(map_object,self.cut_list):
                # append the CUT to the CUT list
                self.cut_list.append(map_object)
        # check if map object is a FIX
        elif map_object_list_name.upper() == 'FIX':
            # check if FIX already exists in the FIX list
            if not self.check_if_object_in_object_list(map_object,self.fix_list):
                # append the FIX to the FIX list
                self.fix_list.append(map_object)     

    def clear_user_markers(self):
        for marker in self.user_marker_list:
            marker.delete()
        for path in self.path_list:
            path.delete()
        self.user_marker_list = []
        self.path_list = []

    def clear_target_overlays(self):
        for ewt_marker in self.ewt_marker_list:
            ewt_marker.delete()
        self.ewt_marker_list = []
        for target in self.target_marker_list:
            target.delete()
        self.target_marker_list = []
        for lob in self.lob_list:
            lob.delete()
        self.lob_list = []
        for cut in self.cut_list:
            cut.delete()
        self.cut_list = []
        for fix in self.fix_list:
            fix.delete()
        self.fix_list = []

    def clear_entries(self):
        from tkinter import END
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
        self.batch_download_center_mgrs.delete(0,END)
        self.batch_download_zoom_range.delete(0,END)
        self.batch_download_radius.delete(0,END)
        self.search_mgrs.delete(0,END)
        
    def batch_download(self):
        import re
        from utilities import check_mgrs_input, convert_coords_to_mgrs, convert_mgrs_to_coords, get_coord_box
        def append_cmd_to_queue(cmd,file_path=os.path.dirname(os.path.abspath(__file__))+"\\queue_files\\batch_tile_queue.csv"):
            import csv
            if cmd == "" or cmd == []: return
            row_to_append = [cmd]
            with open(file_path, mode='a', newline='') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow(row_to_append)
        # read center mgrs input
        center_mgrs = self.batch_download_center_mgrs.get().replace(" ","")
        # check if NOT a valid mgrs
        if not check_mgrs_input(center_mgrs):
            # check if a valid coordinate
            center_coord = self.correct_coord_input(center_mgrs)
            if not self.check_coord_input(center_coord):
                # display input error warning
                self.show_info("MGRS / coordiante input is invalid",box_title="Input Error",icon='warning')
                # end function
                return
            # convert coordinate to mgrs string
            center_mgrs = convert_coords_to_mgrs(center_coord)
        # if a valid mgrs
        else:
            # convert mgrs string to coordinate list
            center_coord = convert_mgrs_to_coords(center_mgrs)
        # read zoom string input
        zoom_string = self.batch_download_zoom_range.get()
        # check if zoom string is valid
        if zoom_string == '' or len(zoom_string) > 5 or re.search(r'[a-zA-Z]+', zoom_string):
            # display error upon invalid zoom string
            self.show_info("Zoom range is invalid",box_title="Input Error",icon='warning')
            # end function
            return
        # define zoom range
        min_zoom = min([int(x.strip()) for x in zoom_string.split('-')])
        max_zoom = max([int(x.strip()) for x in zoom_string.split('-')])
        if min_zoom < 0: min_zoom = 0
        if max_zoom > App.MAX_ZOOM: max_zoom = App.MAX_ZOOM
        # read radius input and determine if valid
        try:
            radius_m = int(self.batch_download_radius.get())
            x_dist_m = y_dist_m = radius_m
        # if not valid
        except ValueError:
            # display error upon invalid radius input
            self.show_info("Radius input is invalid",box_title="Input Error",icon='warning')
            # end function
            return
        # identify tile download filepath
        get_tiles_file = os.path.join(self.src_directory, "get_tiles.py")
        # identify remote tile API
        tile_url = '"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png"'
        # identify number of threads dedicated to download
        parallel_threads = 4
        # generate coordinate bbox from input
        coord_bbox = get_coord_box(center_coord,x_dist_m,y_dist_m)
        # string operation on coordinate bbox
        coord_bbox = coord_bbox.replace(","," ").split()
        # generate CLI command
        cmd = f'python "{get_tiles_file}" "{tile_url}" "{self.tile_directory}" --extent {coord_bbox[0]} {coord_bbox[1]} {coord_bbox[2]} {coord_bbox[3]} --minzoom {min_zoom} --maxzoom {max_zoom} --parallel {parallel_threads}'
        '''
        
        Alter queue append to send args, not entire command
        Add a main function to estimate run time and a main fuction to give status on current batch download queue
        gui function to do a popup on the batch download details and a verify 
        
        '''
        append_cmd_to_queue(cmd)
        # # generate command list
        # cmd_list = ['python',f'"{get_tiles_file}"',f'"{tile_url}"',f'"{self.tile_directory}"','--extent','{coord_bbox[0]}',
        #             '{coord_bbox[1]}','{coord_bbox[2]}','{coord_bbox[3]}','--minzoom','{min_zoom}','--maxzoom','{max_zoom}',
        #             '--parallel','{parallel_threads}']
        # def download_func(cmd_list):
        #     # subprocess.Popen(cmd_list,start_new_session=True)
        #     subprocess.run(cmd, shell=True, start_new_session=True)
        # # run tile download command
        # # subprocess.run(cmd, shell=True, start_new_session=True)
        # from multiprocessing import Process
        # proc_batch_download = Process(target=download_func,args=(cmd_list))
        # # procs.append(proc_batch_download)
        # proc_batch_download.start()
        
    def marker_click(self,marker):
        if "EWT" in marker.data:
            self.show_info(msg=marker.data,box_title='EWT Data',icon='info')
        elif "TGT" in marker.data:
            self.show_info(msg=marker.data,box_title='TGT Data',icon='info')
        else:
            self.show_info(msg=marker.data,box_title='EWT Data',icon='info')
        
    def polygon_click(self,polygon):
        self.show_info(msg=polygon.data,box_title='Target Data',icon='info')

    def show_info(self,msg,box_title='Warning Message',icon='warning'):
        from CTkMessagebox import CTkMessagebox
        CTkMessagebox(title=box_title, message=msg, icon=icon,option_1='Ackowledged')

    def input_error(self,category,msg,single_lob_option=False,cut_option=False):
        from CTkMessagebox import CTkMessagebox
        if not single_lob_option and not cut_option:
            msgBox = CTkMessagebox(title=f"Error in {category}", message=msg, icon='warning',options=['Re-input','Use Default'])
        elif single_lob_option and not cut_option:
            msgBox = CTkMessagebox(title=f"Error in {category}", message=msg, icon='warning',options=['Re-input','LOB','Use Default'])            
        elif cut_option:
            msgBox = CTkMessagebox(title=f"Error in {category}", message=msg, icon='warning',options=['Re-input','LOB/CUT','Use Default'])
        response = msgBox.get()
        if response == 'Re-input':
            return False
        elif response == 'Use Default':
            return True
        elif response == 'LOB':
            return 'SL'
        elif response == 'LOB/CUT':
            return 'LOB/CUT'

    def change_map(self, new_map: str):
        map_server_url = f'http://localhost:{App.MAP_SERVER_PORT}'
        if new_map == 'Local Map Server':
            self.map_widget.set_tile_server(map_server_url+"/{z}/{x}/{y}.png", max_zoom=App.MAX_ZOOM)
        elif new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google Street":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=App.MAX_ZOOM)
        elif new_map == "Google Satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=App.MAX_ZOOM)

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
        if sensor_option == 'BEAST+':
            self.sensor1_receiver_gain_dBi = 0
            self.sensor2_receiver_gain_dBi = 0
            self.sensor1_error = 4
            self.sensor2_error = 4
        elif sensor_option == 'VROD/VMAX':
            self.sensor1_receiver_gain_dBi = 0
            self.sensor2_receiver_gain_dBi = 0
            self.sensor1_error = 6
            self.sensor2_error = 6

    def on_closing(self, event=0):
        import sys
        # for proc in procs:
        #     proc.join()
        self.destroy()
        sys.exit()
        

    def start(self):
        self.mainloop()

def main():
    app = App()
    app.start()

if __name__ == "__main__":
    from multiprocessing import Process
    # global procs; procs = []
    proc_app = Process(target=main)
    # procs.append(proc_app)
    proc_app.start()

"""
DEV NOTES

--- MVP Reqs:
    - give estimate warning prior to executing batch download
    - csv log error if file is open (bypass by creating alternate file?)
    - if cut exists with one random lob, still plot random lob
    - add enter command to user input
    - assign LOB targets to EWT in info description
    - allow user to input LOB 3-liner for EWT 2 or 3 if EWT 1 is empty
    - change log successful display to info, not warning
    - single lob not being attributed to ewt 1
    - lob area tgt data formatting, needs improvement
    - distance format function that changes km to m based on number (already exists in dist to ewt)
    - better formating in log file
    
- earth curvature limitation identified on elevation map
    - circle around EWTs with radius being LOS?
- provide option to input coordinates instead of MGRS
- move batch download function into utilities file
- add config file for hard-coded data
- restart app button

"""
