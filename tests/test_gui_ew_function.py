import pytest
import customtkinter as ctk
import sys
import os
import time

# Ensure src/ is in the system path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from gui import App  # Import App after modifying the path
from utilities import read_json
conf = read_json(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","src","config_files","conf.json"))

@pytest.fixture
def default_inputs():
    return {
    "default_sensor1_mgrs": conf["DEFAULT_SENSOR_1_MGRS"],
    "default_sensor1_Rpwr": conf["DEFAULT_SENSOR_1_PWR_RECEIVED"],
    "default_sensor1_lob": conf["DEFAULT_SENSOR_1_LOB"],
    "default_sensor2_mgrs": conf["DEFAULT_SENSOR_2_MGRS"],
    "default_sensor2_Rpwr": conf["DEFAULT_SENSOR_2_PWR_RECEIVED"],
    "default_sensor2_lob": conf["DEFAULT_SENSOR_2_LOB"],
    "default_sensor3_mgrs": conf["DEFAULT_SENSOR_3_MGRS"],
    "default_sensor3_Rpwr": conf["DEFAULT_SENSOR_3_PWR_RECEIVED"],
    "default_sensor3_lob": conf["DEFAULT_SENSOR_3_LOB"],
    "default_frequency":conf["DEFAULT_FREQUENCY_MHZ"],
    "default_min_ERP":conf["DEFAULT_MIN_ERP_W"],
    "default_max_ERP":conf["DEFAULT_MAX_ERP_W"],
    "default_option_path_loss_coeff":conf["DEFAULT_PATH-LOSS_COEFFICIENT_DESCRIPTION"]
    }

@pytest.fixture()
def expected_values():
    return {
        "LOB_EWT1": {
            "expected_target_grid": "32UQV 01793 58322",
            "expected_label_target_grid": "TARGET GRID (1 LOB)",
            "expected_sensor1_distance": "1.89km",
            "expected_sensor2_distance": "N/A",
            "expected_sensor3_distance": "N/A",
            "expected_target_error": "446 acres",
            "expected_target_class": "(1 LOB)",
            "expected_target_coord": [49.24437525321693, 11.77266110324632],
            "expected_target_mgrs": "32UQV0179358322"
        },
        "LOB_EWT2": {
            "expected_target_grid": "32UQV 01759 58557",
            "expected_label_target_grid": "TARGET GRID (1 LOB)",
            "expected_sensor1_distance": "N/A",
            "expected_sensor2_distance": "2.11km",
            "expected_sensor3_distance": "N/A",
            "expected_target_error": "564 acres",
            "expected_target_class": "(1 LOB)",
            "expected_target_coord": [49.24649727522025, 11.772304238438442],
            "expected_target_mgrs": "32UQV0175958557"
        },
        "LOB_EWT3": {
            "expected_target_grid": "32UQV 01698 58754",
            "expected_label_target_grid": "TARGET GRID (1 LOB)",
            "expected_sensor1_distance": "N/A",
            "expected_sensor2_distance": "N/A",
            "expected_sensor3_distance": "2.38km",
            "expected_target_error": "714 acres",
            "expected_target_class": "(1 LOB)",
            "expected_target_coord": [49.24829283849336, 11.771573744236349],
            "expected_target_mgrs": "32UQV0169858754"
        },
        "CUT_EWT1_EWT2": {
            "expected_target_grid": "32UQV 01433 58602",
            "expected_label_target_grid": "TARGET GRID (CUT)",
            "expected_sensor1_distance": "1.43km",
            "expected_sensor2_distance": "1.78km",
            "expected_sensor3_distance": "N/A",
            "expected_target_error": "100 acres",
            "expected_target_class": "(CUT)",
            "expected_target_coord": [49.247009833868965, 11.767851178576054],
            "expected_target_mgrs": "32UQV0143358602"
        },
        "CUT_EWT1_EWT3": {
            "expected_target_grid": "32UQV 01367 58653",
            "expected_label_target_grid": "TARGET GRID (CUT)",
            "expected_sensor1_distance": "1.35km",
            "expected_sensor2_distance": "N/A",
            "expected_sensor3_distance": "2.04km",
            "expected_target_error": "58 acres",
            "expected_target_class": "(CUT)",
            "expected_target_coord": [49.24748873637496, 11.766976917051867],
            "expected_target_mgrs": "32UQV0136758653"
        },
        "CUT_EWT2_EWT3": {
            "expected_target_grid": "32UQV 01273 58624",
            "expected_label_target_grid": "TARGET GRID (CUT)",
            "expected_sensor1_distance": "N/A",
            "expected_sensor2_distance": "1.62km",
            "expected_sensor3_distance": "1.94km",
            "expected_target_error": "159 acres",
            "expected_target_class": "(CUT)",
            "expected_target_coord": [49.24726059841342, 11.765672634976104],
            "expected_target_mgrs": "32UQV0127358624"
        },
        "Fix": {
            "expected_target_grid": "32UQV 01374 58661",
            "expected_label_target_grid": "TARGET GRID (FIX)",
            "expected_sensor1_distance": "1.35km",
            "expected_sensor2_distance": "1.72km",
            "expected_sensor3_distance": "2.05km",
            "expected_target_error": "53 acres",
            "expected_target_class": "(FIX)",
            "expected_target_coord": [49.247557821821765, 11.76706972332321],
            "expected_target_mgrs": "32UQV0137458661"
        }
    }

@pytest.fixture(scope="module")
def app():
    """Initialize the CustomTkinter app for testing in the main thread."""
    app_instance = App()
    app_instance.button_clear_markers.invoke()
    app_instance.button_clear_tactical_graphics.invoke()
    app_instance.button_clear_target_overlays.invoke()
    app_instance.button_clear_measurements.invoke()
    app_instance.button_clear_entries.invoke()
    app_instance.update_idletasks()  # Process UI events
    app_instance.update()  # Ensure widgets are rendered
    yield app_instance
    app_instance.button_clear_markers.invoke()
    app_instance.button_clear_tactical_graphics.invoke()
    app_instance.button_clear_target_overlays.invoke()
    app_instance.button_clear_measurements.invoke()
    app_instance.button_clear_entries.invoke()
    app_instance.destroy()

def test_attribute_existence(app):
    """Test if the required attributes exist in the App instance."""
    # left panel
    assert hasattr(app, "sensor1_mgrs"), "sensor1_mgrs entry field not found in App."
    assert hasattr(app, "sensor1_Rpwr"), "sensor1_Rpwr entry field not found in App."
    assert hasattr(app, "sensor1_lob"), "sensor1_lob entry field not found in App."
    assert hasattr(app, "sensor2_mgrs"), "sensor2_mgrs entry field not found in App."
    assert hasattr(app, "sensor2_Rpwr"), "sensor2_Rpwr entry field not found in App."
    assert hasattr(app, "sensor2_lob"), "sensor2_lob entry field not found in App."
    assert hasattr(app, "sensor3_mgrs"), "sensor3_mgrs entry field not found in App."
    assert hasattr(app, "sensor3_Rpwr"), "sensor3_Rpwr entry field not found in App."
    assert hasattr(app, "sensor3_lob"), "sensor3_lob entry field not found in App."
    assert hasattr(app, "option_target_emitter_preset"), "option_target_emitter_preset entry field not found in App."
    assert hasattr(app, "frequency"), "frequency entry field not found in App."
    assert hasattr(app, "min_ERP"), "min_erp entry field not found in App."
    assert hasattr(app, "max_ERP"), "max_erp entry field not found in App."
    assert hasattr(app, "option_path_loss_coeff"), "option_path_loss_coeff entry field not found in App."
    assert hasattr(app, "target_grid"), "target_grid entry field not found in App."
    assert hasattr(app, "sensor1_distance"), "sensor1_distance entry field not found in App."
    assert hasattr(app, "sensor2_distance"), "sensor2_distance entry field not found in App."
    assert hasattr(app, "sensor3_distance"), "sensor3_distance entry field not found in App."
    assert hasattr(app, "target_error"), "target_error entry field not found in App."
    assert hasattr(app, "button_clear_entries"), "button_clear_entries button not found in App."
    assert hasattr(app, "button_calculate"), "button_calculate button not found in App."
    assert hasattr(app, "button_reload_last_log"), "button_reload_last_log button not found in App."
    assert hasattr(app, "button_log_data"), "button_log_data button not found in App."
    # top right panel
    assert hasattr(app, "button_plot_eud_location"), "button_plot_eud_location button not found in App."
    assert hasattr(app, "button_clear_tactical_graphics"), "button_clear_tactical_graphics button not found in App."
    assert hasattr(app, "button_clear_target_overlays"), "button_clear_target_overlays button not found in App."
    assert hasattr(app, "button_clear_markers"), "button_clear_markers button not found in App."
    assert hasattr(app, "button_clear_measurements"), "button_clear_measurements button not found in App."
    assert hasattr(app, "map_option_menu"), "map_option_menu entry field not found in App."
    # mid right panel
    assert hasattr(app, "map_widget"), "map_widget not found in App."
    # bottom right panel
    assert hasattr(app, "search_mgrs"), "search_mgrs entry field not found in App."
    assert hasattr(app, "button_search"), "button_search_mgrs button not found in App."
    assert hasattr(app, "button_brightness_down"), "button_brightness_down button not found in App."
    assert hasattr(app, "button_brightness_up"), "button_brightness_up button not found in App."

def plot_user_markers(app):
    pass

def test_default_inputs_EWT1_LOB(app,default_inputs,expected_values):
    """Test default input in the GUI and their expected outputs"""
    
    # Insert default values into the entry fields
    app.button_clear_entries.invoke()
    app.update_idletasks()
    app.bypass_input_errors = True  # Bypass input errors for testing
    app.bypass_elevation_plot_prompt = True  # Bypass elevation plot prompt for testing

    app.sensor1_mgrs.insert(0, default_inputs["default_sensor1_mgrs"])
    app.sensor1_Rpwr.insert(0, default_inputs["default_sensor1_Rpwr"])
    app.sensor1_lob.insert(0, default_inputs["default_sensor1_lob"])
    app.frequency.insert(0, default_inputs["default_frequency"])
    app.min_ERP.insert(0, default_inputs["default_min_ERP"])
    app.max_ERP.insert(0, default_inputs["default_max_ERP"])
    app.option_path_loss_coeff.set(default_inputs["default_option_path_loss_coeff"])

    # Update UI to process the inserted values
    app.update_idletasks()

    # Run the calculation
    app.button_calculate.invoke()
    app.update_idletasks()
    time.sleep(1)

    # Check if the calculated values are displayed
    assert app.target_grid.cget("text") == expected_values["LOB_EWT1"]["expected_target_grid"], f"Target grid is {app.target_grid.cget("text")} instead of {expected_values["LOB_EWT1"]["expected_target_grid"]}."
    assert app.label_target_grid.cget("text") == expected_values["LOB_EWT1"]["expected_label_target_grid"], f"Label for target grid is {app.label_target_grid.cget("text")} instead of {expected_values["LOB_EWT1"]["expected_label_target_grid"]}."
    assert app.sensor1_distance.cget("text") == expected_values["LOB_EWT1"]["expected_sensor1_distance"], f"Sensor 1 distance is {app.sensor1_distance.cget("text")} instead of {expected_values["LOB_EWT1"]["expected_sensor1_distance"]}."
    assert app.sensor2_distance.cget("text") == expected_values["LOB_EWT1"]["expected_sensor2_distance"], f"Sensor 2 distance is {app.sensor2_distance.cget("text")} instead of {expected_values["LOB_EWT1"]["expected_sensor2_distance"]}."
    assert app.sensor3_distance.cget("text") == expected_values["LOB_EWT1"]["expected_sensor3_distance"], f"Sensor 3 distance is {app.sensor3_distance.cget("text")} instead of {expected_values["LOB_EWT1"]["expected_sensor3_distance"]}."
    assert app.target_error.cget("text") == expected_values["LOB_EWT1"]["expected_target_error"], f"Target error is {app.target_error.cget("text")} instead of {expected_values["LOB_EWT1"]["expected_target_error"]}."
    assert app.target_class == expected_values["LOB_EWT1"]["expected_target_class"], f"Target class is {app.target_class} instead of {expected_values["LOB_EWT1"]["expected_target_class"]}."
    assert app.target_coord == expected_values["LOB_EWT1"]["expected_target_coord"], f"Target coordinate is {app.target_coord} instead of {expected_values["LOB_EWT1"]["expected_target_coord"]}."
    assert app.target_mgrs == expected_values["LOB_EWT1"]["expected_target_mgrs"], f"Target MGRS is {app.target_mgrs} instead of {expected_values["LOB_EWT1"]["expected_target_mgrs"]}."

    # Clear the entries after the test
    app.button_clear_target_overlays.invoke()

def test_default_inputs_EWT2_LOB(app,default_inputs,expected_values):
    """Test default input in the GUI and their expected outputs"""

    # Insert default values into the entry fields
    app.button_clear_entries.invoke()
    app.update_idletasks()
    app.bypass_input_errors = True  # Bypass input errors for testing
    app.bypass_elevation_plot_prompt = True  # Bypass elevation plot prompt for testing

    app.sensor2_mgrs.insert(0, default_inputs["default_sensor2_mgrs"])
    app.sensor2_Rpwr.insert(0, default_inputs["default_sensor2_Rpwr"])
    app.sensor2_lob.insert(0, default_inputs["default_sensor2_lob"])
    app.frequency.insert(0, default_inputs["default_frequency"])
    app.min_ERP.insert(0, default_inputs["default_min_ERP"])
    app.max_ERP.insert(0, default_inputs["default_max_ERP"])
    app.option_path_loss_coeff.set(default_inputs["default_option_path_loss_coeff"])

    # Update UI to process the inserted values
    app.update_idletasks()

    # Run the calculation
    app.button_calculate.invoke()
    app.update_idletasks()
    time.sleep(1)

    # Check if the calculated values are displayed
    assert app.target_grid.cget("text") == expected_values["LOB_EWT2"]["expected_target_grid"], f"Target grid is {app.target_grid.cget("text")} instead of {expected_values["LOB_EWT2"]["expected_target_grid"]}."
    assert app.label_target_grid.cget("text") == expected_values["LOB_EWT2"]["expected_label_target_grid"], f"Label for target grid is {app.label_target_grid.cget("text")} instead of {expected_values["LOB_EWT2"]["expected_label_target_grid"]}."
    assert app.sensor1_distance.cget("text") == expected_values["LOB_EWT2"]["expected_sensor1_distance"], f"Sensor 1 distance is {app.sensor1_distance.cget("text")} instead of {expected_values["LOB_EWT2"]["expected_sensor1_distance"]}."
    assert app.sensor2_distance.cget("text") == expected_values["LOB_EWT2"]["expected_sensor2_distance"], f"Sensor 2 distance is {app.sensor2_distance.cget("text")} instead of {expected_values["LOB_EWT2"]["expected_sensor2_distance"]}."
    assert app.sensor3_distance.cget("text") == expected_values["LOB_EWT2"]["expected_sensor3_distance"], f"Sensor 3 distance is {app.sensor3_distance.cget("text")} instead of {expected_values["LOB_EWT2"]["expected_sensor3_distance"]}."
    assert app.target_error.cget("text") == expected_values["LOB_EWT2"]["expected_target_error"], f"Target error is {app.target_error.cget("text")} instead of {expected_values["LOB_EWT2"]["expected_target_error"]}."
    assert app.target_class == expected_values["LOB_EWT2"]["expected_target_class"], f"Target class is {app.target_class} instead of {expected_values["LOB_EWT2"]["expected_target_class"]}."
    assert app.target_coord == expected_values["LOB_EWT2"]["expected_target_coord"], f"Target coordinate is {app.target_coord} instead of {expected_values["LOB_EWT2"]["expected_target_coord"]}."
    assert app.target_mgrs == expected_values["LOB_EWT2"]["expected_target_mgrs"], f"Target MGRS is {app.target_mgrs} instead of {expected_values["LOB_EWT2"]["expected_target_mgrs"]}."

    # Clear the entries after the test
    app.button_clear_target_overlays.invoke()


def test_default_inputs_EWT3_LOB(app,default_inputs,expected_values):
    """Test default input in the GUI and their expected outputs"""
    
    # Insert default values into the entry fields
    app.button_clear_entries.invoke()
    app.update_idletasks()
    app.bypass_input_errors = True  # Bypass input errors for testing
    app.bypass_elevation_plot_prompt = True  # Bypass elevation plot prompt for testing

    app.sensor3_mgrs.insert(0, default_inputs["default_sensor3_mgrs"])
    app.sensor3_Rpwr.insert(0, default_inputs["default_sensor3_Rpwr"])
    app.sensor3_lob.insert(0, default_inputs["default_sensor3_lob"])
    app.frequency.insert(0, default_inputs["default_frequency"])
    app.min_ERP.insert(0, default_inputs["default_min_ERP"])
    app.max_ERP.insert(0, default_inputs["default_max_ERP"])
    app.option_path_loss_coeff.set(default_inputs["default_option_path_loss_coeff"])

    # Update UI to process the inserted values
    app.update_idletasks()

    # Run the calculation
    app.button_calculate.invoke()
    app.update_idletasks()
    time.sleep(1)

    # Check if the calculated values are displayed
    assert app.target_grid.cget("text") == expected_values["LOB_EWT3"]["expected_target_grid"], f"Target grid is {app.target_grid.cget("text")} instead of {expected_values["LOB_EWT3"]["expected_target_grid"]}."
    assert app.label_target_grid.cget("text") == expected_values["LOB_EWT3"]["expected_label_target_grid"], f"Label for target grid is {app.label_target_grid.cget("text")} instead of {expected_values["LOB_EWT3"]["expected_label_target_grid"]}."
    assert app.sensor1_distance.cget("text") == expected_values["LOB_EWT3"]["expected_sensor1_distance"], f"Sensor 1 distance is {app.sensor1_distance.cget("text")} instead of {expected_values["LOB_EWT3"]["expected_sensor1_distance"]}."
    assert app.sensor2_distance.cget("text") == expected_values["LOB_EWT3"]["expected_sensor2_distance"], f"Sensor 2 distance is {app.sensor2_distance.cget("text")} instead of {expected_values["LOB_EWT3"]["expected_sensor2_distance"]}."
    assert app.sensor3_distance.cget("text") == expected_values["LOB_EWT3"]["expected_sensor3_distance"], f"Sensor 3 distance is {app.sensor3_distance.cget("text")} instead of {expected_values["LOB_EWT3"]["expected_sensor3_distance"]}."
    assert app.target_error.cget("text") == expected_values["LOB_EWT3"]["expected_target_error"], f"Target error is {app.target_error.cget("text")} instead of {expected_values["LOB_EWT3"]["expected_target_error"]}."
    assert app.target_class == expected_values["LOB_EWT3"]["expected_target_class"], f"Target class is {app.target_class} instead of {expected_values["LOB_EWT3"]["expected_target_class"]}."
    assert app.target_coord == expected_values["LOB_EWT3"]["expected_target_coord"], f"Target coordinate is {app.target_coord} instead of {expected_values["LOB_EWT3"]["expected_target_coord"]}."
    assert app.target_mgrs == expected_values["LOB_EWT3"]["expected_target_mgrs"], f"Target MGRS is {app.target_mgrs} instead of {expected_values["LOB_EWT3"]["expected_target_mgrs"]}."

    # Clear the entries after the test
    app.button_clear_target_overlays.invoke()


def test_default_inputs_EWT1_EWT2_CUT(app,default_inputs,expected_values):
    """Test default input in the GUI and their expected outputs"""
    
    # Insert default values into the entry fields
    app.button_clear_entries.invoke()
    app.update_idletasks()
    app.bypass_input_errors = True  # Bypass input errors for testing
    app.bypass_elevation_plot_prompt = True  # Bypass elevation plot prompt for testing

    app.sensor1_mgrs.insert(0, default_inputs["default_sensor1_mgrs"])
    app.sensor1_Rpwr.insert(0, default_inputs["default_sensor1_Rpwr"])
    app.sensor1_lob.insert(0, default_inputs["default_sensor1_lob"])
    app.sensor2_mgrs.insert(0, default_inputs["default_sensor2_mgrs"])
    app.sensor2_Rpwr.insert(0, default_inputs["default_sensor2_Rpwr"])
    app.sensor2_lob.insert(0, default_inputs["default_sensor2_lob"])
    app.frequency.insert(0, default_inputs["default_frequency"])
    app.min_ERP.insert(0, default_inputs["default_min_ERP"])
    app.max_ERP.insert(0, default_inputs["default_max_ERP"])
    app.option_path_loss_coeff.set(default_inputs["default_option_path_loss_coeff"])

    # Update UI to process the inserted values
    app.update_idletasks()

    # Run the calculation
    app.button_calculate.invoke()
    app.update_idletasks()
    time.sleep(1)

    # Check if the calculated values are displayed
    assert app.target_grid.cget("text") == expected_values["CUT_EWT1_EWT2"]["expected_target_grid"], f"Target grid is {app.target_grid.cget("text")} instead of {expected_values["CUT_EWT1_EWT2"]["expected_target_grid"]}."
    assert app.label_target_grid.cget("text") == expected_values["CUT_EWT1_EWT2"]["expected_label_target_grid"], f"Label for target grid is {app.label_target_grid.cget("text")} instead of {expected_values["CUT_EWT1_EWT2"]["expected_label_target_grid"]}."
    assert app.sensor1_distance.cget("text") == expected_values["CUT_EWT1_EWT2"]["expected_sensor1_distance"], f"Sensor 1 distance is {app.sensor1_distance.cget("text")} instead of {expected_values["CUT_EWT1_EWT2"]["expected_sensor1_distance"]}."
    assert app.sensor2_distance.cget("text") == expected_values["CUT_EWT1_EWT2"]["expected_sensor2_distance"], f"Sensor 2 distance is {app.sensor2_distance.cget("text")} instead of {expected_values["CUT_EWT1_EWT2"]["expected_sensor2_distance"]}."
    assert app.sensor3_distance.cget("text") == expected_values["CUT_EWT1_EWT2"]["expected_sensor3_distance"], f"Sensor 3 distance is {app.sensor3_distance.cget("text")} instead of {expected_values["CUT_EWT1_EWT2"]["expected_sensor3_distance"]}."
    assert app.target_error.cget("text") == expected_values["CUT_EWT1_EWT2"]["expected_target_error"], f"Target error is {app.target_error.cget("text")} instead of {expected_values["CUT_EWT1_EWT2"]["expected_target_error"]}."
    assert app.target_class == expected_values["CUT_EWT1_EWT2"]["expected_target_class"], f"Target class is {app.target_class} instead of {expected_values["FCUT_EWT1_EWT2ix"]["expected_target_class"]}."
    assert app.target_coord == expected_values["CUT_EWT1_EWT2"]["expected_target_coord"], f"Target coordinate is {app.target_coord} instead of {expected_values["CUT_EWT1_EWT2"]["expected_target_coord"]}."
    assert app.target_mgrs == expected_values["CUT_EWT1_EWT2"]["expected_target_mgrs"], f"Target MGRS is {app.target_mgrs} instead of {expected_values["CUT_EWT1_EWT2"]["expected_target_mgrs"]}."

    # Clear the entries after the test
    app.button_clear_target_overlays.invoke()


def test_default_inputs_EWT1_EWT3_CUT(app,default_inputs,expected_values):
    pass

def test_default_inputs_EWT2_EWT3_CUT(app,default_inputs,expected_values):
    pass

def test_default_inputs_fix(app,default_inputs,expected_values):
    """Test default input in the GUI and their expected outputs"""
    
    # Insert default values into the entry fields
    app.button_clear_entries.invoke()
    app.update_idletasks()
    app.bypass_input_errors = True  # Bypass input errors for testing
    app.bypass_elevation_plot_prompt = True  # Bypass elevation plot prompt for testing

    app.sensor1_mgrs.insert(0, default_inputs["default_sensor1_mgrs"])
    app.sensor1_Rpwr.insert(0, default_inputs["default_sensor1_Rpwr"])
    app.sensor1_lob.insert(0, default_inputs["default_sensor1_lob"])
    app.sensor2_mgrs.insert(0, default_inputs["default_sensor2_mgrs"])
    app.sensor2_Rpwr.insert(0, default_inputs["default_sensor2_Rpwr"])
    app.sensor2_lob.insert(0, default_inputs["default_sensor2_lob"])
    app.sensor3_mgrs.insert(0, default_inputs["default_sensor3_mgrs"])
    app.sensor3_Rpwr.insert(0, default_inputs["default_sensor3_Rpwr"])
    app.sensor3_lob.insert(0, default_inputs["default_sensor3_lob"])
    app.frequency.insert(0, default_inputs["default_frequency"])
    app.min_ERP.insert(0, default_inputs["default_min_ERP"])
    app.max_ERP.insert(0, default_inputs["default_max_ERP"])
    app.option_path_loss_coeff.set(default_inputs["default_option_path_loss_coeff"])

    # Update UI to process the inserted values
    app.update_idletasks()

    # Run the calculation
    app.button_calculate.invoke()
    app.update_idletasks()
    time.sleep(1)

    # Check if the calculated values are displayed
    assert app.target_grid.cget("text") == expected_values["Fix"]["expected_target_grid"], f"Target grid is {app.target_grid.cget("text")} instead of {expected_values["Fix"]["expected_target_grid"]}."
    assert app.label_target_grid.cget("text") == expected_values["Fix"]["expected_label_target_grid"], f"Label for target grid is {app.label_target_grid.cget("text")} instead of {expected_values["Fix"]["expected_label_target_grid"]}."
    assert app.sensor1_distance.cget("text") == expected_values["Fix"]["expected_sensor1_distance"], f"Sensor 1 distance is {app.sensor1_distance.cget("text")} instead of {expected_values["Fix"]["expected_sensor1_distance"]}."
    assert app.sensor2_distance.cget("text") == expected_values["Fix"]["expected_sensor2_distance"], f"Sensor 2 distance is {app.sensor2_distance.cget("text")} instead of {expected_values["Fix"]["expected_sensor2_distance"]}."
    assert app.sensor3_distance.cget("text") == expected_values["Fix"]["expected_sensor3_distance"], f"Sensor 3 distance is {app.sensor3_distance.cget("text")} instead of {expected_values["Fix"]["expected_sensor3_distance"]}."
    assert app.target_error.cget("text") == expected_values["Fix"]["expected_target_error"], f"Target error is {app.target_error.cget("text")} instead of {expected_values["Fix"]["expected_target_error"]}."
    assert app.target_class == expected_values["Fix"]["expected_target_class"], f"Target class is {app.target_class} instead of {expected_values["Fix"]["expected_target_class"]}."
    assert app.target_coord == expected_values["Fix"]["expected_target_coord"], f"Target coordinate is {app.target_coord} instead of {expected_values["Fix"]["expected_target_coord"]}."
    assert app.target_mgrs == expected_values["Fix"]["expected_target_mgrs"], f"Target MGRS is {app.target_mgrs} instead of {expected_values["Fix"]["expected_target_mgrs"]}."

    # Clear the entries after the test
    app.button_clear_target_overlays.invoke()

