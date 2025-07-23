#!/usr/bin/env python

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from utilities import read_json
import customtkinter
import logging
from logger import LoggerManager
from _tkinter import TclError

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
    # read the app config file
    conf = read_json(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config_files","conf.json"))
    # present IP address for the map server
    MAP_SERVER_IP = conf["MAP_SERVER_IP"]
    # preset local port that is hosting the map server
    MAP_SERVER_PORT = conf["MAP_SERVER_PORT"]
    # preset maximum map zoom level
    MAX_ZOOM = conf["MAX_ZOOM"]
    # preset default values
    DEFAULT_VALUES = {
        "Sensor 1 MGRS": conf["DEFAULT_SENSOR_1_MGRS"],
        "Sensor 1 PWR Received": conf["DEFAULT_SENSOR_1_PWR_RECEIVED"],
        "Sensor 1 LOB": conf["DEFAULT_SENSOR_1_LOB"],
        "Sensor 1 Height (M)": conf["DEFAULT_SENSOR_1_HEIGHT_M"],
        "Sensor 2 MGRS": conf["DEFAULT_SENSOR_2_MGRS"],
        "Sensor 2 PWR Received": conf["DEFAULT_SENSOR_2_PWR_RECEIVED"],
        "Sensor 2 LOB": conf["DEFAULT_SENSOR_2_LOB"],
        "Sensor 2 Height (M)": conf["DEFAULT_SENSOR_2_HEIGHT_M"],
        "Sensor 3 MGRS": conf["DEFAULT_SENSOR_3_MGRS"],
        "Sensor 3 PWR Received": conf["DEFAULT_SENSOR_3_PWR_RECEIVED"],
        "Sensor 3 LOB": conf["DEFAULT_SENSOR_3_LOB"],
        "Sensor 3 Height (M)": conf["DEFAULT_SENSOR_3_HEIGHT_M"],
        "Frequency":conf["DEFAULT_FREQUENCY_MHZ"],
        "Transmitter Gain (dBi)":conf["DEFAULT_TX_GAIN_dBi"],
        "Transmitter Height (M)":conf["DEFAULT_TX_HEIGHT_M"],
        "Min ERP":conf["DEFAULT_MIN_ERP_W"],
        "Max ERP":conf["DEFAULT_MAX_ERP_W"],
        "Path-Loss Coefficient":conf["DEFAULT_PATH-LOSS_COEFFICIENT"],
        "Path-Loss Coefficient Description":conf["DEFAULT_PATH-LOSS_COEFFICIENT_DESCRIPTION"],
        "Temperature (F)":conf["DEFAULT_TEMP_F"],
        "Border Width":conf["DEFAULT_BORDER_WIDTH"],
        "LOB Fill Color":conf["DEFAULT_LOB_FILL_COLOR"],
        "LOB Center Line Color":conf["DEFAULT_LOB_CENTER_LINE_COLOR"],
        "LOB Area Outline Color":conf["DEFAULT_LOB_AREA_OUTLINE_COLOR"],
        "CUT Area Outline Color":conf["DEFAULT_CUT_AREA_OUTLINE_COLOR"],
        "FIX Area Outline Color":conf["DEFAULT_FIX_AREA_OUTLINE_COLOR"],
        "Initial Latitude":conf["DEFAULT_INITIAL_LATITUDE"],
        "Initial Longitude":conf["DEFAULT_INITIAL_LONGITUDE"],
        "Map Server File Path":conf["DEFAULT_MAP_SERVER_PATH"],
        "POI Marker Filename":conf["FILENAME_POI_MARKERS"],
        "Tactical Graphic Marker Filename":conf["FILENAME_TACTICAL_GRAPHIC_MARKERS"],
        "EWT Marker Filename":conf["FILENAME_EWT_MARKERS"],
        "Initial Map Zoom":conf["INITIAL_ZOOM"]
    }
    PATH_LOSS_DICT = {
        'Free Space':2,
        'No Foliage':3,
        'Light Foliage':3.5,
        'Moderate Foliage':4,
        'Dense Foliage':4.5,
        'Jungle Foliage':5        
    }
    # read the target preset config file
    conf_target_presets = read_json(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config_files","target_presets.json"))

    def __init__(self, *args, **kwargs):
        """
        Defines application initialization attributes
        """
        super().__init__(*args, **kwargs)
        self.logger_gui = LoggerManager.get_logger(
                    name="gui",
                    category="app",
                    level=logging.INFO
                )
        self.logger_gui.info("Application initialized")
        self.logger_targeting = LoggerManager.get_logger(
                    name="targeting",
                    category="app",
                    level=logging.INFO
                )
        self.logger_positioning = LoggerManager.get_logger(
                    name="eud_position",
                    category="app",
                    level=logging.INFO
                )
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
        self.icon_directory = os.path.join(os.path.dirname(self.src_directory), App.conf["DIR_RELATIVE_ICONS"])
        # define map tile directory
        self.tile_directory = os.path.join(os.path.dirname(self.src_directory), App.conf["DIR_RELATIVE_MAP_TILES"])
        # define base log directory
        self.log_directory = os.path.join(os.path.dirname(self.src_directory), App.conf["DIR_RELATIVE_LOGS"])
        # define targeting log directory
        self.log_targeting_directory = os.path.join(os.path.dirname(self.src_directory), App.conf["DIR_RELATIVE_LOGS_TARGETING"])
        # define EUD log file directory
        self.log_eud_position_directory = os.path.join(os.path.dirname(self.src_directory), App.conf["DIR_RELATIVE_LOGS_EUD_POSITION"])
        # define target image icon
        self.target_image_LOB = ImageTk.PhotoImage(Image.open(os.path.join(self.icon_directory, "target_LOB.png")).resize((40, 40)))
        # define target image icon
        self.target_image_CUT = ImageTk.PhotoImage(Image.open(os.path.join(self.icon_directory, "target_CUT.png")).resize((40, 40)))
        # define target image icon
        self.target_image_FIX = ImageTk.PhotoImage(Image.open(os.path.join(self.icon_directory, "target_FIX.png")).resize((40, 40)))
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
        # define initial POI marker list
        self.POI_marker_list = []
        # define objective list
        self.obj_list = []
        # define NAI list
        self.nai_list = []
        # define initial EDU marker list
        self.eud_marker_list = []
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
        # define default target class
        self.target_class = ''
        # define default target value (used as conditional in logging method)
        self.target_mgrs = None
        # define default target emitter
        self.bypass_input_errors = False
        self.bypass_elevation_plot_prompt =  False

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

        # ============ GUI Input/Ouput Frame ============
        
        # define frame header attributes
        self.label_header = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="EW TARGETING DATA", 
            text_color='yellow')
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
            text="EWT 1 Location (MGRS):", 
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
        # bind mgrs entry "Right Click" to copy (if selection exists) / paste function (otherwise)
        self.sensor1_mgrs.bind("<Button-3>", lambda cTk_obj: self._paste_from_clipboard(self.sensor1_mgrs))
        # bind EWT function to RETURN keystroke in Sensor 1 MGRS input field
        self.sensor1_mgrs.bind("<Return>", self.ewt_input_processor)
        # define sensor 1 LOB label
        self.label_sensor1_lob = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="EWT 1 LOB (Degrees):", 
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
        # bind LOB entry "Right Click" to copy (if selection exists) / paste function (otherwise)
        self.sensor1_lob.bind("<Button-3>", lambda cTk_obj: self._paste_from_clipboard(self.sensor1_lob))
        # bind EWT function to RETURN keystroke in Sensor 1 LOB input field
        self.sensor1_lob.bind("<Return>", self.ewt_input_processor)
        # define sensor 1 received power label attributes
        self.label_sensor1_Rpwr = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="EWT 1 PWR Rec. (dBm):", 
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
        # bind power entry "Right Click" to copy (if selection exists) / paste function (otherwise)
        self.sensor1_Rpwr.bind("<Button-3>", lambda cTk_obj: self._paste_from_clipboard(self.sensor1_Rpwr))
        # bind EWT function to RETURN keystroke in Sensor 1 Rpwr input field
        self.sensor1_Rpwr.bind("<Return>", self.ewt_input_processor)
        # define sensor 2 mgrs label attributes
        self.label_sensor2_mgrs = customtkinter.CTkLabel(
            master = self.frame_left, 
            text="EWT 2 Location (MGRS):", 
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
        # bind mgrs entry "Right Click" to copy (if selection exists) / paste function (otherwise)
        self.sensor2_mgrs.bind("<Button-3>", lambda cTk_obj: self._paste_from_clipboard(self.sensor2_mgrs))
        # bind EWT function to RETURN keystroke in Sensor 2 MGRS input field
        self.sensor2_mgrs.bind("<Return>", self.ewt_input_processor)
        # define sensor 2 LOB label attributes
        self.label_sensor2_lob = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="EWT 2 LOB (Degrees):", 
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
        # bind LOB entry "Right Click" to copy (if selection exists) / paste function (otherwise)
        self.sensor2_lob.bind("<Button-3>", lambda cTk_obj: self._paste_from_clipboard(self.sensor2_lob))
        # bind EWT function to RETURN keystroke in Sensor 2 LOB input field
        self.sensor2_lob.bind("<Return>", self.ewt_input_processor)
        # define sensor 2 received power attributes
        self.label_sensor2_Rpwr = customtkinter.CTkLabel(
            self.frame_left, 
            text="EWT 2 PWR Rec. (dBm):", 
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
        # bind Rpwr entry "Right Click" to copy (if selection exists) / paste function (otherwise)
        self.sensor2_Rpwr.bind("<Button-3>", lambda cTk_obj: self._paste_from_clipboard(self.sensor2_Rpwr))
        # bind EWT function to RETURN keystroke in Sensor 2 Rpwr input field
        self.sensor2_Rpwr.bind("<Return>", self.ewt_input_processor)
        # define sensor 3 mgrs label attributes
        self.label_sensor3_mgrs = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="EWT 3 Location (MGRS):", 
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
        # bind mgrs entry "Right Click" to copy (if selection exists) / paste function (otherwise)
        self.sensor3_mgrs.bind("<Button-3>", lambda cTk_obj: self._paste_from_clipboard(self.sensor3_mgrs))
        # bind EWT function to RETURN keystroke in Sensor 3 MGRS input field
        self.sensor3_mgrs.bind("<Return>", self.ewt_input_processor)
        # define sensor 3 LOB label attributes
        self.label_sensor3_lob = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="EWT 3 LOB (Degrees):", 
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
        # bind mgrs entry "Right Click" to copy (if selection exists) / paste function (otherwise)
        self.sensor3_lob.bind("<Button-3>", lambda cTk_obj: self._paste_from_clipboard(self.sensor3_lob))
        # bind EWT function to RETURN keystroke in Sensor 3 LOB input field
        self.sensor3_lob.bind("<Return>", self.ewt_input_processor)
        # define sensor 3 received power label attributes
        self.label_sensor3_Rpwr = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="EWT 3 PWR Rec. (dBm):", 
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
        # bind mgrs entry "Right Click" to copy (if selection exists) / paste function (otherwise)
        self.sensor3_Rpwr.bind("<Button-3>", lambda cTk_obj: self._paste_from_clipboard(self.sensor3_Rpwr))
        # bind EWT function to RETURN keystroke in Sensor 3 Rpwr input field
        self.sensor3_Rpwr.bind("<Return>", self.ewt_input_processor)
        # define target frequency label attributes
        self.label_frequency = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="Frequency (Mhz):",
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
        # bind freq entry "Right Click" to copy (if selection exists) / paste function (otherwise)
        self.frequency.bind("<Button-3>", lambda cTk_obj: self._paste_from_clipboard(self.frequency))
        # bind EWT function to RETURN keystroke in Frequency input field
        self.frequency.bind("<Return>", self.ewt_input_processor)
        # define min ERP label attributes
        # define preset target emitter label attributes
        self.label_target_emitter_preset = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="Target Emitter:", 
            text_color='white')
        # assign preset target emitter label grid position
        self.label_target_emitter_preset.grid(
            row=self.frequency.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,5), 
            pady=(0,0),
            sticky='w')
        # define path-loss coefficient option attributes
        self.option_target_emitter_preset = customtkinter.CTkOptionMenu(
            master=self.frame_left, 
            values=["Custom"]+list(App.conf_target_presets.keys()),
            fg_color='brown',
            button_color='brown',
            command=self.change_preset_target_emitter)
        # assign path-loss coefficient option grid position
        self.option_target_emitter_preset.grid(
            row=self.frequency.grid_info()["row"]+1,
            rowspan=1, 
            column=1, 
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        self.label_min_ERP = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="Minimum ERP (Watts):", 
            text_color='white')
        # assign min ERP label grid position
        self.label_min_ERP.grid(
            row=self.option_target_emitter_preset.grid_info()["row"]+1,
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
            row=self.option_target_emitter_preset.grid_info()["row"]+1, 
            rowspan=1,
            column=1, 
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # bind ERP entry "Right Click" to copy (if selection exists) / paste function (otherwise)
        self.min_ERP.bind("<Button-3>", lambda cTk_obj: self._paste_from_clipboard(self.min_ERP))
        # bind EWT function to RETURN keystroke in Min ERP input field
        self.min_ERP.bind("<Return>", self.ewt_input_processor)
        # define max ERP label attributes
        self.label_max_ERP = customtkinter.CTkLabel(
            master=self.frame_left, 
            text="Maximum ERP (Watts):", 
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
        # bind ERP entry "Right Click" to copy (if selection exists) / paste function (otherwise)
        self.max_ERP.bind("<Button-3>", lambda cTk_obj: self._paste_from_clipboard(self.max_ERP))
        # bind EWT function to RETURN keystroke in Max ERP input field
        self.max_ERP.bind("<Return>", self.ewt_input_processor)
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
            values=["Free Space","No Foliage","Light Foliage","Moderate Foliage","Dense Foliage","Jungle Foliage"],
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
        # bind TGT grid label "Right Click" to copy
        self.target_grid.bind("<Button-3>", lambda cTk_obj: self.copy_selection(self.target_grid))
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
            text="Clear User Inputs",
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
            text="Calcuate",
            fg_color='blue',
            command = self.ewt_input_processor)
        # assign calculate button grid position
        self.button_calculate.grid(
            row=self.target_error.grid_info()["row"]+1,
            rowspan=1,
            column=1,
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define TBD button attributes
        self.button_reload_last_log = customtkinter.CTkButton(
            master=self.frame_left, 
            text="Reload Last Log",
            fg_color='brown',
            command=self.reload_last_log)
        # assign TBD button grid position
        self.button_reload_last_log.grid(
            row=self.button_calculate.grid_info()["row"]+1,
            rowspan=1,
            column=0,
            columnspan=1, 
            padx=(0,0), 
            pady=(0,0))
        # define log entries button 
        self.button_log_data = customtkinter.CTkButton(
            master=self.frame_left, 
            text="Log Target Data",
            fg_color='green',
            command = self.log_target_data)
        # assign log entries button grid position
        self.button_log_data.grid(
            row=self.button_clear_entries.grid_info()["row"]+1,
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
        self.frame_right.grid_columnconfigure(0, weight=0)
        # configure second column with high weight
        self.frame_right.grid_columnconfigure(1, weight=1)
        # configure third column with low weight
        self.frame_right.grid_columnconfigure(2, weight=0)
        # configure forth column with low weight
        self.frame_right.grid_columnconfigure(3, weight=0)
        # configure fifth column with low weight
        self.frame_right.grid_columnconfigure(4, weight=0)
        # configure sixth column with low weight
        self.frame_right.grid_columnconfigure(5, weight=0)
        # define map widget attributes
        self.map_widget = TkinterMapView(
            master=self.frame_right, 
            corner_radius=0)
        # assign map widget grid position
        self.map_widget.grid(
            row=1, 
            rowspan=2, 
            column=0, 
            columnspan=6,
            padx=(0, 0), 
            pady=(0, 0),
            sticky="nswe")
        # set map widget default tile server
        map_server_url = f'http://{App.MAP_SERVER_IP}:{App.MAP_SERVER_PORT}'
        self.map_widget.set_tile_server(
            tile_server=map_server_url+App.DEFAULT_VALUES["Map Server File Path"],
            max_zoom=App.MAX_ZOOM)
        # set initial zoom level for map tile server
        self.map_widget.set_zoom(14)
        # define plot EUD button attributes
        self.button_plot_eud_location = customtkinter.CTkButton(
            master=self.frame_right,
            text="Plot EUD Position",
            fg_color="brown",
            text_color="white",
            command=self.plot_EUD_position)
        # assign clear markers button grid position
        self.button_plot_eud_location.grid(
            row=0, 
            rowspan=1,
            column=0, 
            columnspan=1, 
            padx=(12, 0), 
            pady=12,
            sticky="ew")
        # define mgrs entry form attributes
        self.search_mgrs = customtkinter.CTkEntry(
            master=self.frame_right,
            placeholder_text="Insert MGRS Grid")
        # assign mgrs entry form grid position
        self.search_mgrs.grid(
            row=0,
            column=1,
            columnspan=2,
            padx=(12, 0), 
            pady=12,
            sticky="ew")
        # bind mgrs entry RETURN keystroke to search function
        self.search_mgrs.bind("<Return>", self.search_event)
        # bind mgrs entry "Right Click" to copy (if selection exists) / paste function (otherwise)
        self.search_mgrs.bind("<Button-3>", lambda cTk_obj: self._paste_from_clipboard(self.search_mgrs))
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
            column=3, 
            columnspan=1, 
            padx=(12, 0), 
            pady=12,
            sticky="ew")
        # define clear option dropdown attributes
        self.clear_option_dropdown = customtkinter.CTkOptionMenu(
            master=self.frame_right, 
            values=["Clear POIs",
                    "Clear Graphics", 
                    "Clear Target Overlays", 
                    "Clear EWTs", 
                    "Clear Measurements"
                    ],
            fg_color="red",
            text_color="white",
            command=self.clear_options)
        self.clear_option_dropdown.grid(
            row=0,
            rowspan=1,
            column=4, 
            columnspan=1, 
            padx=(12,0), 
            pady=12,
            sticky="w")

        # define map option dropdown attributes
        self.map_option_menu = customtkinter.CTkOptionMenu(
            master=self.frame_right, 
            values=["Local Terrain Map", 
                    "Local Satellite Map", 
                    "OpenStreetMap", 
                    "Google Street", 
                    "Google Satellite"
                    ],
            fg_color="green",
            text_color="white",
            command=self.change_map)
        # assign map option dropdown grid position
        self.map_option_menu.grid(
            row=0,
            rowspan=1,
            column=5, 
            columnspan=1, 
            padx=(12, 0), 
            pady=12,
            sticky="w")
        # set initial location
        self.map_widget.set_position(App.DEFAULT_VALUES["Initial Latitude"],App.DEFAULT_VALUES["Initial Longitude"])
        # set clear option
        self.clear_option_dropdown.set("Map Clear Options")
        # set map widget default server
        self.map_option_menu.set("Local Terrain Map")
        # set default path-loss coefficient
        self.option_path_loss_coeff.set('Dense Foliage')
        # set default sensor
        self.option_sensor.set('BEAST+')
        # define right-click attributes
        self.map_widget.add_right_click_menu_command(
            label="Add Point of Interest (POI)",
            command=self.add_marker_event,
            pass_coords=True)
        self.map_widget.add_right_click_menu_command(
            label="Copy MGRS Gid",
            command=self.copy_mgrs_grid,
            pass_coords=True)
        # self.map_widget.add_right_click_menu_command(
        #     label="Plot OBJ",
        #     command=self.plot_OBJ,
        #     pass_coords=True)
        # self.map_widget.add_right_click_menu_command(
        #     label="Plot NAI",
        #     command=self.plot_NAI,
        #     pass_coords=True)
        self.map_widget.add_right_click_menu_command(
            label="Plot EWT",
            command=self.right_click_plot_EWT,
            pass_coords=True)
        self.map_widget.add_right_click_menu_command(
            label="Decrease Brightness (20%)",
            command=self.increment_brightness_down)
        self.map_widget.add_right_click_menu_command(
            label="Increase Brightness (20%)",
            command=self.increment_brightness_up)
        self.plot_current_markers()

    def plot_current_markers(self) -> None:
        from tkinter import END
        from coords import convert_coords_to_mgrs, format_readable_mgrs
        from utilities import read_csv
        filepath_POI_markers = os.path.join(self.log_directory, App.DEFAULT_VALUES["POI Marker Filename"])
        initial_coord = []
        try:
            marker_data_list = read_csv(filepath_POI_markers)
            marker_data_list = sorted(marker_data_list,key=lambda x: int(x["MARKER_NUM"]))
            for marker_data in marker_data_list:
                marker_coord = marker_data['LOC_LATLON']
                marker_coord = [float(x) for x in marker_coord.split(', ')]
                self.add_marker_event(marker_coord,True,True)
                self.logger_gui.info(f"Loaded POI Marker No. {marker_data['MARKER_NUM']} at {format_readable_mgrs(convert_coords_to_mgrs(marker_coord))}")
                initial_coord = marker_coord
        except FileNotFoundError:
            pass
        tactical_marker_filepath = os.path.join(self.log_directory, App.DEFAULT_VALUES["Tactical Graphic Marker Filename"])
        try:
            marker_data_list = read_csv(tactical_marker_filepath)
            for marker_data in marker_data_list:
                marker_coord = marker_data['LOC_LATLON']
                marker_coord = [float(x) for x in marker_coord.split(', ')]
                if marker_data['MARKER_TYPE'] == 'OBJ':
                    self.plot_OBJ(marker_coord,True)
                    self.logger_gui.info(f"Loaded OBJ Marker at {format_readable_mgrs(convert_coords_to_mgrs(marker_coord))}")
                elif marker_data['MARKER_TYPE'] == 'NAI':
                    self.plot_NAI(marker_coord,True)
                    self.logger_gui.info(f"Loaded NAI Marker at {format_readable_mgrs(convert_coords_to_mgrs(marker_coord))}")
                initial_coord = marker_coord
        except FileNotFoundError:
            pass
        ewt_marker_filepath = os.path.join(self.log_directory, App.DEFAULT_VALUES["EWT Marker Filename"])
        try:
            marker_data_list = read_csv(ewt_marker_filepath)
            for marker_data in marker_data_list:
                ewt_num = str(marker_data['MARKER_NUM'])
                marker_coord = marker_data['LOC_LATLON']
                marker_coord = [float(x) for x in marker_coord.split(', ')]
                marker_mgrs = convert_coords_to_mgrs(marker_coord)
                if ewt_num == '1':
                    self.sensor1_mgrs.delete(0,END)
                    self.sensor1_mgrs.insert(0,marker_mgrs)
                elif ewt_num == '2':
                    self.sensor2_mgrs.delete(0,END)
                    self.sensor2_mgrs.insert(0,marker_mgrs)
                elif ewt_num == '3':
                    self.sensor3_mgrs.delete(0,END)
                    self.sensor3_mgrs.insert(0,marker_mgrs)
                else:
                    self.logger_gui.warning(f"Invalid EWT number {ewt_num} in marker file.")
                    continue
                self.plot_EWT(marker_coord,ewt_num,True)
                self.logger_gui.info(f"Loaded EWT {ewt_num} marker at {format_readable_mgrs(marker_mgrs)}")
                initial_coord = marker_coord
        except FileNotFoundError:
            pass
        if initial_coord != []:
            self.map_widget.set_position(initial_coord[0],initial_coord[1])
            self.map_widget.set_zoom(App.DEFAULT_VALUES["Initial Map Zoom"])

    def read_ewt_input_fields(self):
        """
        Function to read and ajudicate EWT input
        """
        from tkinter import END
        from coords import check_mgrs_input, correct_mgrs_input
        # resets boolean values to FALSE, allowing EWT input
        single_lob_bool = False; cut_bool = False; bypass_ewt1_bool = False; bypass_ewt2_bool = False; bypass_ewt3_bool = False
        # reset sensor mgrs/coord reading to None, conditional in log method
        self.sensor1_mgrs_val = None; self.sensor2_mgrs_val = None; self.sensor3_mgrs_val = None
        self.sensor1_coord = None; self.sensor2_coord = None; self.sensor3_coord = None
        self.sensor1_max_distance_m = None; self.sensor2_max_distance_m = None ; self.sensor3_max_distance_m = None
        self.frequency_MHz_val = None; self.min_wattage_val = None; self.max_wattage_val = None
        # set values without option for user input 
        self.sensor1_receiver_height_m_val = App.DEFAULT_VALUES["Sensor 1 Height (M)"]
        self.sensor2_receiver_height_m_val = App.DEFAULT_VALUES["Sensor 2 Height (M)"]
        self.sensor3_receiver_height_m_val = App.DEFAULT_VALUES["Sensor 3 Height (M)"]
        self.transmitter_gain_dBi_val = App.DEFAULT_VALUES["Transmitter Gain (dBi)"]
        self.transmitter_height_m_val = App.DEFAULT_VALUES["Transmitter Height (M)"]
        self.temp_f_val = App.DEFAULT_VALUES["Temperature (F)"]
        # try to read sensor 1 mgrs value
        try:
            # get input from sensor1_mgrs input field
            self.sensor1_mgrs_val = str(self.sensor1_mgrs.get()).strip().replace(" ","")
            # assess whether the input MGRS value is valid
            if check_mgrs_input(self.sensor1_mgrs_val):
                # if MGRS value is valid, pass on to next portion of function code
                pass
            else:
                # if MGRS is invalid, give user the option to re-input, bypass EWT, or use default value
                if not self.bypass_input_errors: 
                    choice = self._input_error(category='Sensor 1 Grid',msg=f'Invalid Input {self.sensor1_mgrs_val}',single_lob_option=False,cut_option=False,ewt_bypass_option=True,EWT_num='1')
                else:
                    choice = "Bypass"
                # end function if user x's out of the pop-up window
                if choice is None: return
                # assess if user wishes to use the default value or end function
                elif choice == 'Default':
                    # clear the previous sensor 1 MGRS input
                    self.sensor1_mgrs.delete(0,END)
                    # insert the default sensor 1 MGRS value
                    self.sensor1_mgrs.insert(0,App.DEFAULT_VALUES['Sensor 1 MGRS'])
                    # set local Sensor 1 MGRS value to default value
                    self.sensor1_mgrs_val = App.DEFAULT_VALUES['Sensor 1 MGRS']
                elif choice == 'Bypass':
                    bypass_ewt1_bool = True
                    # set all local Sensor 1 values to None
                    self.sensor1_mgrs_val = None
                    self.sensor1_grid_azimuth_val = None
                    self.sensor1_power_received_dBm_val = None
                    # clear all Sensor 1 input fields
                    self.sensor1_mgrs.delete(0,END)
                    self.sensor1_lob.delete(0,END)
                    self.sensor1_Rpwr.delete(0,END)                
                # if user chooses to re-input the sensor 1 MGRS value
                elif choice == 'Re-input':
                    # end function
                    return
            if not bypass_ewt1_bool:
                # clear the previous sensor 1 MGRS input
                self.sensor1_mgrs.delete(0,END)
                # insert the default sensor 1 MGRS value
                self.sensor1_mgrs.insert(0,correct_mgrs_input(self.sensor1_mgrs_val))
        # exception handling for ValueError
        except ValueError:
            # if value error occurs, set Sensor 1 MGRS value to None
            if self.sensor1_mgrs_val in [None,""] or not check_mgrs_input(self.sensor1_mgrs_val):
                self.sensor1_mgrs_val = None
                self.sensor1_mgrs.delete(0,END)
        if not bypass_ewt1_bool:
            # try to read sensor 1 LOB value
            try:
                # get input from Sensor 1 LOB field
                self.sensor1_grid_azimuth_val = int(self.sensor1_lob.get())
                # assess feasiblity of Sensor 1 LOB input value
                if self.sensor1_grid_azimuth_val < 0 or self.sensor1_grid_azimuth_val > 360:
                    raise ValueError
            # exception handling for ValueError
            except ValueError:
                # give user option to re-input value, bypass EWT, or use the default Sensor 1 LOB value
                if not self.bypass_input_errors: 
                    choice = self._input_error(category='Sensor 1 Grid Azimuth',msg='Invalid Input',single_lob_option=False,cut_option=False,ewt_bypass_option=True,EWT_num='1')
                else:
                    choice = "Bypass"
                # end function if user x's out of the pop-up window
                if choice is None: return
                # if user chooses to use the default Sensor 1 LOB value
                if choice == "Default":
                    # clear Sensor 1 LOB input field
                    self.sensor1_lob.delete(0,END)
                    # insert default Sensor 1 LOB value
                    self.sensor1_lob.insert(0,App.DEFAULT_VALUES['Sensor 1 LOB'])
                    # set local Sensor 1 LOB value to default value
                    self.sensor1_grid_azimuth_val = App.DEFAULT_VALUES['Sensor 1 LOB']
                elif choice == 'Bypass':
                    bypass_ewt1_bool = True
                    # set all local Sensor 1 values to None
                    if self.sensor1_mgrs_val in [None,""] or not check_mgrs_input(self.sensor1_mgrs_val):
                        self.sensor1_mgrs_val = None
                        self.sensor1_mgrs.delete(0,END)
                    self.sensor1_grid_azimuth_val = None
                    self.sensor1_power_received_dBm_val = None
                    # clear all Sensor 1 input fields
                    self.sensor1_lob.delete(0,END)
                    self.sensor1_Rpwr.delete(0,END)
                # if user choose to re-input the Sensor 1 LOB value
                elif choice == 'Re-input':
                    # end function
                    return
        if not bypass_ewt1_bool:
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
                # give user option to re-input value, bypass EWT, or use the default Sensor 1 PWR received value
                if not self.bypass_input_errors:
                    choice = self._input_error(category='Sensor 1 Power Received',msg='Invalid Input',single_lob_option=False,cut_option=False,ewt_bypass_option=True,EWT_num='1')
                else:
                    choice = "Bypass"
                # end function if user x's out of the pop-up window
                if choice is None: return
                # if user chooses to use the default Sensor 1 PWR Received value
                if choice == "Default":
                    # clear the Sensor 1 PWR Received value
                    self.sensor1_Rpwr.delete(0,END)
                    # insert the default Sensor 1 PWR Received value
                    self.sensor1_Rpwr.insert(0,App.DEFAULT_VALUES['Sensor 1 PWR Received'])
                    # set local Sensor 1 PWR Received value to default value 
                    self.sensor1_power_received_dBm_val = App.DEFAULT_VALUES['Sensor 1 PWR Received']
                elif choice == 'Bypass':
                    bypass_ewt1_bool = True
                    # set all local Sensor 1 values to None
                    if self.sensor1_mgrs_val in [None,""] or not check_mgrs_input(self.sensor1_mgrs_val):
                        self.sensor1_mgrs_val = None
                        self.sensor1_mgrs.delete(0,END)
                    self.sensor1_grid_azimuth_val = None
                    self.sensor1_power_received_dBm_val = None
                    # clear all Sensor 1 input fields
                    self.sensor1_lob.delete(0,END)
                    self.sensor1_Rpwr.delete(0,END)
                # if user chooses to re-input the Sensor 1 PWR Received value
                elif choice == 'Re-input':
                    # end function
                    return
        # try to read the Sensor 2 MGRS value
        try:
            # if Single LOB boolean value is FALSE
            if not single_lob_bool:
                # get input from Sensor 2 MGRS field
                self.sensor2_mgrs_val = str(self.sensor2_mgrs.get()).strip().replace(" ","")
                # assess if Sensor 2 MGRS input is valid
                if check_mgrs_input(self.sensor2_mgrs_val):
                    # if MGRS value is valid, pass on to next portion of function code
                    pass
                else:
                    # if MGRS is invalid, give user the option to re-input, bypass EWT, or use default value
                    if not self.bypass_input_errors:
                        choice = self._input_error(category='Sensor 2 Grid',msg=f'Invalid Input {self.sensor2_mgrs_val}',single_lob_option=False,cut_option=False,ewt_bypass_option=True,EWT_num='2')
                    else:
                        choice = "Bypass"
                    # end function if user x's out of the pop-up window
                    if choice is None: return
                    # if user chooses to use default Sensor 2 MGRS value
                    if choice == 'Default':
                        # clear Sensor 2 MGRS input field
                        self.sensor2_mgrs.delete(0,END)
                        # insert default Sensor 2 MGRS value into field
                        self.sensor2_mgrs.insert(0,App.DEFAULT_VALUES['Sensor 2 MGRS'])
                        # set local Sensor 2 MGRS value to default value
                        self.sensor2_mgrs_val = App.DEFAULT_VALUES['Sensor 2 MGRS']
                    # if user chooses to bypass Sensor 2 input
                    elif choice == 'Bypass':
                        bypass_ewt2_bool = True
                        # set all local Sensor 2 values to None
                        self.sensor2_mgrs_val = None
                        self.sensor2_grid_azimuth_val = None
                        self.sensor2_power_received_dBm_val = None
                        # clear all Sensor 2 input fields
                        self.sensor2_mgrs.delete(0,END) 
                        self.sensor2_lob.delete(0,END)
                        self.sensor2_Rpwr.delete(0,END)  
                    # if user chooses to re-input the Sensor 2 MGRS value
                    elif choice == 'Re-input':
                        # end function
                        return
                    # if user chooses to utilize only a single LOB
                    elif choice == 'SL':
                        # set Single LOB boolean value to TRUE
                        single_lob_bool = True
                        if self.sensor2_mgrs_val in [None,""] or not check_mgrs_input(self.sensor2_mgrs_val):
                            self.sensor2_mgrs_val = None
                            self.sensor2_mgrs.delete(0,END)
                if not bypass_ewt2_bool:
                    # clear the previous sensor 2 MGRS input
                    self.sensor2_mgrs.delete(0,END)
                    # insert the default sensor 2 MGRS value
                    self.sensor2_mgrs.insert(0,correct_mgrs_input(self.sensor2_mgrs_val))
            # if Single LOB Boolean value is TRUE
            else:
                # set all local Sensor 2 values to None
                if self.sensor2_mgrs_val in [None,""] or not check_mgrs_input(self.sensor2_mgrs_val):
                    self.sensor2_mgrs_val = None
                    self.sensor2_mgrs.delete(0,END)
                self.sensor2_grid_azimuth_val = None
                self.sensor2_power_received_dBm_val = None
                # clear all Sensor 2 input fields
                self.sensor2_lob.delete(0,END)
                self.sensor2_Rpwr.delete(0,END)   
        # exception handling for ValueError         
        except ValueError:
            # set local Sensor 2 MGRS value to None
            if self.sensor2_mgrs_val in [None,""] or not check_mgrs_input(self.sensor2_mgrs_val):
                self.sensor2_mgrs_val = None
                self.sensor2_mgrs.delete(0,END)
            self.sensor2_grid_azimuth_val = None
            self.sensor2_power_received_dBm_val = None
        # if Single LOB Boolean value is FALSE
        if not single_lob_bool and not bypass_ewt2_bool:
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
                # if ValueError occurs, give user the option to re-input, bypass EWT, or use default value
                if not self.bypass_input_errors:
                    choice = self._input_error(category='Sensor 2 Grid Azimuth',msg='Invalid Input',single_lob_option=False,cut_option=False,ewt_bypass_option=True,EWT_num='2')
                else:
                    choice = "Bypass"
                # end function if user x's out of the pop-up window
                if choice is None: return
                # if users chooses to utilize the default Sensor 2 LOB value
                if choice == 'Default':
                    # clear the Sensor 2 LOB input field
                    self.sensor2_lob.delete(0,END)
                    # insert the default Sensor 2 LOB value 
                    self.sensor2_lob.insert(0,App.DEFAULT_VALUES['Sensor 2 LOB'])   
                    # set local Sensor 2 LOB value to default value
                    self.sensor2_grid_azimuth_val = App.DEFAULT_VALUES['Sensor 2 LOB']
                # if user chooses to bypass Sensor 2 input
                elif choice == 'Bypass':
                    bypass_ewt2_bool = True
                    # set all local Sensor 2 values to None
                    if self.sensor2_mgrs_val in [None,""] or not check_mgrs_input(self.sensor2_mgrs_val):
                        self.sensor2_mgrs_val = None
                        self.sensor2_mgrs.delete(0,END)
                    self.sensor2_grid_azimuth_val = None
                    self.sensor2_power_received_dBm_val = None
                    # clear all Sensor 2 input fields
                    self.sensor2_lob.delete(0,END)
                    self.sensor2_Rpwr.delete(0,END)
                # if user chooses to re-input the Sensor 2 LOB value
                elif choice == 'Re-input':
                    # end function
                    return
                # if user chooses to only utilize a Single LOB
                elif choice == 'SL':
                    # set Single LOB Boolean value to TRUE
                    single_lob_bool = True
                    # set local Sensor 2 LOB value to None
                    self.sensor2_grid_azimuth_val = None
                    # clear Sensor 2 LOB input field
                    self.sensor2_lob.delete(0,END)
        # if Single LOB Boolean value is TRUE
        else:
            # set all local Sensor 2 input values to None
            if self.sensor2_mgrs_val in [None,""] or not check_mgrs_input(self.sensor2_mgrs_val):
                self.sensor2_mgrs_val = None
                self.sensor2_mgrs.delete(0,END)
            self.sensor2_grid_azimuth_val = None
            self.sensor2_power_received_dBm_val = None
            # clear all Sensor 2 input fields
            self.sensor2_lob.delete(0,END)
            self.sensor2_Rpwr.delete(0,END)
        # if Single LOB Boolean value is FALSE
        if not single_lob_bool and not bypass_ewt2_bool:
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
                # if ValueError occurs, give user the option to re-input, bypass EWT, or use default value
                if not self.bypass_input_errors:
                    choice = self._input_error(category='Sensor 2 Power Received',msg='Invalid Input',single_lob_option=False,cut_option=False,ewt_bypass_option=True,EWT_num='2')
                else:
                    choice = "Bypass"
                # end function if user x's out of the pop-up window
                if choice is None: return
                # if user chooses to utilize the default Sensor 2 LOB value
                if choice == 'Default':
                    # clear the Sensor 2 Received PWR input field
                    self.sensor2_Rpwr.delete(0,END)
                    # insert the default Sensor 2 PWR Received value
                    self.sensor2_Rpwr.insert(0,App.DEFAULT_VALUES['Sensor 2 PWR Received'])
                    # set local Sensor 2 PWR Received value to default value
                    self.sensor2_power_received_dBm_val = App.DEFAULT_VALUES['Sensor 2 PWR Received']
                # if user chooses to bypass Sensor 2 input
                elif choice == 'Bypass':
                    bypass_ewt2_bool = True
                    # set all local Sensor 2 values to None
                    if self.sensor2_mgrs_val in [None,""] or not check_mgrs_input(self.sensor2_mgrs_val):
                        self.sensor2_mgrs_val = None
                        self.sensor2_mgrs.delete(0,END)
                    self.sensor2_grid_azimuth_val = None
                    self.sensor2_power_received_dBm_val = None
                    # clear all Sensor 2 input fields
                    self.sensor2_lob.delete(0,END)
                    self.sensor2_Rpwr.delete(0,END)
                # if user chooses to re-input the Sensor 2 PWR Received value
                elif choice == 'Re-input':
                    # end function
                    return
                # if user chooses to only utilize a single LOB
                elif choice == 'SL':
                    # set Single LOB Boolean to TRUE
                    single_lob_bool = True
                    # set local Sensor 2 PWR Received value to None
                    self.sensor2_power_received_dBm_val = None
                    # clear Sensor 2 PWR Received input field
                    self.sensor2_Rpwr.delete(0,END)
        else:
            # set all local Sensor 2 values to None
            if self.sensor2_mgrs_val in [None,""] or not check_mgrs_input(self.sensor2_mgrs_val):
                self.sensor2_mgrs_val = None
                self.sensor2_mgrs.delete(0,END)
            self.sensor2_grid_azimuth_val = None
            self.sensor2_power_received_dBm_val = None
            # clear all Sensor 2 input fields
            self.sensor2_lob.delete(0,END)
            self.sensor2_Rpwr.delete(0,END)
        try:
            # if Single LOB and CUT boolean value are FALSE
            if not single_lob_bool and not cut_bool:
                # get input from Sensor 3 MGRS field
                self.sensor3_mgrs_val = str(self.sensor3_mgrs.get()).strip().replace(" ","")
                # assess if Sensor 3 MGRS input is valid
                if check_mgrs_input(self.sensor3_mgrs_val):
                    # if MGRS value is valid, pass on to next portion of function code
                    pass
                else:
                    # if MGRS is invalid, give user the option to re-input, bypass EWT, or use default value
                    if not self.bypass_input_errors:
                        choice = self._input_error(category='Sensor 3 Grid',msg=f'Invalid Input {self.sensor3_mgrs_val}',single_lob_option=False,cut_option=False,ewt_bypass_option=True,EWT_num='3')
                    else:
                        choice = "Bypass"
                    # end function if user x's out of the pop-up window
                    if choice is None: return
                    # if user chooses to use default Sensor 3 MGRS value
                    if choice == 'Default':
                        # clear Sensor 3 MGRS input field
                        self.sensor3_mgrs.delete(0,END)
                        # insert default Sensor 3 MGRS value into field
                        self.sensor3_mgrs.insert(0,App.DEFAULT_VALUES['Sensor 3 MGRS'])
                        # set local Sensor 3 MGRS value to default value
                        self.sensor3_mgrs_val = App.DEFAULT_VALUES['Sensor 3 MGRS']
                    # if user chooses to bypass Sensor 3 input
                    elif choice == 'Bypass':
                        bypass_ewt3_bool = True
                        # set all local Sensor 3 values to None
                        self.sensor3_mgrs_val = None
                        self.sensor3_grid_azimuth_val = None
                        self.sensor3_power_received_dBm_val = None
                        # clear all Sensor 1 input fields
                        self.sensor3_mgrs.delete(0,END) 
                        self.sensor3_lob.delete(0,END)
                        self.sensor3_Rpwr.delete(0,END)
                    # if user chooses to re-input the Sensor 3 MGRS value
                    elif choice == 'Re-input':
                        # end function
                        return
                    # if user chooses to utilize only a single LOB
                    elif choice == 'SL':
                        # set Single LOB boolean value to TRUE
                        single_lob_bool = True
                        # set CUT boolean value to FALSE
                        cut_bool = False
                        if self.sensor3_mgrs_val in [None,""] or not check_mgrs_input(self.sensor3_mgrs_val):
                            self.sensor3_mgrs_val = None
                            self.sensor3_mgrs.delete(0,END)
                    elif choice == 'LOB/CUT':
                        # set Single LOB boolean value to FALSE
                        single_lob_bool = False
                        # set CUT boolean value to TRUE
                        cut_bool = True
                        if self.sensor3_mgrs_val in [None,""] or not check_mgrs_input(self.sensor3_mgrs_val):
                            self.sensor3_mgrs_val = None
                            self.sensor3_mgrs.delete(0,END)
                if not bypass_ewt3_bool:
                    # clear the previous sensor 2 MGRS input
                    self.sensor3_mgrs.delete(0,END)
                    # insert the default sensor 3 MGRS value
                    self.sensor3_mgrs.insert(0,correct_mgrs_input(self.sensor3_mgrs_val))
            # if Single LOB Boolean value is TRUE
            else:
                # set all local Sensor 3 values to None
                if self.sensor3_mgrs_val in [None,""] or not check_mgrs_input(self.sensor3_mgrs_val):
                    self.sensor3_mgrs_val = None
                    self.sensor3_mgrs.delete(0,END)
                self.sensor3_grid_azimuth_val = None
                self.sensor3_power_received_dBm_val = None
                # clear all Sensor 3 input fields
                self.sensor3_lob.delete(0,END)
                self.sensor3_Rpwr.delete(0,END)   
        # exception handling for ValueError         
        except ValueError:
            if self.sensor3_mgrs_val in [None,""] or not check_mgrs_input(self.sensor3_mgrs_val):
                self.sensor3_mgrs_val = None
                self.sensor3_mgrs.delete(0,END)
        # if Single LOB and CUT Boolean value is FALSE
        if not single_lob_bool and not cut_bool and not bypass_ewt3_bool:
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
                # if ValueError occurs, give user the option to re-input, bypass EWT, or use default value
                if not self.bypass_input_errors:
                    choice = self._input_error(category='Sensor 3 Grid Azimuth',msg='Invalid Input',single_lob_option=False,cut_option=False,ewt_bypass_option=True,EWT_num='3')
                else:
                    choice = "Bypass"
                # end function if user x's out of the pop-up window
                if choice is None: return
                # if users chooses to utilize the default Sensor 3 LOB value
                if choice == 'Default':
                    # clear the Sensor 3 LOB input field
                    self.sensor3_lob.delete(0,END)
                    # insert the default Sensor 3 LOB value 
                    self.sensor3_lob.insert(0,App.DEFAULT_VALUES['Sensor 3 LOB'])   
                    # set local Sensor 3 LOB value to default value
                    self.sensor3_grid_azimuth_val = App.DEFAULT_VALUES['Sensor 3 LOB']
                # if user chooses to bypass Sensor 3 input
                elif choice == 'Bypass':
                    bypass_ewt3_bool = True
                    # set all local Sensor 3 values to None
                    if self.sensor3_mgrs_val in [None,""] or not check_mgrs_input(self.sensor3_mgrs_val):
                        self.sensor3_mgrs_val = None
                        self.sensor3_mgrs.delete(0,END)
                    self.sensor3_grid_azimuth_val = None
                    self.sensor3_power_received_dBm_val = None
                    # clear all Sensor 1 input fields
                    self.sensor3_lob.delete(0,END)
                    self.sensor3_Rpwr.delete(0,END)
                # if user chooses to re-input the Sensor 3 LOB value
                elif choice == 'Re-input':
                    # end function
                    return
                # if user chooses to only utilize a Single LOB
                elif choice == 'LOB/CUT':
                    # set Single LOB boolean value to TRUE
                    single_lob_bool = True
                    # set CUT boolean value to FALSE
                    cut_bool = False
                    if self.sensor3_mgrs_val in [None,""] or not check_mgrs_input(self.sensor3_mgrs_val):
                        self.sensor3_mgrs_val = None
                        self.sensor3_mgrs.delete(0,END)
        # if Single LOB or CUT Boolean value is TRUE
        else:
            # set all local Sensor 3 input values to None
            if self.sensor3_mgrs_val in [None,""] or not check_mgrs_input(self.sensor3_mgrs_val):
                self.sensor3_mgrs_val = None
                self.sensor3_mgrs.delete(0,END)
            self.sensor3_grid_azimuth_val = None
            self.sensor3_power_received_dBm_val = None
            # clear all Sensor 3 input fields
            self.sensor3_lob.delete(0,END)
            self.sensor3_Rpwr.delete(0,END)
        # if Single LOB and CUT Boolean value is FALSE
        if not single_lob_bool and not cut_bool and not bypass_ewt3_bool:
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
                # if ValueError occurs, give user the option to re-input, bypass EWT, or use default value
                if not self.bypass_input_errors:
                    choice = self._input_error(category='Sensor 3 Power Received',msg='Invalid Input',single_lob_option=False,cut_option=False,ewt_bypass_option=True,EWT_num='3')
                else:
                    choice = "Bypass"
                # end function if user x's out of the pop-up window
                if choice is None: return
                # if user chooses to utilize the default Sensor 3 LOB value
                if choice == 'Default':
                    # clear the Sensor 3 Received PWR input field
                    self.sensor3_Rpwr.delete(0,END)
                    # insert the default Sensor 3 PWR Received value
                    self.sensor3_Rpwr.insert(0,App.DEFAULT_VALUES['Sensor 3 PWR Received'])  
                    # set local Sensor 2 PWR Received value to default value
                    self.sensor3_power_received_dBm_val = App.DEFAULT_VALUES['Sensor 3 PWR Received']
                # if user chooses to bypass Sensor 3 input
                elif choice == 'Bypass':
                    bypass_ewt3_bool = True
                    # set all local Sensor 3 values to None
                    if self.sensor3_mgrs_val in [None,""] or not check_mgrs_input(self.sensor3_mgrs_val):
                        self.sensor3_mgrs_val = None
                        self.sensor3_mgrs.delete(0,END)
                    self.sensor3_grid_azimuth_val = None
                    self.sensor3_power_received_dBm_val = None
                    # clear all Sensor 1 input fields
                    self.sensor3_lob.delete(0,END)
                    self.sensor3_Rpwr.delete(0,END)
                # if user chooses to re-input the Sensor 3 PWR Received value
                elif choice == 'Re-input':
                    # end function
                    return
                # if user chooses to only utilize a single LOB
                elif choice == 'LOB/CUT':
                    # set Single LOB boolean value to TRUE
                    single_lob_bool = True
                    # set CUT boolean value to FALSE
                    cut_bool = False
                    if self.sensor3_mgrs_val in [None,""] or not check_mgrs_input(self.sensor3_mgrs_val):
                        self.sensor3_mgrs_val = None
                        self.sensor3_mgrs.delete(0,END)
        else:
            # set all local Sensor 3 values to None
            if self.sensor3_mgrs_val in [None,""] or not check_mgrs_input(self.sensor3_mgrs_val):
                self.sensor3_mgrs_val = None
                self.sensor3_mgrs.delete(0,END)
            self.sensor3_grid_azimuth_val = None
            self.sensor3_power_received_dBm_val = None
            # clear all Sensor 2 input fields
            self.sensor3_lob.delete(0,END)
            self.sensor3_Rpwr.delete(0,END)
        if bypass_ewt1_bool and bypass_ewt2_bool and bypass_ewt3_bool:
            self._show_info("No EWT data entered.",icon='warning')
            return
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
            # if ValueError occurs, give user the option to re-input, bypass EWT, or use default value
            choice = self._input_error(category='Frequency',msg='Invalid Input')
            # end function if user x's out of the pop-up window
            if choice is None: return
            # if user chooses to use the default frequency value
            if choice == 'Default':
                # clear frequency input field
                self.frequency.delete(0,END)
                # input default frequency value in input field
                self.frequency.insert(0,App.DEFAULT_VALUES['Frequency'])
                # set local frequency value to default frequency value
                self.frequency_MHz_val = App.DEFAULT_VALUES['Frequency']
            # if user chooses to re-input the frequency value
            elif choice == 'Re-input':
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
            choice = self._input_error(category='Minimum ERP',msg='Invalid Input')
            # end function if user x's out of the pop-up window
            if choice is None: return
            # if user chooses to utilize the default Min ERP value
            if choice == 'Default':
                # clear Min ERP input field
                self.min_ERP.delete(0,END)
                # insert default Min ERP value in input field
                self.min_ERP.insert(0,App.DEFAULT_VALUES['Min ERP'])
                # set local Min ERP value to default Min ERP value
                self.min_wattage_val = App.DEFAULT_VALUES['Min ERP']
            # if user chooses to re-input Min ERP value
            elif choice == 'Re-input':
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
            choice = self._input_error(category='Maximum ERP',msg='Invalid Input')
            # end function if user x's out of the pop-up window
            if choice is None: return
            # if user chooses to use the default Max ERP value
            if choice == 'Default':
                # clear Max ERP input field
                self.max_ERP.delete(0,END)
                # insert default Max ERP in input field
                self.max_ERP.insert(0,App.DEFAULT_VALUES['Max ERP'])
                # set local Max ERP value to default value
                self.max_wattage_val = App.DEFAULT_VALUES['Max ERP']
            # if user chooses to re-input the Max ERP value
            elif choice == 'Re-input':
                # end function
                return
        # try to read path-loss coefficient value
        try:
            # set local path-loss coefficient value to global path-loss coefficent value
            self.path_loss_coeff_val = self.path_loss_coeff
        # exception handling for ValueError
        except ValueError:
            # if ValueError occurs, give user the option to re-input or use default value
            choice = self._input_error(category='Path-Loss Coefficient',msg='Invalid Input')
            # end function if user x's out of the pop-up window
            if choice is None: return
            # if user chooses to use the default path-loss coefficient
            if choice == 'Default':
                # set local path-loss coefficient value to default value
                self.path_loss_coeff_val = App.DEFAULT_VALUES['Path-Loss Coefficient']
                # set path-loss coefficient input field to default description
                self.option_path_loss_coeff.set(App.DEFAULT_VALUES['Path-Loss Coefficient Description'])
                # set global path-loss coefficient value to default value
                self.path_loss_coeff = App.DEFAULT_VALUES['Path-Loss Coefficient']
            # if user chooses to re-input the path-loss coefficient
            elif choice == 'Re-input':
                # end function
                return
        # logging the input values
        self.bypass_input_errors = False
        self._log_ewt_input_values()

    def set_target_field(self) -> None:
        import numpy as np
        from coords import convert_coords_to_mgrs, format_readable_mgrs
        if self.target_coord == None and self.target_mgrs == None:
            sensor1_target_mgrs = convert_coords_to_mgrs(self.sensor1_target_coord)
            sensor2_target_mgrs = convert_coords_to_mgrs(self.sensor2_target_coord)
            sensor3_target_mgrs = convert_coords_to_mgrs(self.sensor3_target_coord)
            nl = "\n"
            # set target grid field
            target_grid_list = [f'{x}' for x in [sensor1_target_mgrs,sensor2_target_mgrs,sensor3_target_mgrs] if x != None]
            target_grid_list_formatted = [f'{format_readable_mgrs(x)}' for x in [sensor1_target_mgrs,sensor2_target_mgrs,sensor3_target_mgrs] if x != None]
            self.target_grid.configure(text=f'{nl.join(target_grid_list_formatted)}',text_color='yellow')
            # set target error field
            target_error_list = [x for x in [self.sensor1_lob_error_acres,self.sensor2_lob_error_acres,self.sensor3_lob_error_acres] if x != None]
            self.target_error.configure(text=f'{max(target_error_list):,.0f} acres',text_color='white')
            self.target_error_val = max(target_error_list)
            # define multi-target MGRS value
            self.target_mgrs = f'{", ".join(target_grid_list)}'
            # define multi-target coordinates
            target_coord_list = [x for x in [self.sensor1_target_coord,self.sensor2_target_coord,self.sensor3_target_coord] if x != None]
            # set map position based on target location
            self.map_widget.set_position(np.average([x[0] for x in target_coord_list]), np.average([x[1] for x in target_coord_list]))
            target_coord_list = [x for x in [self.sensor1_target_coord,self.sensor2_target_coord,self.sensor3_target_coord] if x != None]
            if len(target_coord_list) == 1:
                self.target_coord = target_coord_list[0]
            elif len(target_coord_list) > 1:
                target_coord_list = [[str(x[0]),str(x[1])] for x in target_coord_list]
                target_coord_list = [f'{", ".join(x)}' for x in target_coord_list]
                self.target_coord = f'{" | ".join(target_coord_list)}'
            self.logger_targeting.info(f'{self.target_class} {"Targets" if len(target_grid_list_formatted) > 1 else "Target"} at {self.target_mgrs} with an error of {self.target_error_val:,.0f} acres')
        else:
            self.logger_targeting.info(f'{self.target_class} Target at {format_readable_mgrs(self.target_mgrs)} with an error of {self.target_error_val:,.0f} acres')
        if self.sensor1_distance_val != None: self.logger_targeting.info(f'Sensor 1 distance to target: {self._generate_sensor_distance_text(self.sensor1_distance_val)}')
        if self.sensor1_bearing_val != None: self.logger_targeting.info(f'Sensor 1 bearing to target: {self.sensor1_bearing_val}°')
        if self.sensor2_distance_val != None: self.logger_targeting.info(f'Sensor 2 distance to target: {self._generate_sensor_distance_text(self.sensor2_distance_val)}')
        if self.sensor2_bearing_val != None: self.logger_targeting.info(f'Sensor 2 bearing to target: {self.sensor2_bearing_val}°')
        if self.sensor3_distance_val != None: self.logger_targeting.info(f'Sensor 3 distance to target: {self._generate_sensor_distance_text(self.sensor3_distance_val)}')
        if self.sensor3_bearing_val != None: self.logger_targeting.info(f'Sensor 3 bearing to target: {self.sensor3_bearing_val}°')

    def ewt_input_processor(self,*args, **kwargs) -> None:
        from utilities import format_readable_DTG, generate_DTG
        from coords import convert_coords_to_mgrs, convert_mgrs_to_coords, format_readable_mgrs, get_bearing_between_coordinates, get_distance_between_coords, get_center_coord, get_coords_from_LOBs
        from ew import get_emission_distance
        from map import check_for_intersection, check_if_point_in_polygon, get_intersection, get_line, get_polygon_area, organize_polygon_coords
        import threading

        def elevation_profile_worker(sensor_coord, nearside_target_distance_km, target_coord, farside_target_distance_km, callback):
            from dted import get_elevation_profile, generate_coordinates_of_interest
            try:
                farside_coord = generate_coordinates_of_interest(sensor_coord, target_coord, farside_target_distance_km)
                elevation_data = get_elevation_profile(sensor_coord, farside_coord, interpoint_distance_m=30)

                # Schedule callback in main thread using after
                if hasattr(callback, '__self__') and hasattr(callback.__self__, 'after'):
                    callback.__self__.after(0, callback, elevation_data, sensor_coord, nearside_target_distance_km, target_coord, farside_target_distance_km)
                else:
                    # fallback if no .after() is found — will run in the thread (unsafe for GUI)
                    callback(elevation_data, sensor_coord, nearside_target_distance_km, target_coord, farside_target_distance_km)
            except Exception as e:
                self.logger_gui.error(f"Error generating elevation profile: {e}")

        def run_2D_elevation_plotter_threaded(sensor_coord, nearside_target_distance_km, target_coord, farside_target_distance_km, callback):
            thread = threading.Thread(
                target=elevation_profile_worker,
                args=(sensor_coord, nearside_target_distance_km, target_coord, farside_target_distance_km, callback)
            )
            thread.daemon = True
            thread.start()

        def plot_lobs(s1lnmc,s1lfmc,s2lnmc,s2lfmc,s3lnmc,s3lfmc,plot_ewt1_lob_tgt_bool=True,plot_ewt2_lob_tgt_bool=True,plot_ewt3_lob_tgt_bool=True):
            self.sensor1_target_coord = None ; self.sensor2_target_coord = None ; self.sensor3_target_coord = None
            import numpy as np
            num_lobs = 3-[self.sensor1_grid_azimuth_val,self.sensor2_grid_azimuth_val,self.sensor3_grid_azimuth_val].count(None)
            # assess if there is no target class
            if self.target_class == '':
                # set target class
                self.target_class = f'({num_lobs} {"LOB" if num_lobs == 1 else "LOBs"})'
                # set target grid label to include target classification
                self.label_target_grid.configure(text=f'{"TARGET GRID" if num_lobs == 1 else "TARGET GRIDs"} {self.target_class}'.strip(),text_color='red')
            # assess if sensor 1 has a non-None grid
            if self.sensor1_mgrs_val != None and (self.sensor1_grid_azimuth_val == None or self.sensor1_power_received_dBm_val == None):
                self.sensor1_coord = convert_mgrs_to_coords(self.sensor1_mgrs_val)
                # define and set sensor 1 marker on the map
                self.plot_EWT(self.sensor1_coord,1,False)
            # assess if sensor 1 has non-None values
            if self.sensor1_mgrs_val != None and self.sensor1_grid_azimuth_val != None and self.sensor1_power_received_dBm_val != None:
                # calculate sensor 1 target coordinate
                self.sensor1_target_coord = [np.average([s1lnmc[0],s1lfmc[0]]),np.average([s1lnmc[1],s1lfmc[1]])]
                # calculate sensor 1 target MGRS
                sensor1_target_mgrs = convert_coords_to_mgrs(self.sensor1_target_coord)
                # calculate sensor 1 LOB error (in acres)
                self.sensor1_lob_error_acres = get_polygon_area(self.sensor1_lob_polygon)
                # define sensor 1 LOB description
                sensor1_lob_description = f"EWT 1 at {format_readable_mgrs(self.sensor1_mgrs_val)} with a LOB at bearing {int(self.sensor1_grid_azimuth_val)}° between {self._generate_sensor_distance_text(self.sensor1_min_distance_m)} and {self._generate_sensor_distance_text(self.sensor1_max_distance_m)} with {self.sensor1_lob_error_acres:,.0f} acres of error"
                # define and set sensor 1 marker on the map
                self.plot_EWT(self.sensor1_coord,1,False)
                # define and set sensor 1 center line
                sensor1_lob = self.map_widget.set_polygon(
                    position_list=[(self.sensor1_coord[0],self.sensor1_coord[1]),(s1lfmc[0],s1lfmc[1])],
                    fill_color=App.DEFAULT_VALUES['LOB Fill Color'],
                    outline_color=App.DEFAULT_VALUES['LOB Center Line Color'],
                    border_width=App.DEFAULT_VALUES['Border Width'],
                    command=self.polygon_click,
                    data="LOB Line\n"+sensor1_lob_description)
                # add sensor 1 LOB center-line to polygon list
                self._append_object(sensor1_lob,"LOB")
                # define and set sensor 1 LOB area
                sensor1_lob_area = self.map_widget.set_polygon(
                    position_list=self.sensor1_lob_polygon,
                    fill_color=App.DEFAULT_VALUES['LOB Fill Color'],
                    outline_color=App.DEFAULT_VALUES['LOB Area Outline Color'],
                    border_width=App.DEFAULT_VALUES['Border Width'],
                    command=self.polygon_click,
                    data="LOB Area\n"+sensor1_lob_description)
                # add sensor 1 LOB area to polygon list
                self._append_object(sensor1_lob_area,"LOB")
                if plot_ewt1_lob_tgt_bool:
                    # define and set sensor 1 target marker
                    target1_marker = self.map_widget.set_marker(
                        deg_x=self.sensor1_target_coord[0], 
                        deg_y=self.sensor1_target_coord[1], 
                        text=f'{format_readable_mgrs(sensor1_target_mgrs)}', 
                        image_zoom_visibility=(10, float("inf")),
                        marker_color_circle='white',
                        icon=self.target_image_LOB,
                        command=self.marker_click,
                        data=f'TGT (LOB)\nEWT 1\n{format_readable_mgrs(sensor1_target_mgrs)}\nat {format_readable_DTG(generate_DTG())}')
                    # add sensor 1 target marker to target marker list
                    self._append_object(target1_marker,"TGT")
                # calculate sensor 1 distance to target 1
                self.sensor1_distance_val = int(get_distance_between_coords(self.sensor1_coord,self.sensor1_target_coord))
                self.sensor1_bearing_val = int(get_bearing_between_coordinates(self.sensor1_coord,self.sensor1_target_coord))
                # generate sensor 1 distance from target text     
                dist_sensor1_text = self._generate_sensor_distance_text(self.sensor1_distance_val,self.sensor1_bearing_val)
                # set sensor 1 distance field
                self.sensor1_distance.configure(text=dist_sensor1_text,text_color='white')
                # generate a 2D elevation plot
                if self.target_class == '(1 LOB)' and not self.bypass_elevation_plot_prompt:
                    from CTkMessagebox import CTkMessagebox
                    msgBox = CTkMessagebox(title="2D Elevation Plot", message="Do you want to generate a 2D Elevation Plot", icon='info',options=['Yes','No'])
                    response = msgBox.get()
                    if response == 'Yes': 
                        run_2D_elevation_plotter_threaded(self.sensor1_coord,self.sensor1_min_distance_km,self.sensor1_target_coord,self.sensor1_max_distance_km,callback=self._safe_plot_callback)
                        self.logger_gui.info(f"Attempting to create a 2D Elevation Plot for EWT 1 at {format_readable_mgrs(self.sensor1_mgrs_val)} with a LOB at bearing {int(self.sensor1_grid_azimuth_val)}° between {self._generate_sensor_distance_text(self.sensor1_min_distance_m)} and {self._generate_sensor_distance_text(self.sensor1_max_distance_m)}")
            else:
                sensor1_target_mgrs = None
                self.sensor1_lob_error_acres = None
                self.sensor1_target_coord = None
                self.sensor1_distance.configure(text="N/A",text_color='white')
            # assess if sensor 2 has a non-None grid
            if self.sensor2_mgrs_val != None and (self.sensor2_grid_azimuth_val == None or self.sensor2_power_received_dBm_val == None):
                # define and set sensor 2 marker on the map
                self.sensor2_coord = convert_mgrs_to_coords(self.sensor2_mgrs_val)
                self.plot_EWT(self.sensor2_coord,2,False)
            # assess if sensor 2 has non-None values
            if self.sensor2_mgrs_val != None and self.sensor2_grid_azimuth_val != None and self.sensor2_power_received_dBm_val != None:
                # calculate sensor 2 target coordinate
                self.sensor2_target_coord = [np.average([s2lnmc[0],s2lfmc[0]]),np.average([s2lnmc[1],s2lfmc[1]])]
                # calculate sensor 2 target MGRS
                sensor2_target_mgrs = convert_coords_to_mgrs(self.sensor2_target_coord)
                # calculate LOB 2 sensor error (in acres)
                self.sensor2_lob_error_acres = get_polygon_area(self.sensor2_lob_polygon)
                # define LOB 2 description
                sensor2_lob_description = f"EWT 2 at {format_readable_mgrs(self.sensor2_mgrs_val)} with a LOB at bearing {int(self.sensor2_grid_azimuth_val)}° between {self._generate_sensor_distance_text(self.sensor2_min_distance_m)} and {self._generate_sensor_distance_text(self.sensor2_max_distance_m)} with {self.sensor2_lob_error_acres:,.0f} acres of error"
                # define and set sensor 2 marker on the map
                self.plot_EWT(self.sensor2_coord,2,False)
                # define and set sensor 2 LOB area
                sensor2_lob = self.map_widget.set_polygon(
                    position_list=[(self.sensor2_coord[0],self.sensor2_coord[1]),(s2lfmc[0],s2lfmc[1])],
                    fill_color=App.DEFAULT_VALUES['LOB Fill Color'],
                    outline_color=App.DEFAULT_VALUES['LOB Center Line Color'],
                    border_width=App.DEFAULT_VALUES['Border Width'],
                    command=self.polygon_click,
                    data="LOB Line\n"+sensor2_lob_description)
                # add sensor 2 LOB area to polygon list
                self._append_object(sensor2_lob,"LOB")
                # define and set sensor 2 LOB area
                sensor2_lob_area = self.map_widget.set_polygon(
                    position_list=self.sensor2_lob_polygon,
                    fill_color=App.DEFAULT_VALUES['LOB Fill Color'],
                    outline_color=App.DEFAULT_VALUES['LOB Area Outline Color'],
                    border_width=App.DEFAULT_VALUES['Border Width'],
                    command=self.polygon_click,
                    data="LOB Area\n"+sensor2_lob_description)
                # add LOB area to polygon list
                self._append_object(sensor2_lob_area,"LOB")
                if plot_ewt2_lob_tgt_bool:
                    # define and set sensor 2 target marker
                    target2_marker = self.map_widget.set_marker(
                        deg_x=self.sensor2_target_coord[0], 
                        deg_y=self.sensor2_target_coord[1], 
                        text=f'{format_readable_mgrs(sensor2_target_mgrs)}', 
                        image_zoom_visibility=(10, float("inf")),
                        marker_color_circle='white',
                        icon=self.target_image_LOB,
                        command=self.marker_click,
                        data=f'TGT (LOB)\nEWT 2\n{format_readable_mgrs(sensor2_target_mgrs)}\nat {format_readable_DTG(generate_DTG())}')
                    # add sensor 2 target marker to tarket marker list
                    self._append_object(target2_marker,"TGT")
                # calculate sensor 1 distance to target 2
                self.sensor2_distance_val = int(get_distance_between_coords(self.sensor2_coord,self.sensor2_target_coord))
                self.sensor2_bearing_val = int(get_bearing_between_coordinates(self.sensor2_coord,self.sensor2_target_coord))
                # generate sensor 2 distance from target text       
                dist_sensor2_text = self._generate_sensor_distance_text(self.sensor2_distance_val,self.sensor2_bearing_val)
                # set sensor 2 distance field
                self.sensor2_distance.configure(text=dist_sensor2_text,text_color='white')
                # generate a 2D elevation plot
                if self.target_class == '(1 LOB)' and not self.bypass_elevation_plot_prompt:
                    from CTkMessagebox import CTkMessagebox
                    msgBox = CTkMessagebox(title="2D Elevation Plot", message="Do you want to generate a 2D Elevation Plot", icon='info',options=['Yes','No'])
                    response = msgBox.get()
                    if response == 'Yes': 
                        run_2D_elevation_plotter_threaded(self.sensor2_coord,self.sensor2_min_distance_km,self.sensor2_target_coord,self.sensor2_max_distance_km,callback=self._safe_plot_callback)
                        self.logger_gui.info(f"Attempting to create a 2D Elevation Plot for EWT 2 at {format_readable_mgrs(self.sensor2_mgrs_val)} with a LOB at bearing {int(self.sensor2_grid_azimuth_val)}° between {self._generate_sensor_distance_text(self.sensor2_min_distance_m)} and {self._generate_sensor_distance_text(self.sensor2_max_distance_m)}")

            else:
                sensor2_target_mgrs = None
                self.sensor2_lob_error_acres = None
                self.sensor2_target_coord = None
                self.sensor2_distance.configure(text="N/A",text_color='white')
            # assess if sensor 3 has a non-None grid
            if self.sensor3_mgrs_val != None and (self.sensor3_grid_azimuth_val == None or self.sensor3_power_received_dBm_val == None):
                # define and set sensor 3 marker on the map
                self.sensor3_coord = convert_mgrs_to_coords(self.sensor3_mgrs_val)
                self.plot_EWT(self.sensor3_coord,3,False)
            # assess if sensor 3 has non-None values
            if self.sensor3_mgrs_val != None and self.sensor3_grid_azimuth_val != None and self.sensor3_power_received_dBm_val != None:
                # calculate sensor 3 target coordinate
                self.sensor3_target_coord = [np.average([s3lnmc[0],s3lfmc[0]]),np.average([s3lnmc[1],s3lfmc[1]])]
                # calculate sensor 3 target MGRS
                sensor3_target_mgrs = convert_coords_to_mgrs(self.sensor3_target_coord)
                # calculate LOB 3 sensor error (in acres)
                self.sensor3_lob_error_acres = get_polygon_area(self.sensor3_lob_polygon)
                # define sensor 3 LOB description
                sensor3_lob_description = f"EWT 3 at {format_readable_mgrs(self.sensor3_mgrs_val)} with a LOB at bearing {int(self.sensor3_grid_azimuth_val)}° between {self._generate_sensor_distance_text(self.sensor3_min_distance_m)} and {self._generate_sensor_distance_text(self.sensor3_max_distance_m)} with {self.sensor3_lob_error_acres:,.0f} acres of error"
                # define and plot sensor 3 marker on the map
                self.plot_EWT(self.sensor3_coord,3,False)
                # define and set sensor 3 LOB area
                sensor3_lob = self.map_widget.set_polygon(
                    position_list=[(self.sensor3_coord[0],self.sensor3_coord[1]),(s3lfmc[0],s3lfmc[1])],
                    fill_color=App.DEFAULT_VALUES['LOB Fill Color'],
                    outline_color=App.DEFAULT_VALUES['LOB Center Line Color'],
                    border_width=App.DEFAULT_VALUES['Border Width'],
                    command=self.polygon_click,
                    data="LOB Line\n"+sensor3_lob_description)
                # add sensor 2 LOB area to polygon list
                self._append_object(sensor3_lob,"LOB")
                # define and set sensor 2 LOB area
                sensor3_lob_area = self.map_widget.set_polygon(
                    position_list=self.sensor3_lob_polygon,
                    fill_color=App.DEFAULT_VALUES['LOB Fill Color'],
                    outline_color=App.DEFAULT_VALUES['LOB Area Outline Color'],
                    border_width=App.DEFAULT_VALUES['Border Width'],
                    command=self.polygon_click,
                    data="LOB Area\n"+sensor3_lob_description)
                # add LOB area to polygon list
                self._append_object(sensor3_lob_area,"LOB")
                if plot_ewt3_lob_tgt_bool:
                    # define and set sensor 3 target marker
                    target3_marker = self.map_widget.set_marker(
                        deg_x=self.sensor3_target_coord[0], 
                        deg_y=self.sensor3_target_coord[1], 
                        text=f'{format_readable_mgrs(sensor3_target_mgrs)}', 
                        image_zoom_visibility=(10, float("inf")),
                        marker_color_circle='white',
                        icon=self.target_image_LOB,
                        command=self.marker_click,
                        data=f'TGT (LOB)\nEWT 3\n{format_readable_mgrs(sensor3_target_mgrs)}\nat {format_readable_DTG(generate_DTG())}')
                    # add sensor 3 target marker to target marker list
                    self._append_object(target3_marker,"TGT")
                # calculate sensor 3 distance to target 3
                self.sensor3_distance_val = int(get_distance_between_coords(self.sensor3_coord,self.sensor3_target_coord))
                self.sensor3_bearing_val = int(get_bearing_between_coordinates(self.sensor3_coord,self.sensor3_target_coord))
                # generate sensor 3 distance from target text       
                dist_sensor3_text = self._generate_sensor_distance_text(self.sensor3_distance_val,self.sensor3_bearing_val)
                # set sensor 3 distance field
                self.sensor3_distance.configure(text=dist_sensor3_text,text_color='white')
                # generate a 2D elevation plot
                if self.target_class == '(1 LOB)' and not self.bypass_elevation_plot_prompt:
                    from CTkMessagebox import CTkMessagebox
                    msgBox = CTkMessagebox(title="2D Elevation Plot", message="Do you want to generate a 2D Elevation Plot", icon='info',options=['Yes','No'])
                    response = msgBox.get()
                    if response == 'Yes': 
                        run_2D_elevation_plotter_threaded(self.sensor3_coord,self.sensor3_min_distance_km,self.sensor3_target_coord,self.sensor3_max_distance_km,callback=self._safe_plot_callback)
                        self.logger_gui.info(f"Attempting to create a 2D Elevation Plot for EWT 3 at {format_readable_mgrs(self.sensor3_mgrs_val)} with a LOB at bearing {int(self.sensor3_grid_azimuth_val)}° between {self._generate_sensor_distance_text(self.sensor3_min_distance_m)} and {self._generate_sensor_distance_text(self.sensor3_max_distance_m)}")
            else:
                sensor3_target_mgrs = None
                self.sensor3_lob_error_acres = None
                self.sensor3_target_coord = None
                self.sensor3_distance.configure(text="N/A",text_color='white')
            # calculate distance from EWT 1 to other EWT targets
            if self.sensor1_distance._text == "N/A" and self.sensor1_coord != None:
                if self.sensor2_target_coord != None:
                    self.sensor1_distance_val = int(get_distance_between_coords(self.sensor1_coord,self.sensor2_target_coord))
                    self.sensor1_bearing_val = int(get_bearing_between_coordinates(self.sensor1_coord,self.sensor2_target_coord))
                    dist_sensor1_text = self._generate_sensor_distance_text(self.sensor1_distance_val,self.sensor1_bearing_val)
                    self.sensor1_distance.configure(text=dist_sensor1_text,text_color='white')
                if self.sensor3_target_coord != None:
                    self.sensor1_distance_val = int(get_distance_between_coords(self.sensor1_coord,self.sensor3_target_coord))
                    dist_sensor1_text = self._generate_sensor_distance_text(self.sensor1_distance_val)
                    self.sensor1_distance.configure(text=dist_sensor1_text,text_color='white')
            # calculate distance from EWT 2 to other EWT targets
            if self.sensor2_distance._text == "N/A" and self.sensor2_coord != None:
                if self.sensor1_target_coord != None:
                    self.sensor2_distance_val = int(get_distance_between_coords(self.sensor2_coord,self.sensor1_target_coord))
                    self.sensor2_bearing_val = int(get_bearing_between_coordinates(self.sensor2_coord,self.sensor1_target_coord))
                    dist_sensor2_text = self._generate_sensor_distance_text(self.sensor2_distance_val,self.sensor2_bearing_val)
                    self.sensor2_distance.configure(text=dist_sensor2_text,text_color='white')
                if self.sensor3_target_coord != None:
                    self.sensor2_distance_val = int(get_distance_between_coords(self.sensor2_coord,self.sensor3_target_coord))
                    self.sensor2_bearing_val = int(get_bearing_between_coordinates(self.sensor2_coord,self.sensor3_target_coord))
                    dist_sensor2_text = self._generate_sensor_distance_text(self.sensor2_distance_val,self.sensor2_bearing_val)
                    self.sensor2_distance.configure(text=dist_sensor2_text,text_color='white')
            # calculate distance from EWT 3 to other EWT targets
            if self.sensor3_distance._text == "N/A" and self.sensor3_coord != None:
                if self.sensor2_target_coord != None:
                    self.sensor3_distance_val = int(get_distance_between_coords(self.sensor3_coord,self.sensor2_target_coord))
                    self.sensor3_bearing_val = int(get_bearing_between_coordinates(self.sensor3_coord,self.sensor2_target_coord))
                    dist_sensor3_text = self._generate_sensor_distance_text(self.sensor3_distance_val,self.sensor3_bearing_val)
                    self.sensor3_distance.configure(text=dist_sensor3_text,text_color='white')
                if self.sensor1_target_coord != None:
                    self.sensor3_distance_val = int(get_distance_between_coords(self.sensor3_coord,self.sensor1_target_coord))
                    self.sensor3_bearing_val = int(get_bearing_between_coordinates(self.sensor3_coord,self.sensor1_target_coord))
                    dist_sensor3_text = self._generate_sensor_distance_text(self.sensor3_distance_val,self.sensor3_bearing_val)
                    self.sensor3_distance.configure(text=dist_sensor3_text,text_color='white')
    
        def plot_cut(l1c,l1r,l1l,l2c,l2r,l2l,multi_cut_bool=False,plot_cut_tgts=True):
            """
            Detect intersection between lob bounds and other lob's far bound, choose the four closes points for cut polygon'
            """
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
            '''
            Assess if the backstops of LOBs intersect with LOB left-right bounds, need to know which LOBs are being assessed
            '''
            
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
            self._append_object(cut_area,"CUT")
            # calculate distance from sensor 1 and CUT intersection (in meters)
            if self.sensor1_mgrs_val != None: 
                self.sensor1_distance_val = int(get_distance_between_coords(self.sensor1_coord,self.target_coord))
                self.sensor1_bearing_val = int(get_bearing_between_coordinates(self.sensor1_coord,self.target_coord))
            # calculate distance from sensor 2 and CUT intersection (in meters)
            if self.sensor2_mgrs_val != None: 
                self.sensor2_distance_val = int(get_distance_between_coords(self.sensor2_coord,self.target_coord))
                self.sensor2_bearing_val = int(get_bearing_between_coordinates(self.sensor2_coord,self.target_coord))
            # define and set the CUT target marker
            if self.sensor3_mgrs_val != None: 
                self.sensor3_distance_val = int(get_distance_between_coords(self.sensor3_coord,self.target_coord))
                self.sensor3_bearing_val = int(get_bearing_between_coordinates(self.sensor3_coord,self.target_coord))
            if plot_cut_tgts:
                # define and set the CUT target marker
                cut_target_marker = self.map_widget.set_marker(
                    deg_x=self.target_coord[0], 
                    deg_y=self.target_coord[1], 
                    text=f'{format_readable_mgrs(self.target_mgrs)}',
                    image_zoom_visibility=(10, float("inf")),
                    marker_color_circle='white',
                    icon=self.target_image_CUT,
                    command=self.marker_click,
                    data=f'TGT (CUT)\n{format_readable_mgrs(self.target_mgrs)}\nat {format_readable_DTG(generate_DTG())}')
                # add CUT marker to target marker list
                self._append_object(cut_target_marker,"TGT")
            # generate sensor 1 distance from target text     
            if self.sensor1_mgrs_val != None: 
                # generate sensor 1 distance from target text
                dist_sensor1_text = self._generate_sensor_distance_text(self.sensor1_distance_val,self.sensor1_bearing_val)
                # set sensor 1 distance field
                if self.sensor1_distance.cget("text") != '' and multi_cut_bool:
                    if self.sensor1_distance.cget("text") > dist_sensor1_text:
                        self.sensor1_distance.configure(text=dist_sensor1_text,text_color='white')
                else:
                    self.sensor1_distance.configure(text=dist_sensor1_text,text_color='white')
            if self.sensor2_mgrs_val != None: 
                # generate sensor 2 distance from target text
                dist_sensor2_text = self._generate_sensor_distance_text(self.sensor2_distance_val,self.sensor2_bearing_val)
                # set sensor 2 distance field
                if self.sensor2_distance.cget("text") != '' and multi_cut_bool:
                    if self.sensor2_distance.cget("text") > dist_sensor2_text:
                        self.sensor2_distance.configure(text=dist_sensor2_text,text_color='white')
                else:
                    self.sensor2_distance.configure(text=dist_sensor2_text,text_color='white')
            if self.sensor3_mgrs_val != None:
                # generate sensor 3 distance from target text
                dist_sensor3_text = self._generate_sensor_distance_text(self.sensor3_distance_val,self.sensor3_bearing_val)
                # set sensor 3 distance field
                if self.sensor3_distance.cget("text") != '' and multi_cut_bool:
                    if self.sensor3_distance.cget("text") > dist_sensor3_text:
                        self.sensor3_distance.configure(text=dist_sensor3_text,text_color='white')
                else:
                    self.sensor3_distance.configure(text=dist_sensor3_text,text_color='white')
                        # calculate distance from EWT 1 to other EWT targets
            # set EWT distance of EWTs without target data
            if self.sensor1_distance._text == "N/A" and self.sensor1_coord != None:
                self.sensor1_distance_val = int(get_distance_between_coords(self.sensor1_coord,self.target_coord))
                self.sensor1_bearing_val = int(get_bearing_between_coordinates(self.sensor1_coord,self.target_coord))
                dist_sensor1_text = self._generate_sensor_distance_text(self.sensor1_distance_val,self.sensor1_bearing_val)
                self.sensor1_distance.configure(text=dist_sensor1_text,text_color='white')
            if self.sensor2_distance._text == "N/A" and self.sensor2_coord != None:
                self.sensor2_distance_val = int(get_distance_between_coords(self.sensor2_coord,self.target_coord))
                self.sensor2_bearing_val = int(get_bearing_between_coordinates(self.sensor2_coord,self.target_coord))
                dist_sensor2_text = self._generate_sensor_distance_text(self.sensor2_distance_val,self.sensor2_bearing_val)
                self.sensor2_distance.configure(text=dist_sensor2_text,text_color='white')
            if self.sensor3_distance._text == "N/A" and self.sensor3_coord != None:
                self.sensor3_distance_val = int(get_distance_between_coords(self.sensor3_coord,self.target_coord))
                self.sensor3_bearing_val = int(get_bearing_between_coordinates(self.sensor3_coord,self.target_coord))
                dist_sensor3_text = self._generate_sensor_distance_text(self.sensor3_distance_val,self.sensor3_bearing_val)
                self.sensor3_distance.configure(text=dist_sensor3_text,text_color='white')
            # set target grid field with CUT center MGRS
            if multi_cut_bool: self.target_grid.configure(text="MULTIPLE CUTS")
            if not multi_cut_bool: self.target_grid.configure(text=f'{format_readable_mgrs(self.target_mgrs)}',text_color='yellow')
            # set target error field
            if multi_cut_bool: self.target_error.configure(text="MULTIPLE CUTS")
            if not multi_cut_bool: self.target_error.configure(text=f'{self.target_error_val:,.0f} acres',text_color='white')
            # set map position at CUT target 
            self.map_widget.set_position(self.target_coord[0],self.target_coord[1])
            
        def plot_fix(lob1_center,lob1_right_bound,lob1_left_bound,lob2_center,lob2_right_bound,lob2_left_bound,lob3_center,lob3_right_bound,lob3_left_bound):
            """
            Still having issues of inconsistency with some assessments of FIX space
            incorporating alt method as temp solution
            """
            
            from coords import adjust_coordinate, get_bearing_between_coordinates
            # get intersection of LOB 1 & LOB 2 right-bound errors
            intersection_l1r_l2r = get_intersection(lob1_right_bound, lob2_right_bound)
            # get intersection of LOB 1 right-bound error and LOB 2 left-bound error
            intersection_l1r_l2l = get_intersection(lob1_right_bound, lob2_left_bound)
            # get intersection of LOB 1 left-bound error and LOB 2 right-bound error
            intersection_l1l_l2r = get_intersection(lob1_left_bound, lob2_right_bound)
            # get intersection of LOB 1 & LOB 2 left-bound errors 
            intersection_l1l_l2l = get_intersection(lob1_left_bound, lob2_left_bound)
            # define LOB 1 & LOB 2 CUT polygon
            cut12_polygon = [intersection_l1r_l2r,intersection_l1r_l2l,intersection_l1l_l2r,intersection_l1l_l2l]
            # get intersection of LOB 1 & LOB 3 right-bound errors
            intersection_l1r_l3r = get_intersection(lob1_right_bound, lob3_right_bound)
            # get intersection of LOB 1 right-bound error and LOB 3 left-bound error
            intersection_l1r_l3l = get_intersection(lob1_right_bound, lob3_left_bound)
            # get intersection of LOB 1 left-bound error and LOB 3 right-bound error
            intersection_l1l_l3r = get_intersection(lob1_left_bound, lob3_right_bound)
            # get intersection of LOB 1 & LOB 3 left-bound errors 
            intersection_l1l_l3l = get_intersection(lob1_left_bound, lob3_left_bound)
            # define LOB 1 & LOB 3 CUT polygon
            cut13_polygon = [intersection_l1r_l3r,intersection_l1r_l3l,intersection_l1l_l3r,intersection_l1l_l3l]
            # get intersection of LOB 2 & LOB 3 right-bound errors
            intersection_l2r_l3r = get_intersection(lob2_right_bound, lob3_right_bound)
            # get intersection of LOB 2 right-bound error and LOB 3 left-bound error
            intersection_l2r_l3l = get_intersection(lob2_right_bound, lob3_left_bound)
            # get intersection of LOB 2 left-bound error and LOB 3 right-bound error
            intersection_l2l_l3r = get_intersection(lob2_left_bound, lob3_right_bound)
            # get intersection of LOB 2 & LOB 3 left-bound errors 
            intersection_l2l_l3l = get_intersection(lob2_left_bound, lob3_left_bound)
            # define LOB 2 & LOB 3 CUT polygon
            cut23_polygon = [intersection_l2r_l3r,intersection_l2r_l3l,intersection_l2l_l3r,intersection_l2l_l3l]
            # define candidate points
            points_unadjusted = list(list(cut12_polygon) + list(cut13_polygon) + list(cut23_polygon))
            # points.append([35.3336198, -116.5212675])
            center_point = get_center_coord(points_unadjusted)
            fix_buffer_adjustment_m = 5
            points = [adjust_coordinate(p,get_bearing_between_coordinates(p,center_point),fix_buffer_adjustment_m) for p in points_unadjusted]           
            # organize LOB 1 & LOB 2 CUT polygon
            cut12_polygon = organize_polygon_coords(cut12_polygon)
            # organize LOB 1 & LOB 3 CUT polygon
            cut13_polygon = organize_polygon_coords(cut13_polygon)
            # organize LOB 2 & LOB 3 CUT polygon
            cut23_polygon = organize_polygon_coords(cut23_polygon) 
            # define polygons
            polygons = [cut12_polygon,cut13_polygon,cut23_polygon]
            # polygons = [self.sensor1_lob_polygon,self.sensor2_lob_polygon,self.sensor3_lob_polygon]
            # define FIX coords list
            fix_polygon = []
            # loop through all CUT intersection points
            for index_point, point in enumerate(points):
                # set polygon boolean value to TRUE
                in_polygon_bool = True
                # loop through all CUT polygons
                for index_polygon, poly in enumerate(polygons):
                    # assess if the point is in the polygon
                    output = check_if_point_in_polygon(point,poly)
                    if output == 0 or output == False:
                        # set polygon boolean value to FALSE
                        in_polygon_bool = False
                        # end polygon loop
                        break
                # if point is in all CUT polygons
                if in_polygon_bool:
                    # append point as a fix coordinate
                    fix_polygon.append(point)
                else:
                    pass
                in_polygon_bool = True
            if len(fix_polygon) == 0:
                # plot cuts with the CUT target icon
                plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob2_center,lob2_right_bound,lob2_left_bound,True,True)
                plot_cut(lob2_center,lob2_right_bound,lob2_left_bound,lob3_center,lob3_right_bound,lob3_left_bound,True,True)
                plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob3_center,lob3_right_bound,lob3_left_bound,True,True)
                return
            # organize fix coordinates
            fix_polygon = organize_polygon_coords(fix_polygon)
            # assess if the fix polygon is not a polygon
            if len(fix_polygon) < 3:
                # alternate method of determining fix
                int_13 = get_intersection(lob1_center, lob3_center)
                int_12 = get_intersection(lob1_center, lob2_center)
                int_23 = get_intersection(lob2_center, lob3_center)
                fix_polygon = [int_12,int_23,int_13]
                # plot cuts with the CUT target icon
                plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob2_center,lob2_right_bound,lob2_left_bound,True,True)
                plot_cut(lob2_center,lob2_right_bound,lob2_left_bound,lob3_center,lob3_right_bound,lob3_left_bound,True,True)
                plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob3_center,lob3_right_bound,lob3_left_bound,True,True)
            else:
                # plot cuts without the CUT target icon
                plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob2_center,lob2_right_bound,lob2_left_bound,True,False)
                plot_cut(lob2_center,lob2_right_bound,lob2_left_bound,lob3_center,lob3_right_bound,lob3_left_bound,True,False)
                plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob3_center,lob3_right_bound,lob3_left_bound,True,False)
            # define target classification
            self.target_class = '(FIX)'
            # set target label with updated target classification
            self.label_target_grid.configure(text=f'TARGET GRID {self.target_class}'.strip(),text_color='red')
            fix_coord = get_center_coord(fix_polygon)
            self.target_coord = fix_coord
            self.target_mgrs = convert_coords_to_mgrs(self.target_coord)
            self.sensor1_distance_val = int(get_distance_between_coords(self.sensor1_coord,self.target_coord))
            self.sensor1_bearing_val = int(get_bearing_between_coordinates(self.sensor1_coord,self.target_coord))
            self.sensor2_distance_val = int(get_distance_between_coords(self.sensor2_coord,self.target_coord))
            self.sensor2_bearing_val = int(get_bearing_between_coordinates(self.sensor2_coord,self.target_coord))
            self.sensor3_distance_val = int(get_distance_between_coords(self.sensor3_coord,self.target_coord))
            self.sensor3_bearing_val = int(get_bearing_between_coordinates(self.sensor3_coord,self.target_coord))
            self.target_error_val = get_polygon_area(fix_polygon)
            fix_description = f"Target FIX at {format_readable_mgrs(self.target_mgrs)} with {self.target_error_val:,.0f} acres of error"
            fix_target_marker = self.map_widget.set_marker(
                deg_x=self.target_coord[0], 
                deg_y=self.target_coord[1],
                text=f'{format_readable_mgrs(self.target_mgrs)}',
                image_zoom_visibility=(10, float("inf")),
                marker_color_circle='white',
                icon=self.target_image_FIX,
                command=self.marker_click,
                data=f'TGT {self.target_class}\n{format_readable_mgrs(self.target_mgrs)}\nat {format_readable_DTG(generate_DTG())}')
            # add FIX marker to target marker list
            self._append_object(fix_target_marker,"TGT")
            # generate sensor 1 distance from target text     
            dist_sensor1_text = self._generate_sensor_distance_text(self.sensor1_distance_val,self.sensor1_bearing_val)
            # set sensor 1 distance field
            self.sensor1_distance.configure(text=dist_sensor1_text,text_color='white')
            # generate sensor 2 distance from target text       
            dist_sensor2_text = self._generate_sensor_distance_text(self.sensor2_distance_val,self.sensor2_bearing_val)
            # set sensor 2 distance field
            self.sensor2_distance.configure(text=dist_sensor2_text,text_color='white')
            # set target grid field with CUT center MGRS
            dist_sensor3_text = self._generate_sensor_distance_text(self.sensor3_distance_val,self.sensor3_bearing_val)
            # set sensor 2 distance field
            self.sensor3_distance.configure(text=dist_sensor3_text,text_color='white')
            # set target grid field with CUT center MGRS
            self.target_grid.configure(text=f'{format_readable_mgrs(self.target_mgrs)}',text_color='yellow')
            # set target error field
            self.target_error.configure(text=f'{self.target_error_val:,.0f} acres',text_color='white')
            # set map position at CUT target 
            self.map_widget.set_position(self.target_coord[0],self.target_coord[1])
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
            self._append_object(fix_area,"FIX")
            # set EWT distance of EWTs without target data
            if self.sensor1_distance._text == "N/A" and self.sensor1_coord != None:
                self.sensor1_distance_val = int(get_distance_between_coords(self.sensor1_coord,self.target_coord))
                self.sensor1_bearing_val = int(get_bearing_between_coordinates(self.sensor1_coord,self.target_coord))
                dist_sensor1_text = self._generate_sensor_distance_text(self.sensor1_distance_val,self.sensor1_bearing_val)
                self.sensor1_distance.configure(text=dist_sensor1_text,text_color='white')
            if self.sensor2_distance._text == "N/A" and self.sensor2_coord != None:
                self.sensor2_distance_val = int(get_distance_between_coords(self.sensor2_coord,self.target_coord))
                self.sensor2_bearing_val = int(get_bearing_between_coordinates(self.sensor2_coord,self.target_coord))
                dist_sensor2_text = self._generate_sensor_distance_text(self.sensor2_distance_val,self.sensor2_bearing_val)
                self.sensor2_distance.configure(text=dist_sensor2_text,text_color='white')
            if self.sensor3_distance._text == "N/A" and self.sensor3_coord != None:
                self.sensor3_distance_val = int(get_distance_between_coords(self.sensor3_coord,self.target_coord))
                self.sensor3_bearing_val = int(get_bearing_between_coordinates(self.sensor3_coord,self.target_coord))
                dist_sensor3_text = self._generate_sensor_distance_text(self.sensor3_distance_val,self.sensor3_bearing_val)
                self.sensor3_distance.configure(text=dist_sensor3_text,text_color='white')
        # reset fields to defaults
        self.label_target_grid.configure(text='')
        self.target_grid.configure(text='')
        self.sensor1_distance.configure(text='')
        self.sensor2_distance.configure(text='')
        self.sensor3_distance.configure(text='')
        self.target_error.configure(text='')
        self.target_class = ''; self.target_coord = None; self.target_mgrs = None
        self.sensor1_distance_val = None; self.sensor2_distance_val = None; self.sensor3_distance_val = None
        self.sensor1_bearing_val = None; self.sensor2_bearing_val = None; self.sensor3_bearing_val = None
        sensor1_lob_near_middle_coord = None; sensor2_lob_near_middle_coord = None; sensor3_lob_near_middle_coord = None
        sensor1_lob_far_middle_coord = None; sensor2_lob_far_middle_coord = None; sensor3_lob_far_middle_coord = None
        # read the user input fields
        self.read_ewt_input_fields()
        # end function if there is no ewt data
        if self.sensor1_mgrs_val == None and self.sensor2_mgrs_val == None and self.sensor3_mgrs_val == None: return
        # end function if not all data fields were input
        if self.frequency_MHz_val == None or self.min_wattage_val == None or self.max_wattage_val == None: return
        # if sensor 1 has non-None input values
        if self.sensor1_mgrs_val != None and self.sensor1_grid_azimuth_val != None and self.sensor1_power_received_dBm_val != None:
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
            self.sensor1_lob_polygon = [sensor1_lob_near_right_coord,sensor1_lob_far_right_coord,sensor1_lob_far_left_coord,sensor1_lob_near_left_coord]
            # organize sensor 1 LOB polygon points
            self.sensor1_lob_polygon = organize_polygon_coords(self.sensor1_lob_polygon)
            # define sensor 1 LOB backstop Line
            self.sensor1_lob_backstop = get_line(sensor1_lob_far_right_coord,sensor1_lob_far_left_coord)
            # define sensor 1 LOB's center line
            lob1_center = get_line(self.sensor1_coord, sensor1_lob_far_middle_coord)
            # define sensor 1 LOB's right-bound error line
            lob1_right_bound = get_line(sensor1_lob_near_right_coord, sensor1_lob_far_right_coord)
            # define sensor 1 LOB's left-bound error line
            lob1_left_bound = get_line(sensor1_lob_near_left_coord, sensor1_lob_far_left_coord)
        # if sensor 1 has None input values
        else:
            # set sensor 1 input values to None
            self.sensor1_grid_azimuth_val = None; self.sensor1_power_received_dBm_val = None; self.sensor1_lob_polygon = None; self.sensor1_lob_backstop = None
        # if sensor 2 has non-None input values
        if self.sensor2_mgrs_val != None and self.sensor2_grid_azimuth_val != None and self.sensor2_power_received_dBm_val != None:
            # convert sensor 2 MGRS to coordinates
            self.sensor2_coord = convert_mgrs_to_coords(self.sensor2_mgrs_val)
            # # set map position to the middle of sensor 1 and sensor 2
            # self.map_widget.set_position(np.average([self.sensor1_coord[0],self.sensor2_coord[0]]),np.average([self.sensor1_coord[1],self.sensor2_coord[1]]))
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
            self.sensor2_lob_polygon = [sensor2_lob_near_right_coord,sensor2_lob_far_right_coord,sensor2_lob_far_left_coord,sensor2_lob_near_left_coord]
            # organize sensor 2 LOB polygon
            self.sensor2_lob_polygon = organize_polygon_coords(self.sensor2_lob_polygon)
            # define sensor 2 LOB backstop Line
            self.sensor2_lob_backstop = get_line(sensor2_lob_far_right_coord,sensor2_lob_far_left_coord)
            # define sensor 2 LOB center-line
            lob2_center = get_line(self.sensor2_coord, sensor2_lob_far_middle_coord)
            # define sensor 2 LOB right-bound error line
            lob2_right_bound = get_line(sensor2_lob_near_right_coord, sensor2_lob_far_right_coord)
            # define sensor 2 LOB left-bound error line
            lob2_left_bound = get_line(sensor2_lob_near_left_coord, sensor2_lob_far_left_coord)
        # if sensor 2 has None input values
        else:
            # set sensor 2 input values to None
            self.sensor2_grid_azimuth_val = None; self.sensor2_power_received_dBm_val = None; self.sensor2_lob_polygon = None; self.sensor2_lob_backstop = None
        # if sensor 3 has non-None input values 
        if self.sensor3_mgrs_val != None and self.sensor3_grid_azimuth_val != None and self.sensor3_power_received_dBm_val != None:
            # convert sensor 3 MGRS to coordinates
            self.sensor3_coord = convert_mgrs_to_coords(self.sensor3_mgrs_val)
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
            self.sensor3_lob_polygon = [sensor3_lob_near_right_coord,sensor3_lob_far_right_coord,sensor3_lob_far_left_coord,sensor3_lob_near_left_coord]
            # organize sensor 3 LOB polygon
            self.sensor3_lob_polygon = organize_polygon_coords(self.sensor3_lob_polygon)
            # define sensor 3 LOB backstop Line
            self.sensor3_lob_backstop = get_line(sensor3_lob_far_right_coord,sensor3_lob_far_left_coord)
            # define sensor 3 LOB center-line
            lob3_center = get_line(self.sensor3_coord, sensor3_lob_far_middle_coord)
            # define sensor 3 LOB right-bound error line
            lob3_right_bound = get_line(sensor3_lob_near_right_coord, sensor3_lob_far_right_coord)
            # define sensor 3 LOB left-bound error line
            lob3_left_bound = get_line(sensor3_lob_near_left_coord, sensor3_lob_far_left_coord)
        # if sensor 3 has None input values
        else:
            # set sensor 3 input values to None
            self.sensor3_grid_azimuth_val = None; self.sensor3_power_received_dBm_val = None; self.sensor3_lob_polygon = None; self.sensor3_lob_backstop = None
        # assess which LOBs have intersections
        ewt1_ewt2_intersection_bool = check_for_intersection(self.sensor1_coord,sensor1_lob_far_middle_coord,self.sensor2_coord,sensor2_lob_far_middle_coord)
        ewt2_ewt3_intersection_bool = check_for_intersection(self.sensor2_coord,sensor2_lob_far_middle_coord,self.sensor3_coord,sensor3_lob_far_middle_coord)
        ewt1_ewt3_intersection_bool = check_for_intersection(self.sensor1_coord,sensor1_lob_far_middle_coord,self.sensor3_coord,sensor3_lob_far_middle_coord)
        # EWT 1 & 2 CUT, EWT 3 LOB (TOTAL 1 CUT, 1 LOB)
        if ewt1_ewt2_intersection_bool and not ewt2_ewt3_intersection_bool and not ewt1_ewt3_intersection_bool:
            plot_lobs(sensor1_lob_near_middle_coord,sensor1_lob_far_middle_coord,sensor2_lob_near_middle_coord,sensor2_lob_far_middle_coord,sensor3_lob_near_middle_coord,sensor3_lob_far_middle_coord,False,False,True)
            plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob2_center,lob2_right_bound,lob2_left_bound)
        # EWT 2 & 3 CUT, EWT 1 LOB (TOTAL 1 CUT, 1 LOB)
        elif not ewt1_ewt2_intersection_bool and ewt2_ewt3_intersection_bool and not ewt1_ewt3_intersection_bool:
            plot_lobs(sensor1_lob_near_middle_coord,sensor1_lob_far_middle_coord,sensor2_lob_near_middle_coord,sensor2_lob_far_middle_coord,sensor3_lob_near_middle_coord,sensor3_lob_far_middle_coord,True,False,False)
            plot_cut(lob2_center,lob2_right_bound,lob2_left_bound,lob3_center,lob3_right_bound,lob3_left_bound)
        # EWT 1 & 3 CUT, EWT 2 LOB (TOTAL 1 CUT, 1 LOB)
        elif not ewt1_ewt2_intersection_bool and not ewt2_ewt3_intersection_bool and ewt1_ewt3_intersection_bool:
            plot_lobs(sensor1_lob_near_middle_coord,sensor1_lob_far_middle_coord,sensor2_lob_near_middle_coord,sensor2_lob_far_middle_coord,sensor3_lob_near_middle_coord,sensor3_lob_far_middle_coord,False,True,False)
            plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob3_center,lob3_right_bound,lob3_left_bound)
        # EWT 1 & 2 CUT, EWT 2 & 3 NO CUT, EWT 1 & 3 CUT (TOTAL 2 CUT)
        elif ewt1_ewt2_intersection_bool and not ewt2_ewt3_intersection_bool and ewt1_ewt3_intersection_bool:
            plot_lobs(sensor1_lob_near_middle_coord,sensor1_lob_far_middle_coord,sensor2_lob_near_middle_coord,sensor2_lob_far_middle_coord,sensor3_lob_near_middle_coord,sensor3_lob_far_middle_coord,False,False,False)
            plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob2_center,lob2_right_bound,lob2_left_bound,True,True)
            plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob3_center,lob3_right_bound,lob3_left_bound,True,True)
        # EWT 1 & 2 CUT, EWT 2 & 3 CUT, EWT 1 & 3 NO CUT (TOTAL 2 CUT)
        elif ewt1_ewt2_intersection_bool and ewt2_ewt3_intersection_bool and not ewt1_ewt3_intersection_bool:
            plot_lobs(sensor1_lob_near_middle_coord,sensor1_lob_far_middle_coord,sensor2_lob_near_middle_coord,sensor2_lob_far_middle_coord,sensor3_lob_near_middle_coord,sensor3_lob_far_middle_coord,False,False,False)
            plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob2_center,lob2_right_bound,lob2_left_bound,True,True)
            plot_cut(lob2_center,lob2_right_bound,lob2_left_bound,lob3_center,lob3_right_bound,lob3_left_bound,True,True) 
        # EWT 1 & 2 NO CUT, EWT 2 & 3 CUT, EWT 1 & 3 CUT (TOTAL 2 CUT)
        elif not ewt1_ewt2_intersection_bool and ewt2_ewt3_intersection_bool and ewt1_ewt3_intersection_bool:
            plot_lobs(sensor1_lob_near_middle_coord,sensor1_lob_far_middle_coord,sensor2_lob_near_middle_coord,sensor2_lob_far_middle_coord,sensor3_lob_near_middle_coord,sensor3_lob_far_middle_coord,False,False,False)
            plot_cut(lob2_center,lob2_right_bound,lob2_left_bound,lob3_center,lob3_right_bound,lob3_left_bound,True,True)
            plot_cut(lob1_center,lob1_right_bound,lob1_left_bound,lob3_center,lob3_right_bound,lob3_left_bound,True,True)
        # No intersections between an EWT LOBs
        elif not ewt1_ewt2_intersection_bool and not ewt2_ewt3_intersection_bool and not ewt1_ewt3_intersection_bool:
            plot_lobs(sensor1_lob_near_middle_coord,sensor1_lob_far_middle_coord,sensor2_lob_near_middle_coord,sensor2_lob_far_middle_coord,sensor3_lob_near_middle_coord,sensor3_lob_far_middle_coord,True,True,True)
            pass
        # EWT 1, 2, & 3 INTERSECTION (TOTAL 1 FIX, 3 CUT)
        elif ewt1_ewt2_intersection_bool and ewt2_ewt3_intersection_bool and ewt1_ewt3_intersection_bool:
            plot_lobs(sensor1_lob_near_middle_coord,sensor1_lob_far_middle_coord,sensor2_lob_near_middle_coord,sensor2_lob_far_middle_coord,sensor3_lob_near_middle_coord,sensor3_lob_far_middle_coord,False,False,False)
            plot_fix(lob1_center,lob1_right_bound,lob1_left_bound,lob2_center,lob2_right_bound,lob2_left_bound,lob3_center,lob3_right_bound,lob3_left_bound)
        # Unexpected situation
        else:
            self.logger_gui.error(f"Unexpected situation with EWTs: {self.sensor1_mgrs_val}, {self.sensor2_mgrs_val}, {self.sensor3_mgrs_val}")
        self.set_target_field()
      
    def log_target_data(self) -> None:
        from utilities import generate_DTG
        from coords import convert_coords_to_mgrs
        """Logs current input fields and targeting data in a date-specific csv file."""        
        import datetime
        from utilities import read_csv, write_csv
        # define log columns
        log_columns = ['DTG_LOCAL','FREQ_MHz','MIN_ERP_W','MAX_ERP_W','PATH_LOSS_COEFF',
                       'TGT_CLASS','TGT_MGRS','TGT_LATLON','TGT_ERROR_ACRES',
                       'EWT_1_MGRS','EWT_1_LATLON','EWT_1_LOB_DEGREES','EWT_1_PWR_REC_DbM','EWT_1_LOB_TGT_MGRS','EWT_1_LOB_TGT_LATLON','EWT_1_DIST2TGT_KM','EWT_1_MIN_DIST_KM','EWT_1_MAX_DIST_KM',
                       'EWT_2_MGRS','EWT_2_LATLON','EWT_2_LOB_DEGREES','EWT_2_PWR_REC_DbM','EWT_2_LOB_TGT_MGRS','EWT_2_LOB_TGT_LATLON','EWT_2_DIST2TGT_KM','EWT_2_MIN_DIST_KM','EWT_2_MAX_DIST_KM',
                       'EWT_3_MGRS','EWT_3_LATLON','EWT_3_LOB_DEGREES','EWT_3_PWR_REC_DbM','EWT_3_LOB_TGT_MGRS','EWT_3_LOB_TGT_LATLON','EWT_3_DIST2TGT_KM','EWT_3_MIN_DIST_KM','EWT_3_MAX_DIST_KM',
                       'TGT_MGRS_ACTUAL']
        num_ewt_datapoints = 9
        ewt_bool = False
        # assess if directory exists
        if not os.path.exists(self.log_targeting_directory):
            # create log directory
            os.makedirs(self.log_targeting_directory)
            self.logger_gui.info(f"Created directory: {self.log_targeting_directory}")
        # define log file name
        filename = f"EW-targeting-log-{str(datetime.datetime.today()).split()[0]}.csv"
        # if log file already exists
        if os.path.isfile(os.path.join(self.log_targeting_directory, filename)):
            # read current log file
            log_data = read_csv(os.path.join(self.log_targeting_directory, filename))
        # if log file does not yet exist
        else:
            # create log file DataFrame
            log_data = []
        # initilize log entry
        row_data = []
        # add DTG to log entry
        dtg = generate_DTG()
        row_data.append(dtg)
        # if there is target data
        try:
            if self.frequency_MHz_val != None and self.min_wattage_val != None and self.max_wattage_val != None and self.path_loss_coeff_val != None and self.target_mgrs != None and self.target_coord != None and self.target_error_val != None:
                row_data.append(f'{self.frequency_MHz_val:,.2f}')
                row_data.append(f'{self.min_wattage_val:,.3f}')
                row_data.append(f'{self.max_wattage_val:,.3f}')
                row_data.append(self.path_loss_coeff_val)
                row_data.append(self.target_class.split('(')[-1].split(')')[0])
                if row_data[-1] == '2 LOBs' or row_data[-1] == '3 LOBs':
                    row_data.append(self.target_mgrs)
                    row_data.append(self.target_coord)
                    row_data.append(self.target_error_val)
                else:
                    row_data.append(self.target_mgrs)
                    if isinstance(self.target_coord,list):
                        row_data.append(', '.join([str(x) for x in self.target_coord]))
                    elif isinstance(self.target_coord,str):
                        row_data.append(self.target_coord)
                    row_data.append(f'{self.target_error_val:,.2f}')
            # if there is not target data or transmission data
            else:
                # end function w/o logging
                self.logger_gui.warning("Missing required targeting and input data. No data logged.")
                self._show_info("No target data. No data logged.",icon='warning')
                return
        except AttributeError:
            # end function w/o logging
            self.logger_gui.warning("Missing required targeting and input data. No data logged.")
            self._show_info("Missing required data. No data logged.",icon='warning')
            return
        # if sensor 1 has data in the input fields
        if self.sensor1_grid_azimuth_val != None:
            row_data.append(self.sensor1_mgrs_val)
            row_data.append(', '.join([str(x) for x in self.sensor1_coord]))
            row_data.append(self.sensor1_grid_azimuth_val)
            row_data.append(self.sensor1_power_received_dBm_val)
            row_data.append(convert_coords_to_mgrs(self.sensor1_target_coord))
            row_data.append(', '.join([str(x) for x in self.sensor1_target_coord]))
            row_data.append(f'{self.sensor1_distance_val/1000:,.2f}')
            row_data.append(f'{self.sensor1_min_distance_km:,.2f}')
            row_data.append(f'{self.sensor1_max_distance_km:,.2f}')
            
            ewt_bool = True
        # if sensor 1 has no data in the input fields
        else:
            diff = 0
            # add blank entries to sensor 1 data log
            if self.sensor1_mgrs_val != None:
                row_data.append(self.sensor1_mgrs_val)
                row_data.append(', '.join([str(x) for x in self.sensor1_coord]))
                diff += 2
                if self.sensor1_distance._text != 'N/A':
                    for i in range(4): row_data.append('')
                    row_data.append(f'{self.sensor1_distance_val/1000:,.2f}')
                    diff += 5
            # add blank entries to sensor 2 data log
            for i in range(num_ewt_datapoints-diff): row_data.append('')
        # if sensor 2 has data in the input fields
        if self.sensor2_grid_azimuth_val != None:
            row_data.append(self.sensor2_mgrs_val)
            row_data.append(', '.join([str(x) for x in self.sensor2_coord]))
            row_data.append(self.sensor2_grid_azimuth_val)
            row_data.append(self.sensor2_power_received_dBm_val)
            row_data.append(convert_coords_to_mgrs(self.sensor2_target_coord))
            row_data.append(', '.join([str(x) for x in self.sensor2_target_coord]))
            row_data.append(f'{self.sensor2_distance_val/1000:,.2f}')
            row_data.append(f'{self.sensor2_min_distance_km:,.2f}')
            row_data.append(f'{self.sensor2_max_distance_km:,.2f}')
            ewt_bool = True
        # if sensor 2 has no data in the input fields
        else:
            diff = 0
            # add blank entries to sensor 2 data log
            if self.sensor2_mgrs_val != None:
                row_data.append(self.sensor2_mgrs_val)
                row_data.append(', '.join([str(x) for x in self.sensor2_coord]))
                diff += 2
                if self.sensor2_distance._text != 'N/A':
                    for i in range(4): row_data.append('')
                    row_data.append(f'{self.sensor2_distance_val/1000:,.2f}')
                    diff += 5
            for i in range(num_ewt_datapoints-diff): row_data.append('')
        # if sensor 2 has data in the input fields
        if self.sensor3_grid_azimuth_val != None:
            row_data.append(self.sensor3_mgrs_val)
            row_data.append(', '.join([str(x) for x in self.sensor3_coord]))
            row_data.append(self.sensor3_grid_azimuth_val)
            row_data.append(self.sensor3_power_received_dBm_val)
            row_data.append(convert_coords_to_mgrs(self.sensor3_target_coord))
            row_data.append(', '.join([str(x) for x in self.sensor3_target_coord]))
            row_data.append(f'{self.sensor3_distance_val/1000:,.2f}')
            row_data.append(f'{self.sensor3_min_distance_km:,.2f}')
            row_data.append(f'{self.sensor3_max_distance_km:,.2f}')
            ewt_bool = True
        # if sensor 3 has no data in the input fields
        else:
            diff = 0
            # add blank entries to sensor 1 data log
            if self.sensor3_mgrs_val != None:
                row_data.append(self.sensor3_mgrs_val)
                row_data.append(', '.join([str(x) for x in self.sensor3_coord]))
                diff += 2
                if self.sensor3_distance._text != 'N/A':
                    for i in range(4): row_data.append('')
                    row_data.append(f'{self.sensor3_distance_val/1000:,.2f}')
                    diff += 5
            # add blank entries to sensor 3 data log
            for i in range(num_ewt_datapoints-diff): row_data.append('')
        if not ewt_bool:
            # end function w/o logging
            self.logger_gui.warning("No EWT data detected. No data logged.")
            self._show_info("No EWT data. No data logged.",icon='warning')
            return
        # append empty column for ACTUAL_TGT_MGRS to data row
        row_data.append('')

        # convert log row into dictionary
        log_row_dict = dict(zip(log_columns, row_data))
        # append data row (dict) to log data
        log_data.append(log_row_dict)
        # try to save the updated log file
        try:
            write_csv(os.path.join(self.log_targeting_directory, filename),log_data)
        # if file permissions prevent log file saving
        except PermissionError:
            # error message if file is currently open
            self.logger_gui.error(f"The desired {filename} log file is open during log function")
            self._show_info("Log file currently open. Cannot log data!",icon='warning')
            return
        # success pop-up
        self.logger_gui.info(f"Target data successfully logged to {filename}")
        self._show_info("Data successfully logged!!!",box_title='Successful Log',icon='info') 
    
    def reload_last_log(self) -> None:
        from utilities import read_csv
        import os
        import datetime
        import tkinter as tk

        def get_most_recently_modified_file(directory):
            # Validate directory
            if not os.path.isdir(directory):
                return None
            # Get list of CSV files
            files = [
                os.path.join(directory, f) for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f)) and f.endswith('.csv')
            ]
            # Sort by modification time
            files.sort(key=lambda x: os.stat(x).st_mtime, reverse=True)
            mtime = os.stat(files[0]).st_mtime
            readable_date = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %Hh:%Mm:%Ss')
            self.logger_gui.info(f"Reloading logged target from: {readable_date}")
            return files[0] if files else None

        # Check log directory
        if not os.path.isdir(self.log_targeting_directory):
            os.makedirs(self.log_targeting_directory)
            self.logger_gui.info(f"Target log directory created: '{self.log_targeting_directory}'")

        # Get most recent file
        recent_file = get_most_recently_modified_file(self.log_targeting_directory)
        if recent_file is None:
            self.logger_gui.warning("No log files detected.")
            self._show_info("No log files detected.", icon='warning')
            return

        # Read log data
        log_data = read_csv(recent_file)
        if not log_data:
            self.logger_gui.warning("Most recent log file is empty.")
            self._show_info("Most recent log file is empty.", icon='warning')
            return

        last_log_entry = log_data[-1]

        # Validate required keys
        required_keys = [
            'EWT_1_MGRS', 'EWT_1_LOB_DEGREES', 'EWT_1_PWR_REC_DbM',
            'EWT_2_MGRS', 'EWT_2_LOB_DEGREES', 'EWT_2_PWR_REC_DbM',
            'EWT_3_MGRS', 'EWT_3_LOB_DEGREES', 'EWT_3_PWR_REC_DbM',
            'FREQ_MHz', 'MIN_ERP_W', 'MAX_ERP_W', 'PATH_LOSS_COEFF'
        ]
        missing_keys = [key for key in required_keys if key not in last_log_entry]
        if missing_keys:
            self.logger_gui.error(f"Missing keys in log file: {', '.join(missing_keys)}")
            self._show_info(f"Missing keys in log file: {', '.join(missing_keys)}", icon='warning')
            return

        # Clear current entries
        self.clear_entries()

        # Populate Tkinter fields
        self.sensor1_mgrs.insert(0, last_log_entry['EWT_1_MGRS'])
        self.sensor1_lob.insert(0, last_log_entry['EWT_1_LOB_DEGREES'])
        self.sensor1_Rpwr.insert(0, last_log_entry['EWT_1_PWR_REC_DbM'])
        self.sensor2_mgrs.insert(0, last_log_entry['EWT_2_MGRS'])
        self.sensor2_lob.insert(0, last_log_entry['EWT_2_LOB_DEGREES'])
        self.sensor2_Rpwr.insert(0, last_log_entry['EWT_2_PWR_REC_DbM'])
        self.sensor3_mgrs.insert(0, last_log_entry['EWT_3_MGRS'])
        self.sensor3_lob.insert(0, last_log_entry['EWT_3_LOB_DEGREES'])
        self.sensor3_Rpwr.insert(0, last_log_entry['EWT_3_PWR_REC_DbM'])
        self.frequency.insert(0, last_log_entry['FREQ_MHz'])
        self.min_ERP.insert(0, last_log_entry['MIN_ERP_W'])
        self.max_ERP.insert(0, last_log_entry['MAX_ERP_W'])
        self.path_loss_coeff = last_log_entry['PATH_LOSS_COEFF']
        self.logger_gui.info(f"Target data reloaded into input fields.")

        # Set path loss coefficient option
        try:
            self.option_path_loss_coeff.set(self.get_pathloss_description_from_coeff(last_log_entry['PATH_LOSS_COEFF']))
        except Exception as e:
            self.logger_gui.error(f"Invalid path loss coefficient: {str(e)}")
            self._show_info(f"Invalid path loss coefficient: {str(e)}", icon='warning')
            return

        # Run EWT processor
        try:
            self.bypass_input_errors = True
            self.ewt_input_processor()
        except Exception as e:
            self.logger_gui.error(f"Failed to process log data: {str(e)}")
            self._show_info(f"Failed to process log data: {str(e)}", icon='warning')
        finally:
            self.bypass_input_errors = False
    
    def add_marker_event(self, 
                         coord: list[float,float], 
                         bool_bypass_measurement: bool = False, 
                         bool_bypass_log: bool = False
                         ) -> None:
        """Plot a "POI marker" on the map at user discretion."""
        # import libraries
        from PIL import Image, ImageTk
        from utilities import format_readable_DTG, generate_DTG
        from coords import convert_coords_to_mgrs, format_readable_mgrs, get_distance_between_coords
        import numpy as np
        import os
        # define marker's mgrs string
        marker_mgrs = f"{format_readable_mgrs(convert_coords_to_mgrs(list(coord)))}"
        # define marker's number
        marker_num = len(self.POI_marker_list) + 1
        # define marker's data string
        try:
            marker_data = f"POI marker (No. {marker_num%10}) plotted at {format_readable_mgrs(convert_coords_to_mgrs(list(coord)))} on {format_readable_DTG(generate_DTG())}"
            marker_icon = ImageTk.PhotoImage(Image.open(os.path.join(self.icon_directory, "POI_markers", f"POI_marker_{marker_num}.png")).resize((40, 40)))
        except FileNotFoundError:
            maker_data = f"POI marker plotted at {format_readable_mgrs(convert_coords_to_mgrs(list(coord)))} on {format_readable_DTG(generate_DTG())}"
            marker_icon = ImageTk.PhotoImage(Image.open(os.path.join(self.icon_directory, "POI_markers", "generic_marker.png")).resize((40, 40)))
        # plot marker
        new_marker = self.map_widget.set_marker(coord[0], coord[1], 
                                                text=marker_mgrs,
                                                icon=marker_icon,
                                                image_zoom_visibility=(10, float("inf")),
                                                command=self.marker_click,
                                                data=marker_data)
        # append marker object to marker list
        self._append_object(new_marker,"POI")
        self.logger_gui.info(f"POI marker (No. {marker_num}) plotted at {marker_mgrs}")
        # log the marker 
        if not bool_bypass_log: self.log_POI_marker(new_marker)
        # if other markers current exist
        if len(self.POI_marker_list) > 1 and not bool_bypass_measurement:
            from CTkMessagebox import CTkMessagebox
            num_start_point = len(self.POI_marker_list)-1
            msgBox = CTkMessagebox(title="Measurement Option", message=f"Measure distance from point {num_start_point}?", icon='info',options=['Yes','No'])
            response = msgBox.get()
            if response == "No": return
            # reverse POI marker list (last marker first)
            sequencial_marker_list = self.POI_marker_list[::-1]
            # initialize coordinate list
            sequencial_coord_list = []
            # create list of POI marker coordinates
            for i,marker in enumerate(sequencial_marker_list):
                sequencial_coord_list.append(list(marker.position))
            # determine distance between last two POI markers
            distance = get_distance_between_coords(sequencial_coord_list[0],sequencial_coord_list[1])
            # generate distance text
            distance_text = self._generate_sensor_distance_text(distance)
            # plot line between last two POI markers
            dist_line = self.map_widget.set_polygon([(sequencial_coord_list[0][0],sequencial_coord_list[0][1]),
                            (sequencial_coord_list[1][0],sequencial_coord_list[1][1])],outline_color="black")
            # determine middle coordinate between the last two coordinates
            coord_x = np.average([sequencial_coord_list[0][0],sequencial_coord_list[1][0]])
            coord_y = np.average([sequencial_coord_list[0][1],sequencial_coord_list[1][1]])
            # plot marker distance at center coordinate
            marker_dist = self.map_widget.set_marker(coord_x,coord_y,text=f'{distance_text}',
                                                     image_zoom_visibility=(10, float('inf')),
                                                     icon=self.blank_image)
            # add distance marker and connecting line to list
            self.path_list.append(dist_line)
            self.path_list.append(marker_dist)
            mgrs_start = format_readable_mgrs(convert_coords_to_mgrs(sequencial_coord_list[0]))
            mgrs_end = format_readable_mgrs(convert_coords_to_mgrs(sequencial_coord_list[1]))
            self.logger_gui.info(f"Measurement plotted from {mgrs_start} to {mgrs_end}: {distance_text}")

    def plot_OBJ(self,coord : list[float,float], 
                 bool_bypass_log = False
                 ) -> None:
        """Plot an "objective" on the map at user discretion."""
        # import libraries
        from PIL import Image, ImageTk
        from utilities import format_readable_DTG, generate_DTG
        from coords import convert_coords_to_mgrs, format_readable_mgrs
        import numpy as np
        import os
        # define marker's mgrs string
        marker_mgrs = f"{format_readable_mgrs(convert_coords_to_mgrs(list(coord)))}"
        # define marker's number
        marker_num = len(self.obj_list) + 1
        # define marker's data string
        marker_data = f"OBJ (No. {marker_num%10}) plotted at {format_readable_mgrs(convert_coords_to_mgrs(list(coord)))} on {format_readable_DTG(generate_DTG())}"
        marker_icon = ImageTk.PhotoImage(Image.open(os.path.join(self.icon_directory, "objective.png")).resize((40, 40)))
        # plot marker
        new_marker = self.map_widget.set_marker(coord[0], coord[1], 
                                                text=marker_mgrs,
                                                icon=marker_icon,
                                                image_zoom_visibility=(10, float("inf")),
                                                command=self.marker_click,
                                                data=marker_data)
        # append marker object to marker list
        self._append_object(new_marker,"OBJ")
        # log the marker 
        if not bool_bypass_log: self.log_tactical_marker(new_marker,"OBJ")

    def plot_NAI(self,coord : list[float,float], bool_bypass_log = False):
        """Plot a "NAI" on the map at user discretion."""
        # import libraries
        from PIL import Image, ImageTk
        from utilities import format_readable_DTG, generate_DTG
        from coords import convert_coords_to_mgrs, format_readable_mgrs, get_distance_between_coords
        import numpy as np
        import os
        # define marker's mgrs string
        marker_mgrs = f"{format_readable_mgrs(convert_coords_to_mgrs(list(coord)))}"
        # define marker's number
        marker_num = len(self.nai_list) + 1
        # define marker's data string
        marker_data = f"NAI (No. {marker_num%10}) plotted at {format_readable_mgrs(convert_coords_to_mgrs(list(coord)))} on {format_readable_DTG(generate_DTG())}"
        marker_icon = ImageTk.PhotoImage(Image.open(os.path.join(self.icon_directory, "nai.png")).resize((40, 40)))
        # plot marker
        new_marker = self.map_widget.set_marker(coord[0], coord[1], 
                                                text=marker_mgrs,
                                                icon=marker_icon,
                                                image_zoom_visibility=(10, float("inf")),
                                                command=self.marker_click,
                                                data=marker_data)
        # append marker object to marker list
        self._append_object(new_marker,"NAI")
        # log the marker 
        if not bool_bypass_log: self.log_tactical_marker(new_marker,"NAI")

    def plot_EWT(self,ewt_coord : list[float,float], 
                 ewt_num: int, 
                 bool_bypass_log = False
                 ) -> None:
        from utilities import format_readable_DTG, generate_DTG
        from coords import convert_coords_to_mgrs, format_readable_mgrs
        ewt_mgrs = format_readable_mgrs(convert_coords_to_mgrs(ewt_coord))
        ewt_num = str(ewt_num)
        if ewt_num == '1':
            image = self.ew_team1_image
        elif ewt_num == '2':
            image = self.ew_team2_image
        elif ewt_num == '3':
            image = self.ew_team3_image
        ewt_marker = self.map_widget.set_marker(
            deg_x=ewt_coord[0], 
            deg_y=ewt_coord[1], 
            text="", 
            image_zoom_visibility=(10, float("inf")),
            marker_color_circle='white',
            text_color='black',
            icon=image,
            command=self.marker_click,
            data=f'EWT {ewt_num}\n{ewt_mgrs}\nat {format_readable_DTG(generate_DTG())}')
        self._append_object(ewt_marker,"EWT")
        if not bool_bypass_log: self.log_ewt_marker(ewt_marker,ewt_num)

    def right_click_plot_EWT(self,
                             coord: list[float,float]
                             ) -> None:
        """Function to plot EWT marker on right-click."""
        from CTkMessagebox import CTkMessagebox
        from coords import convert_coords_to_mgrs, format_readable_mgrs
        coord = list(coord)
        msgBox = CTkMessagebox(title="Plotting EWT", message="Which EWT is to be plotted?", icon='info',options=['EWT 1','EWT 2','EWT 3'])
        mgrs = convert_coords_to_mgrs(coord)
        mgrs_readable = format_readable_mgrs(mgrs)
        if msgBox.get() == "EWT 1":
            self.plot_EWT(coord,1)
            self.sensor1_mgrs.delete(0, 'end')
            self.sensor1_mgrs.insert(0,mgrs)
            self.logger_gui.info(f"EWT 1 plotted at {mgrs_readable} via right-click")
        elif msgBox.get() == "EWT 2":
            self.plot_EWT(coord,2)
            self.sensor2_mgrs.delete(0, 'end')
            self.sensor2_mgrs.insert(0,mgrs)
            self.logger_gui.info(f"EWT 2 plotted at {mgrs_readable} via right-click")
        elif msgBox.get() == "EWT 3":
            self.plot_EWT(coord,3)
            self.sensor3_mgrs.delete(0, 'end')
            self.sensor3_mgrs.insert(0,mgrs)
            self.logger_gui.info(f"EWT 3 plotted at {mgrs_readable} via right-click")

    def copy_mgrs_grid(self, 
                       coords: tuple[float,float]
                       ) -> None:
        """Function to copy MGRS coordinates to clipboard."""
        from coords import convert_coords_to_mgrs
        # function to write text to clipboard
        def copy2clip(txt):
            self.clipboard_clear()
            self.clipboard_append(txt)
        # define MGRS string from coordinate
        mgrs = str(convert_coords_to_mgrs(list(coords))).strip()
        # write MGRS to clipboard
        copy2clip(mgrs)
        # copy-to-clipboard pop-up
        msg = f'"{mgrs}" copied to clipboard'
        self._show_info(msg,box_title="Selection Copied",icon="info")

    def copy_selection(self,entry_object) -> None:
        try:
            selected_text = entry_object.get()
        except AttributeError:
            selected_text = entry_object.cget("text")
        except:
            "Error in copy_selection method"
            return
        if len(selected_text.strip()) == 0: return
        self.clipboard_clear()
        self.clipboard_append(selected_text)
        if isinstance(selected_text,list):
            msg = f'"{selected_text[0]}" copied to clipboard'
        elif isinstance(selected_text,str):
            msg = f'"{selected_text}" copied to clipboard'
        self._show_info(msg,box_title="Selection Copied",icon="info")
    
    def search_event(self) -> None:
        from tkinter import END
        from coords import convert_mgrs_to_coords, check_mgrs_input, correct_mgrs_input, check_coord_input, correct_coord_input
        try:
            search_mgrs = self.search_mgrs.get()
        except ValueError:
            self._show_info("Error loading Search MGRS",icon='warning')
            return
        if check_mgrs_input(search_mgrs):
            search_mgrs = correct_mgrs_input(search_mgrs)
            self.search_mgrs.delete(0,END)
            self.search_mgrs.insert(0,search_mgrs)
            search_coord = convert_mgrs_to_coords(search_mgrs)
            self.map_widget.set_position(search_coord[0],search_coord[1])
            self.add_marker_event(search_coord)
        elif check_coord_input(search_mgrs):
            search_coord = correct_coord_input(search_mgrs)
            self.map_widget.set_position(search_coord[0],search_coord[1])
            self.add_marker_event(search_coord)
        else:
            self._show_info("Invalid MGRS input!",icon='warning')
            return

    def get_latest_logged_position(self) -> None:
        import os
        import json
        from pathlib import Path
        from datetime import datetime

        if not os.path.exists(self.log_eud_position_directory):
            return None

        # Get list of log files, sorted by date descending
        log_files = sorted(Path(self.log_eud_position_directory).glob("position_log_*.jsonl"), reverse=True)
        
        for log_file in log_files:
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if not lines:
                        continue
                    # Read from the bottom up
                    for line in reversed(lines):
                        try:
                            entry = json.loads(line)
                            data = entry.get("data", {})
                            lat = float(data.get("lat"))
                            lon = float(data.get("lon"))
                            acc = float(data.get("accuracy_m", 0))
                            return lat, lon, acc
                        except Exception:
                            continue
            except Exception:
                continue
        return None

    def plot_EUD_position(self,coord=None):
        import time
        from PIL import Image, ImageTk
        from utilities import format_readable_DTG, generate_DTG
        from coords import convert_coords_to_mgrs, format_readable_mgrs
        from CTkMessagebox import CTkMessagebox
        time.sleep(2)
        self.logger_positioning.info("Attempting to plot EUD position.")
        if coord == None:
            try:
                latest_position = self.get_latest_logged_position()
                if latest_position is None:
                    self._show_info('No positioning data available.', icon='warning')
                    self.logger_positioning.warning(f"No positioning data available.")
                    return
                lat, lon, acc = latest_position
            except Exception as e:
                self.logger_positioning.error(f"Failure to plot EUD position: {e}.")
                return
            if lat is None or lon is None:
                self.logger_positioning.warning("No GPS data available. Cannot read GPS receiver.")
                self._show_info("Cannot read GPS receiver",icon='warning')
                return
        else:
            lat = coord[0]; lon = coord[1]
        mgrs_formated = format_readable_mgrs(convert_coords_to_mgrs([lat,lon]))
        marker_icon = ImageTk.PhotoImage(Image.open(os.path.join(self.icon_directory, "eud_marker.png")).resize((40, 40)))
        eud_marker_text = f"{mgrs_formated}"
        eud_marker_data = f"EUD at {mgrs_formated} at {format_readable_DTG(generate_DTG())}"
        eud_marker = self.map_widget.set_marker(lat, lon, 
                                                text=eud_marker_text,
                                                icon=marker_icon,
                                                image_zoom_visibility=(10, float("inf")),
                                                command=self.marker_click,
                                                data=eud_marker_data)
        self._append_object(eud_marker,"EUD")
        self.logger_positioning.info(f"Plotted EUD position at {mgrs_formated} ({lat}, {lon}).")
        msgBox = CTkMessagebox(title="EUD Position Plotted", message='Do you want to adjust the map view to the most updated EUD location?', icon='info',options=['Yes','No'])
        response = msgBox.get()
        if response == "Yes":
            self.map_widget.set_position(lat, lon)
            self.logger_gui.info(f"Map view adjusted to EUD position at {mgrs_formated} ({lat}, {lon}).")

    def increment_brightness_up(self):
        from utilities import adjust_brightness
        new_brightness = adjust_brightness('increase')
        self.logger_gui.info(f"Brightness increased to {new_brightness}%.")

    def increment_brightness_down(self):
        from utilities import adjust_brightness
        new_brightness = adjust_brightness('decrease')
        self.logger_gui.info(f"Brightness decreased to {new_brightness}%.")

    def log_POI_marker(self,marker):
        import datetime
        from utilities import generate_DTG, read_csv, write_csv
        from coords import convert_coords_to_mgrs
        marker_coord = [marker.position[0],marker.position[1]]
        marker_mgrs = convert_coords_to_mgrs(marker_coord)
        dtg = generate_DTG()
        # assess if directory exists
        if not os.path.exists(self.log_directory):
            # create log directory
            os.makedirs(self.log_directory)
        # define marker file name
        filename = App.DEFAULT_VALUES["POI Marker Filename"]
        # if marker file already exists
        if os.path.isfile(os.path.join(self.log_directory, filename)):
            # read current log file
            marker_data = read_csv(os.path.join(self.log_directory, filename))
        # if marker file does not yet exist
        else:
            # create marker file DataFrame
            marker_data = []
        marker_columns = ['MARKER_NUM','MARKER_TYPE','LOC_MGRS','LOC_LATLON']
        new_marker_data = [len(marker_data)+1,'POI',marker_mgrs,', '.join([str(x) for x in marker_coord])]
        # convert marker row into dictionary
        log_row_dict = dict(zip(marker_columns, new_marker_data))
        # append data row (dict) to marker data
        marker_data.append(log_row_dict)
        # try to save the updated log file
        try:
            write_csv(os.path.join(self.log_directory, filename),marker_data)
        # if file permissions prevent log file saving
        except PermissionError:
            # error message if file is currently open
            self._show_info("POI Marker file currently open. Cannot log data!",icon='warning')
            return

    def log_tactical_marker(self,marker,marker_type):
        import datetime
        from utilities import read_csv, write_csv
        from coords import convert_coords_to_mgrs
        marker_coord = [marker.position[0],marker.position[1]]
        marker_mgrs = convert_coords_to_mgrs(marker_coord)
        # assess if directory exists
        if not os.path.exists(self.log_directory):
            # create log directory
            os.makedirs(self.log_directory)
        # define marker file name
        filename = App.DEFAULT_VALUES["Tactical Graphic Marker Filename"]
        # if marker file already exists
        if os.path.isfile(os.path.join(self.log_directory, filename)):
            # read current log file
            marker_data = read_csv(os.path.join(self.log_directory, filename))
        # if marker file does not yet exist
        else:
            # create marker file DataFrame
            marker_data = []
        marker_columns = ['MARKER_NUM','MARKER_TYPE','LOC_MGRS','LOC_LATLON']
        new_marker_data = [len(marker_data)+1,marker_type,marker_mgrs,', '.join([str(x) for x in marker_coord])]
        # convert marker row into dictionary
        log_row_dict = dict(zip(marker_columns, new_marker_data))
        # append data row (dict) to marker data
        marker_data.append(log_row_dict)
        # try to save the updated log file
        try:
            write_csv(os.path.join(self.log_directory, filename),marker_data)
        # if file permissions prevent log file saving
        except PermissionError:
            # error message if file is currently open
            self._show_info("POI Marker file currently open. Cannot log data!",icon='warning')
            return

    def log_ewt_marker(self, marker, ewt_num):
        from utilities import read_csv, write_csv
        from coords import convert_coords_to_mgrs
        import os

        marker_coord = [marker.position[0], marker.position[1]]
        marker_mgrs = convert_coords_to_mgrs(marker_coord)

        # Ensure directory exists
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

        filename = App.DEFAULT_VALUES["EWT Marker Filename"]
        filepath = os.path.join(self.log_directory, filename)

        # Load existing data
        if os.path.isfile(filepath):
            marker_data = read_csv(filepath)
        else:
            marker_data = []

        marker_columns = ['MARKER_NUM', 'MARKER_TYPE', 'LOC_MGRS', 'LOC_LATLON', 'EWT_DATA']
        new_marker_data = [ewt_num, 'EWT', marker_mgrs, ', '.join([str(x) for x in marker_coord]), marker.data]
        new_row = dict(zip(marker_columns, new_marker_data))

        # Remove any row with the same ewt_num or EWT_DATA
        marker_data = [
            row for row in marker_data
            if row.get('MARKER_NUM') != ewt_num and row.get('EWT_DATA') != marker.data
        ]

        # Append the new entry
        marker_data.append(new_row)

        # Try to write the updated file
        try:
            write_csv(filepath, marker_data)
        except PermissionError:
            self._show_info("EWT Marker file currently open. Cannot log data!", icon='warning')

    def clear_measurements(self, bool_bypass_log = False) -> None:
        for path in self.path_list:
            path.delete()
        self.path_list = []
        if not bool_bypass_log: self.logger_gui.info("Cleared all measurements from map and path list.")

    def clear_POI_markers(self, bool_bypass_log = False) -> None:
        """Clear all POI markers from the map and the marker list."""
        for POI_marker in self.POI_marker_list:
            POI_marker.delete()

        for eud_marker in self.eud_marker_list:
            eud_marker.delete()
            self.map_widget.canvas.delete(eud_marker)

        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
            self.logger_gui.info(f"Created marker log directory at {self.log_directory}")

        filename = App.DEFAULT_VALUES["POI Marker Filename"]
        marker_file_path = os.path.join(self.log_directory, filename)

        try:
            os.remove(marker_file_path)
        except FileNotFoundError:
            self.logger_gui.debug(f"Marker file not found: {marker_file_path}")
        except PermissionError:
            self._show_info("POI Marker file currently open. Cannot clear data!", icon='warning')
            self.logger_gui.warning(f"Permission denied while deleting: {marker_file_path}")

        self.POI_marker_list = []
        self.eud_marker_list = []
        if not bool_bypass_log: self.logger_gui.info("Cleared all POI markers from the map and marker list.")

    def clear_tactical_markers(self,bool_bypass_log=False) -> None:
        for obj_marker in self.obj_list:
            obj_marker.delete()
        for nai_marker in self.nai_list:
            nai_marker.delete()
        # assess if log directory exists
        if not os.path.exists(self.log_directory):
            # create log directory
            os.makedirs(self.log_directory)
        # define marker file name
        filename = App.DEFAULT_VALUES["Tactical Graphic Marker Filename"]
        try:
            os.remove(os.path.join(self.log_directory, filename))
        # if file does not exist
        except FileNotFoundError:
            pass
        # if file permissions prevent marker file deleting
        except PermissionError:
            # error message if file is currently open
            self._show_info("Tactical Marker file currently open. Cannot clear data!",icon='warning')
        self.obj_list = []; self.nai_list = []
        if not bool_bypass_log: self.logger_gui.info("Cleared all tactical markers from the map and marker list.")
    
    def clear_target_overlays(self) -> None:
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
        self.logger_gui.info(f"Cleared all target overlays from the map and tracker lists.")

    def clear_ewts(self) -> None:
        for ewt_marker in self.ewt_marker_list:
            ewt_marker.delete()
        self.ewt_marker_list = []
        # assess if log directory exists
        if not os.path.exists(self.log_directory):
            # create log directory
            os.makedirs(self.log_directory)
        # define marker file name
        filename = App.DEFAULT_VALUES["EWT Marker Filename"]
        try:
            os.remove(os.path.join(self.log_directory, filename))
        # if file does not exist
        except FileNotFoundError:
            pass
        # if file permissions prevent marker file deleting
        except PermissionError:
            # error message if file is currently open
            self._show_info("EWT Marker file currently open. Cannot clear data!",icon='warning')
        # Log the clearing of EWT markers
        self.logger_gui.info("Cleared all EWT markers from the map and marker list.")

    def clear_entries(self) -> None:
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
        self.logger_gui.info(f"Cleared all POI input fields.")
        # self.batch_download_center_mgrs.delete(0,END)
        # self.batch_download_zoom_range.delete(0,END)
        # self.batch_download_radius.delete(0,END)
        # self.search_mgrs.delete(0,END)
        
    def marker_click(self,marker) -> None:
        from CTkMessagebox import CTkMessagebox
        from map import remove_rows_from_marker_csv, remove_ewt_from_marker_csv
        # generate message box based on marker category
        if "TGT" in marker.data:
            msgBox_title = "TGT Data"
            msgBox = CTkMessagebox(title=msgBox_title, message=marker.data, icon='info',options=['Acknowledge','Remove'])
        elif "EWT" in marker.data:
            msgBox_title = "EWT Data"
            msgBox = CTkMessagebox(title=msgBox_title, message=marker.data, icon='info',options=['Acknowledge','Remove'])
        elif "POI" in marker.data:
            msgBox_title = "Point of Interest (POI)"
            msgBox = CTkMessagebox(title=msgBox_title, message=marker.data, icon='info',options=['Acknowledge','Remove'])
        elif "OBJ" in marker.data:
            msgBox_title = "OBJ Marker"
            msgBox = CTkMessagebox(title=msgBox_title, message=marker.data, icon='info',options=['Acknowledge','Remove'])        
        elif "NAI" in marker.data:
            msgBox_title = "NAI Marker"
            msgBox = CTkMessagebox(title=msgBox_title, message=marker.data, icon='info',options=['Acknowledge','Remove'])        
        else:
            msgBox_title = "Unknown Marker"
            msgBox = CTkMessagebox(title=msgBox_title, message=marker.data, icon='info',options=['Acknowledge','Remove'])
        # get user response
        response = msgBox.get()
        if response == 'Remove':
            # remove marker from marker list
            if msgBox_title == "TGT Data":
                self.target_marker_list.remove(marker)
                self.logger_gui.info(f"TGT Data Marker removed from the map and tracker list.")
            elif msgBox_title == "EWT Data":
                self.ewt_marker_list.remove(marker)
                filepath = os.path.join(self.log_directory,App.DEFAULT_VALUES["EWT Marker Filename"])
                ewt_num = str(str(marker.data).split('\n')[0].split()[-1]).strip()
                coord_string = ', '.join([str(marker.position[0]),str(marker.position[1])])
                remove_ewt_from_marker_csv(filepath,ewt_num,coord_string)
                self.logger_gui.info(f"EWT {ewt_num} marker removed from the map and tracker list.")
            elif msgBox_title == "Point of Interest (POI)":
                self.POI_marker_list.remove(marker)
                filepath = os.path.join(self.log_directory,App.DEFAULT_VALUES["POI Marker Filename"])
                marker_num = int(str(marker.data).split('No. ')[-1].split(')')[0].strip())
                remove_rows_from_marker_csv(filepath,"POI",marker_num)
                self.logger_gui.info(f"POI (No. {marker_num}) removed from the map and tracker file.")
            elif msgBox_title == "OBJ Marker":
                self.obj_list.remove(marker)
                filepath = os.path.join(self.log_directory,App.DEFAULT_VALUES["Tactical Graphic Marker Filename"])
                marker_num = int(str(marker.data).split('No. ')[-1].split(')')[0].strip())
                remove_rows_from_marker_csv(filepath,"OBJ",marker_num)
                self.logger_gui.info(f"OBJ Marker removed from the map and tracker file.")
            elif msgBox_title == "NAI Marker":
                self.nai_list.remove(marker)
                filepath = os.path.join(self.log_directory,App.DEFAULT_VALUES["Tactical Graphic Marker Filename"])
                marker_num = int(str(marker.data).split('No. ')[-1].split(')')[0].strip())
                remove_rows_from_marker_csv(filepath,"NAI",marker_num)
                self.logger_gui.info(f"NAI Marker removed from the map and tracker file.")
            # delete marker from map
            marker.delete()
            if len(self.POI_marker_list) == len(self.path_list) == 0:
                self.clear_POI_markers(bool_bypass_log=True)
            if len(self.obj_list) == len(self.nai_list) == 0:
                self.clear_tactical_markers(bool_bypass_log=True)
        
    def polygon_click(self,polygon) -> None:
        from CTkMessagebox import CTkMessagebox
        # generate message box based on polygon category
        if "LOB" in polygon.data:
            msgBox_title = "LOB"
            msgBox = CTkMessagebox(title=msgBox_title, message=polygon.data, icon='info',options=['Acknowledge','Remove'])
        elif "CUT" in polygon.data:
            msgBox_title = "CUT"
            msgBox = CTkMessagebox(title=msgBox_title, message=polygon.data, icon='info',options=['Acknowledge','Remove'])
        elif "FIX" in polygon.data:
            msgBox_title = "FIX"
            msgBox = CTkMessagebox(title=msgBox_title, message=polygon.data, icon='info',options=['Acknowledge','Remove'])
        else:
            msgBox_title = "Unknown Polygon"
            msgBox = CTkMessagebox(title=msgBox_title, message=polygon.data, icon='info',options=['Acknowledge','Remove'])
        # get user response
        response = msgBox.get()
        if response == 'Remove':
            # remove polygon from polygon list
            if msgBox_title == "LOB":
                self.lob_list.remove(polygon)
                self.logger_gui.info(f"LOB Polygon removed from the map and tracker list.")
            elif msgBox_title == "CUT":
                self.cut_list.remove(polygon)
                self.logger_gui.info(f"CUT Polygon removed from the map and tracker list.")
            elif msgBox_title == "FIX":
                self.fix_list.remove(polygon)
                self.logger_gui.info(f"FIX Polygon removed from the map and tracker list.")
            # delete polygon from map
            polygon.delete()

    def clear_options(self, command: str) -> None:
        """Clear specific options based on the marker type."""
        if command == 'Clear POIs':
            self.clear_POI_markers()
        elif command == 'Clear Graphics':
            self.clear_tactical_markers()
        elif command == 'Clear Target Overlays':
            self.clear_target_overlays()
        elif command == 'Clear Measurements':
            self.clear_measurements()
        elif command == 'Clear EWTs':
            self.clear_ewts()
        else:
            self.logger_gui.warning(f"Unknown marker clear command: {command}")
        self.clear_option_dropdown.set('Map Clear Options')

    def change_map(self, new_map: str) -> None:
        map_server_url = f'http://localhost:{App.MAP_SERVER_PORT}'
        if new_map == 'Local Terrain Map':
            self.map_widget.set_tile_server(map_server_url+"/Terrain/{z}/{x}/{y}.png", max_zoom=App.MAX_ZOOM)
        elif new_map == 'Local Satellite Map':
            self.map_widget.set_tile_server(map_server_url+"/ESRI/{z}/{x}/{y}.png", max_zoom=App.MAX_ZOOM)
        elif new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google Street":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=App.MAX_ZOOM)
        elif new_map == "Google Satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=App.MAX_ZOOM)
        self.logger_gui.info(f"Map Server changed to: {new_map}")

    def change_path_loss(self, path_loss_description: str) -> None:
        self.path_loss_coeff = App.PATH_LOSS_DICT.get(path_loss_description,4)
    
    def get_pathloss_description_from_coeff(self,coeff: float) -> dict[str,str]:
        reversed_dict = {str(value): str(key) for key, value in App.PATH_LOSS_DICT.items()}
        return reversed_dict.get(str(coeff).strip(),'Moderate Foliage')
    
    def change_sensor(self,sensor_option: str) -> None:
        """Change sensor parameters based on the selected sensor option."""
        if sensor_option == 'BEAST+':
            self.sensor1_receiver_gain_dBi = 0
            self.sensor2_receiver_gain_dBi = 0
            self.sensor1_error = 4
            self.sensor2_error = 4
            self.sensor3_error = 4
        elif sensor_option == 'VROD/VMAX':
            self.sensor1_receiver_gain_dBi = 0
            self.sensor2_receiver_gain_dBi = 0
            self.sensor1_error = 6
            self.sensor2_error = 6
            self.sensor3_error = 6

    def change_preset_target_emitter(self, preset_option: str) -> None:
        """Change target emitter parameters based on the selected preset option."""
        if preset_option == 'Custom':
            self.logger_gui.info("Custom target preset selected.") 
        elif preset_option in App.conf_target_presets.keys():
            self.min_ERP.delete(0, 'end')
            self.min_ERP.insert(0,App.conf_target_presets[preset_option]["MIN_ERP"])
            self.max_ERP.delete(0, 'end')
            self.max_ERP.insert(0,App.conf_target_presets[preset_option]["MAX_ERP"])
            self.logger_gui.info(f"Target preset changed to: {preset_option} ({App.conf_target_presets[preset_option]['MIN_ERP']} - {App.conf_target_presets[preset_option]['MAX_ERP']} W)")
        else:
            self.logger_gui.warning(f"Invalid target preset option: {preset_option}")

    def _append_object(self,map_object,map_object_list_name):
        # check if map object is a EWT marker
        if map_object_list_name.upper() == 'EWT':
            # check if EWT marker already exists in the EWT marker list
            if not self._check_if_object_in_object_list(map_object,self.ewt_marker_list):
                # append the EWT marker to the EWT marker list
                self.ewt_marker_list.append(map_object)
        # check if map object is a target marker
        elif map_object_list_name.upper() == 'TGT':
            # check if target marker already exists in the target marker list
            if not self._check_if_object_in_object_list(map_object,self.target_marker_list):
                # append the target marker to the target marker list
                self.target_marker_list.append(map_object)
        # check if map object is a POI marker
        if map_object_list_name.upper() == 'POI':
            # check if EWT marker already exists in the EWT marker list
            if not self._check_if_object_in_object_list(map_object,self.POI_marker_list):
                # append the EWT marker to the EWT marker list
                self.POI_marker_list.append(map_object)
        # check if map object is an OBJ
        elif map_object_list_name.upper() == 'OBJ':
            # check if OBJ already exists in the OBJ list
            if not self._check_if_object_in_object_list(map_object,self.obj_list):
                # append the OBJ to the OBJ list
                self.obj_list.append(map_object)
        # check if map object is an NAI
        elif map_object_list_name.upper() == 'NAI':
            # check if NAI already exists in the NAI list
            if not self._check_if_object_in_object_list(map_object,self.nai_list):
                # append the NAI to the NAI list
                self.nai_list.append(map_object)
        # check if map object is a EUD marker
        if map_object_list_name.upper() == 'EUD':
            # check if EWT marker already exists in the EWT marker list
            if not self._check_if_object_in_object_list(map_object,self.eud_marker_list):
                # append the EWT marker to the EWT marker list
                self.eud_marker_list.append(map_object)        
        # check if map object is a LOB
        elif map_object_list_name.upper() == 'LOB':
            # check if LOB already exists in the LOB list
            if not self._check_if_object_in_object_list(map_object,self.lob_list):
                # append the LOB to the LOB list
                self.lob_list.append(map_object)
        # check if map object is a CUT
        elif map_object_list_name.upper() == 'CUT':
            # check if CUT already exists in the CUT list
            if not self._check_if_object_in_object_list(map_object,self.cut_list):
                # append the CUT to the CUT list
                self.cut_list.append(map_object)
        # check if map object is a FIX
        elif map_object_list_name.upper() == 'FIX':
            # check if FIX already exists in the FIX list
            if not self._check_if_object_in_object_list(map_object,self.fix_list):
                # append the FIX to the FIX list
                self.fix_list.append(map_object)

    def _check_if_object_in_object_list(self,map_object,map_object_list):
        map_object_data = map_object.data
        object_data_list = [mo.data for mo in map_object_list]
        if map_object_data in object_data_list:
            # delete redudant map object
            map_object.delete()
            return True
        else:
            return False

    def _generate_sensor_distance_text(self,
                                       distance : float,
                                       bearing: int = None
                                       ) -> str:
        """Generate sensor distance string w/ adjusted units of measurement."""
        # set default unit of measurement
        distance_unit = 'm'
        # if distance is greater than 1000m
        if distance >= 1000:
            # convert meters to km
            distance /= 1000
            # change unit of measurement to km
            distance_unit = 'km'
        # return distance string
        if bearing is not None:
            return f'{distance:,.2f}{distance_unit} at {bearing}°'
        return f'{distance:,.2f}{distance_unit}'

    def _input_error(self,category: str,msg: str,single_lob_option: bool =False,cut_option: bool =False,ewt_bypass_option: bool =False,EWT_num: str ='') -> str:
        from CTkMessagebox import CTkMessagebox
        if not single_lob_option and not cut_option and not ewt_bypass_option:
            msgBox = CTkMessagebox(title=f"Error in {category}", message=msg, icon='warning',options=['Re-input','Use Default'])
        if not single_lob_option and not cut_option and ewt_bypass_option:
            msgBox = CTkMessagebox(title=f"Error in {category}", message=msg, icon='warning',options=['Re-input',f'Bypass EWT {EWT_num}'.strip(),'Use Default'])
        elif single_lob_option and not cut_option:
            msgBox = CTkMessagebox(title=f"Error in {category}", message=msg, icon='warning',options=['Re-input','LOB',f'Bypass EWT {EWT_num}'.strip(),'Use Default'])            
        elif cut_option:
            msgBox = CTkMessagebox(title=f"Error in {category}", message=msg, icon='warning',options=['Re-input','LOB/CUT',f'Bypass EWT {EWT_num}'.strip(),'Use Default'])
        response = msgBox.get()
        if response is None: return None
        if response == 'Re-input':
            return 'Re-input'
        elif "Bypass" in response:
            return 'Bypass'
        elif response == 'Use Default':
            return 'Default'
        elif response == 'LOB':
            return 'SL'
        elif response == 'LOB/CUT':
            return 'LOB/CUT'
        else:
            return None

    def _log_ewt_input_values(self) -> None:
        """Log the input values to the GUI logger."""
        from coords import format_readable_mgrs
        if self.sensor1_mgrs_val != None:
            self.logger_targeting.info(f"EWT 1 Plotted at {format_readable_mgrs(self.sensor1_mgrs_val)}")
            if self.sensor1_grid_azimuth_val != None: self.logger_targeting.info(f"Sensor 1 Grid Azimuth: {self.sensor1_grid_azimuth_val} degrees ({self.option_sensor.get()})")
            if self.sensor1_power_received_dBm_val != None: self.logger_targeting.info(f"Sensor 1 PWR Received: {self.sensor1_power_received_dBm_val} dBm")
        if self.sensor2_mgrs_val != None:   
            self.logger_targeting.info(f"EWT 2 Plotted at {format_readable_mgrs(self.sensor2_mgrs_val)}")
            if self.sensor2_grid_azimuth_val != None: self.logger_targeting.info(f"Sensor 2 LOB: {self.sensor2_grid_azimuth_val} degrees ({self.option_sensor.get()})")
            if self.sensor2_power_received_dBm_val != None: self.logger_targeting.info(f"Sensor 2 PWR Received: {self.sensor2_power_received_dBm_val} dBm")
        if self.sensor3_mgrs_val != None:
            self.logger_targeting.info(f"EWT 3 Plotted at {format_readable_mgrs(self.sensor3_mgrs_val)}")
            if self.sensor3_grid_azimuth_val != None: self.logger_targeting.info(f"Sensor 3 LOB: {self.sensor3_grid_azimuth_val} degrees ({self.option_sensor.get()})")
            if self.sensor3_power_received_dBm_val != None: self.logger_targeting.info(f"Sensor 3 PWR Received: {self.sensor3_power_received_dBm_val} dBm")
        if self.frequency_MHz_val != None:
            self.logger_targeting.info(f"Targeted Signal: {self.frequency_MHz_val} MHz transmitting between {self.min_wattage_val} and {self.max_wattage_val} W, through {self.get_pathloss_description_from_coeff(self.path_loss_coeff)}")

    def _paste_from_clipboard(self,entry_object) -> None:
        try:
            selected_text = entry_object.selection_get().split()
            if len(selected_text) > 0:
                self.clipboard_clear()
                self.clipboard_append(selected_text)
                if isinstance(selected_text,list):
                    msg = f'"{selected_text[0]}" copied to clipboard'
                elif isinstance(selected_text,str):
                    msg = f'"{selected_text}" copied to clipboard'
                self._show_info(msg,box_title="Selection Copied",icon="info")
            else:
                entry_object.insert('end', self.selection_get(selection='CLIPBOARD'))
        except TclError:
            entry_object.insert('end', self.selection_get(selection='CLIPBOARD'))

    def _safe_plot_callback(self,elevation_data, sensor_coord, nearside_km, target_coord, farside_km):
        from dted import plot_elevation_profile
        plot_elevation_profile(elevation_data, sensor_coord, nearside_km, target_coord, farside_km)
        self.logger_gui.info(f"Elevation Profile Plotted.")

    def _show_info(self,msg,box_title: str ='Warning Message',icon: str ='warning') -> None:
        from CTkMessagebox import CTkMessagebox
        CTkMessagebox(title=box_title, message=msg, icon=icon,option_1='Ackowledged')

    def destroy(self):
        self.logger_gui.info("Application closing")
        LoggerManager.clear_cache()
        super().destroy()

    def on_closing(self):
        import sys
        self.destroy()
        sys.exit()          
        
if __name__ == "__main__":
    app = App()
    app.mainloop()

