import serial
import serial.tools.list_ports
import time
import json
from datetime import datetime
from pathlib import Path
import mgrs
import threading
from datetime import datetime, UTC

class PositioningService:
    def __init__(self, interval=30):
        self.interval = interval
        self.latest_position = None
        self.port, self.baudrate = self.find_gnss_port()
        self.mgrs_converter = mgrs.MGRS()
        self._stop_event = threading.Event()

    def coordinate_format_conversion(self, lat, lat_dir, lon, lon_dir):
        lat = str(lat)
        lon = str(lon)
        lat_deg = float(lat[:2]) + float(lat[2:]) / 60
        if lat_dir == 'S':
            lat_deg *= -1
        lon_deg = float(lon[:3]) + float(lon[3:]) / 60
        if lon_dir == 'W':
            lon_deg *= -1
        return lat_deg, lon_deg

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
                start_time = time.time()
                print(ser)
                print(ser.readline())
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line.startswith('$GPGGA'):
                    data = line.split(',')
                    print(data)
                    if len(data) >= 10 and data[2] and data[4]:
                        utc = data[1]
                        lat, lon = self.coordinate_format_conversion(data[2], data[3], data[4], data[5])
                        num_sats = data[7]
                        alt = data[9]
                        mgrs_coord = self.mgrs_converter.toMGRS(lat, lon).decode()

                        gps_data = {
                            'utc': utc,
                            'lat': lat,
                            'lon': lon,
                            'mgrs': mgrs_coord,
                            'num_sats': num_sats,
                            'alt_m': alt
                        }
                        print("GPS data:", gps_data)
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
