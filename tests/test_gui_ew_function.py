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
        "Fix": {
            "expected_target_grid": "11SNV 43462 09939",
            "expected_label_target_grid": "TARGET GRID (FIX)",
            "expected_sensor1_distance": "1.72km",
            "expected_sensor2_distance": "1.17km",
            "expected_sensor3_distance": "3.06km",
            "expected_target_error": "30 acres",
            "expected_target_class": "(FIX)",
            "expected_target_coord": [35.33176040852016, -116.52176949951918],
            "expected_target_mgrs": "11SNV4346209939"
        }
    }

@pytest.fixture(scope="module")
def app():
    """Initialize the CustomTkinter app for testing in the main thread."""
    app_instance = App()
    app_instance.update_idletasks()  # Process UI events
    app_instance.update()  # Ensure widgets are rendered
    yield app_instance
    app_instance.button_clear_markers.invoke()
    app_instance.button_clear_tactical_graphics.invoke()
    app_instance.button_clear_measurements.invoke()
    app_instance.button_clear_entries.invoke()
    app_instance.destroy()

def test_attribute_existence(app):
    # Check if the EWT user inputs are present in the GUI
    assert hasattr(app, "sensor1_mgrs"), "sensor1_mgrs entry field not found in App."
    assert hasattr(app, "sensor1_Rpwr"), "sensor1_Rpwr entry field not found in App."
    assert hasattr(app, "sensor1_lob"), "sensor1_lob entry field not found in App."
    assert hasattr(app, "sensor2_mgrs"), "sensor2_mgrs entry field not found in App."
    assert hasattr(app, "sensor2_Rpwr"), "sensor2_Rpwr entry field not found in App."
    assert hasattr(app, "sensor2_lob"), "sensor2_lob entry field not found in App."
    assert hasattr(app, "sensor3_mgrs"), "sensor3_mgrs entry field not found in App."
    assert hasattr(app, "sensor3_Rpwr"), "sensor3_Rpwr entry field not found in App."
    assert hasattr(app, "sensor3_lob"), "sensor3_lob entry field not found in App."
    assert hasattr(app, "frequency"), "frequency entry field not found in App."
    assert hasattr(app, "min_ERP"), "min_erp entry field not found in App."
    assert hasattr(app, "max_ERP"), "max_erp entry field not found in App."
    assert hasattr(app, "option_path_loss_coeff"), "option_path_loss_coeff entry field not found in App."

def test_default_inputs_fix(app,default_inputs,expected_values):
    """Test default input in the GUI and their expected outputs"""
    
    # Insert default values into the entry fields
    app.button_clear_entries.invoke()
    app.update_idletasks()

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
    assert app.target_grid.cget("text") == expected_values["Fix"]["expected_target_grid"], f"Target grid is {app.target_grid} instead of {expected_values["Fix"]["expected_target_grid"]}."
    assert app.label_target_grid.cget("text") == expected_values["Fix"]["expected_label_target_grid"], f"Label for target grid is {app.label_target_grid} instead of {expected_values["Fix"]["expected_label_target_grid"]}."
    assert app.sensor1_distance.cget("text") == expected_values["Fix"]["expected_sensor1_distance"], f"Sensor 1 distance is {app.sensor1_distance} instead of {expected_values["Fix"]["expected_sensor1_distance"]}."
    assert app.sensor2_distance.cget("text") == expected_values["Fix"]["expected_sensor2_distance"], f"Sensor 2 distance is {app.sensor2_distance} instead of {expected_values["Fix"]["expected_sensor2_distance"]}."
    assert app.sensor3_distance.cget("text") == expected_values["Fix"]["expected_sensor3_distance"], f"Sensor 3 distance is {app.sensor3_distance} instead of {expected_values["Fix"]["expected_sensor3_distance"]}."
    assert app.target_error.cget("text") == expected_values["Fix"]["expected_target_error"], f"Target error is {app.target_error} instead of {expected_values["Fix"]["expected_target_error"]}."
    assert app.target_class == expected_values["Fix"]["expected_target_class"], f"Target class is {app.target_class} instead of {expected_values["Fix"]["expected_target_class"]}."
    assert app.target_coord == expected_values["Fix"]["expected_target_coord"], f"Target coordinate is {app.target_coord} instead of {expected_values["Fix"]["expected_target_coord"]}."
    assert app.target_mgrs == expected_values["Fix"]["expected_target_mgrs"], f"Target MGRS is {app.target_mgrs} instead of {expected_values["Fix"]["expected_target_mgrs"]}."

