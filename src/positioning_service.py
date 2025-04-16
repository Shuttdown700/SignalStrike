import serial
import serial.tools.list_ports
import time
import json
from datetime import datetime
from pathlib import Path
import mgrs
import threading
from datetime import datetime, UTC
from coords import convert_coords_to_mgrs

class PositioningService:
    def __init__(self, interval=30):
        self.interval = interval
        self.latest_position = None
        self.port, self.baudrate = self.find_gnss_port()
        self.mgrs_converter = mgrs.MGRS()
        self._stop_event = threading.Event()

    def coordinate_format_conversion(self,lat,lat_dir,lon,lon_dir):
        try:
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
        except Exception as e:
            print(f"Coordinate conversion error: {e}")
            print('Inputs: ',lat,lat_dir,lon,lon_dir)
            return None, None

        return lat_new, lon_new

    def find_gnss_port(self):
        ports = serial.tools.list_ports.comports()
        print(f"All available ports: {[p.device for p in ports]}")

        # Priority: try to identify a u-blox device from the description
        for port_info in ports:
            port = port_info.device
            if 'u-blox' in port_info.description.lower():
                print(f"Likely GNSS device detected by name: {port} | {port_info.description}")
                return port, 9600

        # If nothing obvious, try scanning ports for GGA NMEA sentences
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
                                return port, baudrate
                except Exception as e:
                    continue
        print("GNSS serial port not found.")
        return None, None

    def get_log_filename(self):
        logs_dir = Path(__file__).resolve().parent.parent / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now(UTC).strftime("%Y-%m-%d")
        return logs_dir / f'position_log_{date_str}.jsonl'

    def _log_to_file(self, entry):
        try:
            filename = self.get_log_filename()
            with open(filename, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            print(f"Failed to write to log file: {e}")

    def generate_EUD_coordinate(self, max_time_seconds=15):
        if not self.port:
            print("No serial port available for GNSS.")
            return None
        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                while True:
                    try:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()  # Decode bytes to UTF-8 string
                    except UnicodeDecodeError:
                        continue  # Skip decoding errors and try to read the next line
                    if line.startswith('$GPGGA'):
                        data = line.split(',')
                        print(print(f'GNSS Data:\n {data}'))
                        if len(data) >= 10 and data[2] and data[4]:
                            utc = data[1]
                            print(f'UTC: {utc}')
                            lat_DDDmm = data[2]
                            lat_dir = data[3]
                            print(f'Latitude (DDD.mm format): {lat_DDDmm} {lat_dir}')
                            lon_DDmm = data[4]
                            lon_dir = data[5]
                            print(f'Longitude (DDD.mm format): {lon_DDmm} {lon_dir}')
                            lat, lon = self.coordinate_format_conversion(lat_DDDmm, lat_dir, lon_DDmm, lon_dir)
                            print(f'Coordinate (lat,lon): {lat,lon}')
                            num_sats = data[7]
                            print(f'Number of Satellites: {num_sats}')
                            alt = data[9]
                            print(f'Altitude: {alt}')
                            mgrs_coord = convert_coords_to_mgrs(lat, lon)
                            print(f'MGRS Coordinate: {mgrs_coord}')
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
            print(f"Error reading GNSS data: {e}")
        return None

    def poll_location(self):
        while not self._stop_event.is_set():
            position = self.generate_EUD_coordinate()
            if position:
                timestamp = datetime.utcnow().isoformat()
                entry = {
                    'timestamp': timestamp,
                    'data': position
                }
                self.latest_position = entry
                self._log_to_file(entry)
            self._stop_event.wait(self.interval)

    def start(self):
        self._stop_event.clear()
        threading.Thread(target=self.poll_location, daemon=True).start()

    def stop(self):
        self._stop_event.set()

    def get_latest_position_from_logs(self):
        log_files = sorted(Path('.').glob('position_log_*.jsonl'), reverse=True)
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

    try:
        while True:
            time.sleep(10)
            latest = service.get_latest_position_from_logs()
            if latest:
                print("Latest logged position:", latest)
    except KeyboardInterrupt:
        service.stop()
        print("Positioning service stopped.")
