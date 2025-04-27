import serial
import serial.tools.list_ports
import time
import json
import os
from datetime import datetime, UTC
from pathlib import Path
import mgrs
import threading
import winreg
import win32com.client
import usb.core
import usb.util
from coords import convert_coords_to_mgrs
from logger import LoggerManager
import logging
from utilities import read_json

class PositioningService:
    def __init__(self, interval=30):
        conf = read_json(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config_files", "conf.json"))
        self.src_dir = os.path.dirname(os.path.abspath(__file__))
        self.logs_dir = Path(os.path.join(os.path.dirname(self.src_dir), conf["DIR_RELATIVE_LOGS_EUD_POSITION"]))
        self.interval = interval
        self.latest_position = None
        self.mgrs_converter = mgrs.MGRS()
        self.logger = LoggerManager.get_logger(
                    name="eud_position",
                    category="app",
                    level=logging.INFO)
        self.device_type, self.port, self.baudrate = self.find_gnss_port()
        self._stop_event = threading.Event()

    def coordinate_format_conversion(self, lat: str, lat_dir, lon, lon_dir):
        try:
            lat = str(lat)
            lon = str(lon)
            lat_var1 = lat[:2]
            lat_var2 = lat[2:]
            lat_var3 = float(lat_var2) / 60
            lat_new = f"{lat_var1}.{str(lat_var3).split('.')[-1]}"
            if lat_dir == 'S':
                lat_new = f"-{float(lat_new)}"
            lon_var1 = lon[:3]
            lon_var2 = lon[3:]
            lon_var3 = float(lon_var2) / 60
            lon_new = f"{lon_var1}.{str(lon_var3).split('.')[-1]}"
            if lon_dir == 'W':
                lon_new = f"-{float(lon_new)}"
        except Exception as e:
            self.logger.error(f"Coordinate conversion error: {e}")
            self.logger.debug(f"Original coordinates: {lat}, {lat_dir}, {lon}, {lon_dir}")
            return None, None
        return float(lat_new), float(lon_new)

    def find_gnss_port(self):
        # Step 1: List all COM ports
        ports = serial.tools.list_ports.comports()
        self.logger.info(f"Available ports: {[p.device for p in ports]}")

        # Step 2: Try to identify u-blox by port description
        for port_info in ports:
            port = port_info.device
            if 'u-blox' in port_info.description.lower():
                self.logger.info(f"Found u-blox GNSS device: {port} | {port_info.description}")
                return "serial", port, 9600

        # Step 3: Check for u-blox GNSS sensor in Windows Device Manager
        try:
            wmi = win32com.client.GetObject("winmgmts:")
            for sensor in wmi.InstancesOf("Win32_PnPEntity"):
                sensor_name = sensor.Name if sensor.Name else ""
                if sensor_name and 'u-blox' in sensor_name.lower() and 'gnss' in sensor_name.lower():
                    self.logger.info(f"Found u-blox GNSS sensor: {sensor_name}")
                    # Check if a COM port is associated
                    port = self.get_com_port_from_registry(sensor.DeviceID)
                    if port:
                        self.logger.info(f"Associated COM port: {port}")
                        return "serial", port, 9600
                    else:
                        self.logger.warning("No COM port associated with u-blox GNSS sensor.")
                        if self.is_location_api_available():
                            return "sensor", None, None
                        else:
                            self.logger.warning("Windows Location API unavailable; checking USB interface.")
                            if self.find_usb_device():
                                return "usb", None, None
                            else:
                                self.logger.warning("No USB GNSS device found.")
                                return None, None, None
        except Exception as e:
            print(f"Error checking sensors: {e}")

        # Step 4: Fallback to scanning for GGA sentences
        common_baud_rates = [9600, 38400, 115200]
        for port_info in ports:
            port = port_info.device
            print(f"Trying port: {port} | {port_info.description}")
            for baudrate in common_baud_rates:
                try:
                    with serial.Serial(port, baudrate, timeout=1) as ser:
                        for _ in range(5):
                            line = ser.readline().decode('utf-8', errors='ignore').strip()
                            if line.startswith('$GPGGA'):
                                print(f"Detected GNSS on {port} at {baudrate} baud")
                                return "serial", port, baudrate
                except Exception as e:
                    continue
        self.logger.warning("No GNSS device found.")
        return None, None, None

    def is_location_api_available(self):
        """Check if Windows Location API is available."""
        try:
            win32com.client.Dispatch("LocationDisp.Geolocation")
            return True
        except Exception as e:
            self.logger.warning(f"Location API not available: {e}")
            return False

    def find_usb_device(self):
        """Find u-blox USB device by VID:PID (u-blox VID is 0x1546)."""
        try:
            dev = usb.core.find(idVendor=0x1546) # u-blox Vendor ID
            if dev is None:
                self.logger.warning("No u-blox USB device found.")
                return False
            self.logger.info(f"Found u-blox USB device: VID={hex(dev.idVendor)}, PID={hex(dev.idProduct)}")
            return True
        except usb.core.NoBackendError:
            self.logger.error("No USB backend available. Install libusb or WinUSB using Zadig.")
            return False
        except Exception as e:
            self.logger.error(f"Error finding USB device: {e}")
            return False

    def get_com_port_from_registry(self, device_id):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Enum")
            subkey = winreg.OpenKey(key, device_id)
            for i in range(winreg.QueryInfoKey(subkey)[1]):
                name, value, _ = winreg.EnumValue(subkey, i)
                if name == "FriendlyName" and "COM" in value:
                    com_port = value.split("(COM")[1].split(")")[0]
                    return f"COM{com_port}"
            winreg.CloseKey(subkey)
            winreg.CloseKey(key)
        except Exception as e:
            self.logger.error(f"Error accessing registry for COM port: {e}")
        return None

    def get_gnss_data_from_sensor(self, max_time_seconds=15):
        try:
            locator = win32com.client.Dispatch("LocationDisp.Geolocation")
            start_time = time.time()
            while time.time() - start_time < max_time_seconds:
                location = locator.GetLatLongReport()
                if location.Status == 1:  # Valid report
                    latitude = location.Latitude
                    longitude = location.Longitude
                    altitude = location.Altitude if hasattr(location, 'Altitude') else None
                    timestamp = location.Timestamp if hasattr(location, 'Timestamp') else datetime.now(UTC).strftime("%H%M%S")
                    gps_data = {
                        'utc': timestamp,
                        'lat': latitude,
                        'lon': longitude,
                        'mgrs': convert_coords_to_mgrs([latitude, longitude]),
                        'num_sats': None,  # Windows API may not provide satellite count
                        'alt_m': altitude if altitude else None
                    }
                    return gps_data
                time.sleep(1)
            self.logger.warning("No valid GNSS data from sensor within timeout.")  
            return None
        except Exception as e:
            self.logger.error(f"Error reading GNSS sensor data: {e}")
            return None

    def get_gnss_data_from_usb(self, max_time_seconds=15):
        """Placeholder for reading NMEA data from u-blox USB device."""
        try:
            dev = usb.core.find(idVendor=0x1546)
            if dev is None:
                self.logger.warning("No u-blox USB device found.")
                return None
            # Detach kernel driver if active
            if dev.is_kernel_driver_active(0):
                dev.detach_kernel_driver(0)
            # Set configuration
            dev.set_configuration()
            # Find endpoint (assuming bulk or interrupt for NMEA data)
            cfg = dev.get_active_configuration()
            intf = cfg[(0, 0)]
            endpoint = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
            )
            if endpoint is None:
                self.logger.error("No suitable USB endpoint found.")
                return None
            # Read data
            start_time = time.time()
            while time.time() - start_time < max_time_seconds:
                try:
                    data = dev.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize, timeout=1000)
                    line = ''.join([chr(x) for x in data]).strip()
                    if line.startswith('$GPGGA'):
                        data = line.split(',')
                        if len(data) >= 10 and data[2] and data[4]:
                            utc = data[1]
                            lat_DDDmm = data[2]
                            lat_dir = data[3]
                            lon_DDmm = data[4]
                            lon_dir = data[5]
                            lat, lon = self.coordinate_format_conversion(lat_DDDmm, lat_dir, lon_DDmm, lon_dir)
                            if lat is None or lon is None:
                                continue
                            num_sats = data[7]
                            alt = data[9]
                            mgrs_coord = convert_coords_to_mgrs([lat, lon])
                            gps_data = {
                                'utc': utc,
                                'lat': lat,
                                'lon': lon,
                                'mgrs': mgrs_coord,
                                'num_sats': num_sats,
                                'alt_m': alt
                            }
                            return gps_data
                except usb.core.USBError:
                    self.logger.error("USB read error. Device may be disconnected.")
                    continue
            print("No valid GNSS data from USB within timeout.")
            self.logger.warning("No valid GNSS data from USB within timeout.")
            return
        except usb.core.NoBackendError:
            self.logger.error("No USB backend available. Install libusb or WinUSB using Zadig.")
            return None
        except Exception as e:
            self.logger.error(f"Error reading USB GNSS data: {e}")
            return None

    def generate_EUD_coordinate(self, max_time_seconds=15):
        if self.device_type == "serial" and self.port:
            try:
                with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                    start_time = time.time()
                    while time.time() - start_time < max_time_seconds:
                        try:
                            line = ser.readline().decode('utf-8', errors='ignore').strip()
                        except UnicodeDecodeError:
                            continue
                        if line.startswith('$GPGGA'):
                            data = line.split(',')
                            if len(data) >= 10 and data[2] and data[4]:
                                utc = data[1]
                                lat_DDDmm = data[2]
                                lat_dir = data[3]
                                lon_DDmm = data[4]
                                lon_dir = data[5]
                                lat, lon = self.coordinate_format_conversion(lat_DDDmm, lat_dir, lon_DDmm, lon_dir)
                                if lat is None or lon is None:
                                    continue
                                num_sats = data[7]
                                alt = data[9]
                                mgrs_coord = convert_coords_to_mgrs([lat, lon])
                                gps_data = {
                                    'utc': utc,
                                    'lat': lat,
                                    'lon': lon,
                                    'mgrs': mgrs_coord,
                                    'num_sats': num_sats,
                                    'alt_m': alt
                                }
                                return gps_data
            except Exception as e:
                self.logger.error(f"Error reading GNSS serial data: {e}")
                return
        elif self.device_type == "sensor":
            return self.get_gnss_data_from_sensor(max_time_seconds)
        elif self.device_type == "usb":
            return self.get_gnss_data_from_usb(max_time_seconds)
        else:
            self.logger.warning("No GNSS device type detected.")
            return 

    def get_log_filename(self):
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now(UTC).strftime("%Y-%m-%d")
        return self.logs_dir / f'position_log_{date_str}.jsonl'

    def _log_position_to_file(self):
        from coords import format_readable_mgrs
        try:
            filename = self.get_log_filename()
            with open(filename, 'a') as f:
                f.write(json.dumps(self.latest_position) + '\n')
            self.logger.info(f"Logged position: {format_readable_mgrs(self.latest_position['data']['mgrs'])}")
        except Exception as e:
            print(f"Failed to write to log file: {e}")
            self.logger.error(f"Failed to write to log file: {e}")

    def poll_location(self):
        while not self._stop_event.is_set():
            position = self.generate_EUD_coordinate()
            if position:
                timestamp = datetime.now(UTC).isoformat()
                entry = {
                    'timestamp': timestamp,
                    'data': position
                }
                self.latest_position = entry
                self._log_position_to_file(entry)
            self._stop_event.wait(self.interval)

    def start(self):
        self._stop_event.clear()
        threading.Thread(target=self.poll_location, daemon=True).start()

    def stop(self):
        print("Positioning service stopping.")
        self._stop_event.set()

    def get_latest_position_from_logs(self):
        log_files = sorted(Path(self.logs_dir).glob("position_log_*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        return json.loads(lines[-1])
            except:
                continue
        return None

if __name__ == "__main__":
    service = PositioningService(interval=30)
    service.start()
    sleep_interval = 15
    try:
        while True:
            time.sleep(sleep_interval)
            latest = service.get_latest_position_from_logs()
            if latest:
                print("Latest logged position:", latest)
            if service.device_type is None:
                print("No GNSS device found. Exiting...")
                service.stop()
                break
    except KeyboardInterrupt:
        service.stop()
    time.sleep(1000)