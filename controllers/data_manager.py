from typing import Optional, Callable
from models import (
    IMUData, IConnection, SerialConnection, WiFiConnection, MQTTConnection,
    DataParser, DataSimulator, DataLogger
)


class DataManager:
    
    def __init__(self):
        self.connection: Optional[IConnection] = None
        self.parser = DataParser()
        self.simulator = DataSimulator()
        self.logger: Optional[DataLogger] = None
        self.is_simulation = False
        self.data_callback: Optional[Callable[[IMUData], None]] = None
    
    def set_data_callback(self, callback: Callable[[IMUData], None]):
        self.data_callback = callback
    
    def connect_serial(self, port: str, baudrate: int = 921600) -> bool:
        self.disconnect()
        self.connection = SerialConnection(port, baudrate)
        self.is_simulation = False
        return self.connection.connect()
    
    def connect_wifi(self, host: str, port: int = 8888) -> bool:
        self.disconnect()
        self.connection = WiFiConnection(host, port)
        self.is_simulation = False
        return self.connection.connect()
    
    def connect_mqtt(self, broker: str, port: int = 1883,
                     topic_data: str = "gimbal/stabilizer",
                     topic_cmd: str = "gimbal/command") -> bool:
        self.disconnect()
        self.connection = MQTTConnection(broker, port, topic_data, topic_cmd)
        self.is_simulation = False
        return self.connection.connect()
    
    def start_simulation(self):
        self.disconnect()
        self.is_simulation = True
    
    def disconnect(self):
        if self.connection:
            self.connection.disconnect()
            self.connection = None
        self.is_simulation = False
    
    def is_connected(self) -> bool:
        if self.is_simulation:
            return True
        return self.connection is not None and self.connection.is_connected()
    
    def start_logging(self, filename: str = None):
        self.logger = DataLogger(filename)
    
    def stop_logging(self):
        self.logger = None
    
    def is_logging(self) -> bool:
        return self.logger is not None
    
    def get_log_filename(self) -> Optional[str]:
        return self.logger.get_filename() if self.logger else None
    
    def read_data(self) -> Optional[IMUData]:
        data = None
        
        if self.is_simulation:
            data = self.simulator.generate()
        
        elif self.connection and self.connection.is_connected():
            line = self.connection.read_line()
            if line:
                data = self.parser.parse(line)
        
        if data and self.logger:
            self.logger.log(data)
        
        if data and self.data_callback:
            self.data_callback(data)
        
        return data
    
    def send_pid_values(self, kp: float, ki: float, kd: float) -> bool:
        if not self.connection or not self.connection.is_connected():
            return False
        
        command = f"PID:{kp},{ki},{kd}"
        return self.connection.send_command(command)
