import csv
from pathlib import Path
from datetime import datetime
from .imu_data import IMUData


class DataLogger:
    
    def __init__(self, filename: str = None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_log_{timestamp}.csv"
        
        self.filename = filename
        self.file = None
        self.writer = None
        self._write_header()
    
    def _write_header(self):
        with open(self.filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time', 'Roll', 'Gyro Rate', 'Servo Position'])
    
    def log(self, data: IMUData):
        try:
            with open(self.filename, 'a', newline='') as f:
                writer = csv.writer(f)
                timestamp = data.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                writer.writerow([timestamp, data.roll, data.gyro_rate, data.servo_pos])
        except Exception as e:
            print(f"Error logging data: {e}")
    
    def get_filename(self) -> str:
        return self.filename
