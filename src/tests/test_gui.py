
# test_app.py
import os, sys, unittest
from unittest.mock import patch
from colored_test_runner import ColoredTextTestRunner
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gui import App

# ANSI color codes for text
RESET = "\033[0m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"

class TestApp(unittest.TestCase):
    def setUp(self):
        # Create an instance of your App
        self.app = App()

    def tearDown(self):
        # Clean up after each test
        self.app.destroy()     

    def test_add_and_clear_user_markers(self, print_bool=True):
        self.assertEqual(len(self.app.user_marker_list), 0, "The user marker list should initialize with 0 objects.")
        if print_bool: print(f"{GREEN}\nInitial marker count: {len(self.app.user_marker_list)}{RESET}")
        self.app.add_marker_event(coord=[31.88433987652714, -81.61455308068548])
        if print_bool: print(f"{YELLOW}User marker added. Current count: {len(self.app.user_marker_list)}{RESET}")
        self.assertEqual(len(self.app.user_marker_list), 1, "User markers should contain 1 object after adding a user marker.")
        if print_bool: print(f"{GREEN}User marker count: {len(self.app.user_marker_list)}{RESET}")
        self.app.add_marker_event(coord=[31.890242984927013, -81.59223710246293],bool_bypass_measurement=True,bool_bypass_log=True)
        if print_bool: print(f"{YELLOW}User marker added. Current count: {len(self.app.user_marker_list)}{RESET}")
        self.assertEqual(len(self.app.user_marker_list), 2, "User markers should contain 2 objects after adding a second user marker.")
        if print_bool: print(f"{GREEN}User marker count: {len(self.app.user_marker_list)}{RESET}")
        self.assertEqual(len(self.app.path_list), 2, "Path marker list should contain 2 path objects (line & label) after adding a second user marker.")
        if print_bool: print(f"{GREEN}Path object count: {len(self.app.path_list)}{RESET}")
        self.app.button_clear_markers.invoke()
        if print_bool: print(f"{YELLOW}User markers cleared. Current count: {len(self.app.user_marker_list)}{RESET}")
        self.assertEqual(len(self.app.user_marker_list), 0, "User markers should be empty after clearing.")
        if print_bool: print(f"{GREEN}User marker count: {len(self.app.user_marker_list)}{RESET}")
        self.assertEqual(len(self.app.path_list), 0, "Path marker list should be empty after clearing.")
        if print_bool: print(f"{GREEN}Path object count: {len(self.app.path_list)}{RESET}")
        self.assertEqual(len(self.app.eud_marker_list), 0, "EUD marker list should be empty after clearing.")
        if print_bool: print(f"{GREEN}EUD marker count: {len(self.app.eud_marker_list)}{RESET}")
    
    def input_single_LOBs(self,print_bool=True):
        pass

    def input_CUTs(self,print_bool=True):
        pass

    def input_FIX(self,print_bool=True):
        pass

if __name__ == "__main__":
    unittest.main(testRunner=ColoredTextTestRunner(),exit=False)
