"""Connection interfaces and implementations."""

from abc import ABC, abstractmethod
from typing import Optional
import serial
import serial.tools.list_ports
import socket


class IConnection(ABC):
    """Interface untuk koneksi data."""
    
    @abstractmethod
    def connect(self) -> bool:
        """Membuka koneksi."""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Menutup koneksi."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Cek status koneksi."""
        pass
    
    @abstractmethod
    def read_line(self) -> Optional[str]:
        """Membaca satu baris data."""
        pass


class SerialConnection(IConnection):
    """Koneksi Serial untuk komunikasi USB."""
    
    def __init__(self, port: str, baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
    
    def connect(self) -> bool:
        """Membuka koneksi serial."""
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=0.1)
            return True
        except Exception as e:
            print(f"Error membuka serial port: {e}")
            return False
    
    def disconnect(self):
        """Menutup koneksi serial."""
        if self.serial and self.serial.is_open:
            self.serial.close()
    
    def is_connected(self) -> bool:
        """Cek status koneksi serial."""
        return self.serial is not None and self.serial.is_open
    
    def read_line(self) -> Optional[str]:
        """Membaca satu baris dari serial."""
        if not self.is_connected():
            return None
        
        try:
            if self.serial.in_waiting > 0:
                line = self.serial.readline().decode('utf-8').strip()
                return line if line else None
        except Exception as e:
            print(f"Error membaca serial: {e}")
        
        return None
    
    @staticmethod
    def list_ports():
        """Mendapatkan daftar port serial yang tersedia."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]


class WiFiConnection(IConnection):
    """Koneksi WiFi menggunakan TCP socket."""
    
    def __init__(self, host: str, port: int = 8888):
        self.host = host
        self.port = port
        self.socket = None
        self.buffer = ""
    
    def connect(self) -> bool:
        """Membuka koneksi TCP."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(0.1)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Error membuka WiFi connection: {e}")
            return False
    
    def disconnect(self):
        """Menutup koneksi TCP."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.buffer = ""
    
    def is_connected(self) -> bool:
        """Cek status koneksi TCP."""
        return self.socket is not None
    
    def read_line(self) -> Optional[str]:
        """Membaca satu baris dari TCP socket."""
        if not self.is_connected():
            return None
        
        try:
            # Terima data dari socket
            data = self.socket.recv(1024).decode('utf-8')
            if data:
                self.buffer += data
            
            # Cari baris lengkap
            if '\n' in self.buffer:
                line, self.buffer = self.buffer.split('\n', 1)
                return line.strip()
        except socket.timeout:
            pass
        except Exception as e:
            print(f"Error membaca WiFi: {e}")
            self.disconnect()
        
        return None
