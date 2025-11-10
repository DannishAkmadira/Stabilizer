"""Data logging functionality."""

import csv
from pathlib import Path
from datetime import datetime
from .imu_data import IMUData


class DataLogger:
    """Logger untuk menyimpan data ke file CSV."""
    
    def __init__(self, filename: str = None):
        """
        Inisialisasi logger.
        
        Args:
            filename: Nama file CSV. Jika None, akan generate otomatis.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data_log_{timestamp}.csv"
        
        self.filename = filename
        self.file = None
        self.writer = None
        self._write_header()
    
    def _write_header(self):
        """Tulis header CSV."""
        with open(self.filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time', 'Roll', 'Gyro Rate', 'Servo Position'])
    
    def log(self, data: IMUData):
        """
        Log data ke CSV.
        
        Args:
            data: IMUData object yang akan disimpan
        """
        try:
            with open(self.filename, 'a', newline='') as f:
                writer = csv.writer(f)
                timestamp = data.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                writer.writerow([timestamp, data.roll, data.gyro_rate, data.servo_pos])
        except Exception as e:
            print(f"Error logging data: {e}")
    
    def get_filename(self) -> str:
        """Get nama file log."""
        return self.filename
