"""Data manager controller."""

from typing import Optional, Callable
from models import (
    IMUData, IConnection, SerialConnection, WiFiConnection,
    DataParser, DataSimulator, DataLogger
)


class DataManager:
    """Manager untuk mengelola koneksi, parsing, dan logging data."""
    
    def __init__(self):
        self.connection: Optional[IConnection] = None
        self.parser = DataParser()
        self.simulator = DataSimulator()
        self.logger: Optional[DataLogger] = None
        self.is_simulation = False
        self.data_callback: Optional[Callable[[IMUData], None]] = None
    
    def set_data_callback(self, callback: Callable[[IMUData], None]):
        """Set callback yang dipanggil saat ada data baru."""
        self.data_callback = callback
    
    def connect_serial(self, port: str) -> bool:
        """
        Koneksi ke serial port.
        
        Args:
            port: Nama port serial (e.g., "COM3")
            
        Returns:
            True jika berhasil connect
        """
        self.disconnect()
        self.connection = SerialConnection(port)
        self.is_simulation = False
        return self.connection.connect()
    
    def connect_wifi(self, host: str, port: int = 8888) -> bool:
        """
        Koneksi ke WiFi (TCP).
        
        Args:
            host: IP address ESP32
            port: Port TCP (default 8888)
            
        Returns:
            True jika berhasil connect
        """
        self.disconnect()
        self.connection = WiFiConnection(host, port)
        self.is_simulation = False
        return self.connection.connect()
    
    def start_simulation(self):
        """Mulai mode simulasi."""
        self.disconnect()
        self.is_simulation = True
    
    def disconnect(self):
        """Disconnect dari koneksi aktif."""
        if self.connection:
            self.connection.disconnect()
            self.connection = None
        self.is_simulation = False
    
    def is_connected(self) -> bool:
        """Cek apakah sedang connected atau simulation mode."""
        if self.is_simulation:
            return True
        return self.connection is not None and self.connection.is_connected()
    
    def start_logging(self, filename: str = None):
        """Mulai logging data ke CSV."""
        self.logger = DataLogger(filename)
    
    def stop_logging(self):
        """Stop logging data."""
        self.logger = None
    
    def is_logging(self) -> bool:
        """Cek apakah sedang logging."""
        return self.logger is not None
    
    def get_log_filename(self) -> Optional[str]:
        """Get nama file log yang sedang aktif."""
        return self.logger.get_filename() if self.logger else None
    
    def read_data(self) -> Optional[IMUData]:
        """
        Baca data dari koneksi atau simulator.
        
        Returns:
            IMUData object atau None jika tidak ada data
        """
        data = None
        
        # Simulasi mode
        if self.is_simulation:
            data = self.simulator.generate()
        
        # Real connection mode
        elif self.connection and self.connection.is_connected():
            line = self.connection.read_line()
            if line:
                data = self.parser.parse(line)
        
        # Log jika ada logger dan data valid
        if data and self.logger:
            self.logger.log(data)
        
        # Call callback jika ada data dan callback terdaftar
        if data and self.data_callback:
            self.data_callback(data)
        
        return data
