from abc import ABC, abstractmethod
from typing import Optional, Callable
import serial
import serial.tools.list_ports
import socket
import json
try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None


class IConnection(ABC):
    
    @abstractmethod
    def connect(self) -> bool:
        pass
    
    @abstractmethod
    def disconnect(self):
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        pass
    
    @abstractmethod
    def read_line(self) -> Optional[str]:
        pass
    
    @abstractmethod
    def send_command(self, command: str) -> bool:
        pass


class SerialConnection(IConnection):
    
    def __init__(self, port: str, baudrate: int = 921600):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
    
    def connect(self) -> bool:
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=0.1)
            return True
        except Exception as e:
            print(f"Error serial: {e}")
            return False
    
    def disconnect(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
    
    def is_connected(self) -> bool:
        return self.serial is not None and self.serial.is_open
    
    def read_line(self) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            if self.serial.in_waiting > 0:
                line = self.serial.readline().decode('utf-8').strip()
                return line if line else None
        except Exception as e:
            print(f"Error: {e}")
        return None
    
    def send_command(self, command: str) -> bool:
        if not self.is_connected():
            return False
        try:
            if not command.endswith('\n'):
                command += '\n'
            self.serial.write(command.encode('utf-8'))
            self.serial.flush()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    @staticmethod
    def list_ports():
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]


class WiFiConnection(IConnection):
    
    def __init__(self, host: str, port: int = 8888):
        self.host = host
        self.port = port
        self.socket = None
        self.buffer = ""
    
    def connect(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(0.1)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Error WiFi: {e}")
            return False
    
    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.buffer = ""
    
    def is_connected(self) -> bool:
        return self.socket is not None
    
    def read_line(self) -> Optional[str]:
        if not self.is_connected():
            return None
        try:
            data = self.socket.recv(1024).decode('utf-8')
            if data:
                self.buffer += data
            if '\n' in self.buffer:
                line, self.buffer = self.buffer.split('\n', 1)
                return line.strip()
        except socket.timeout:
            pass
        except Exception as e:
            print(f"Error: {e}")
            self.disconnect()
        return None
    
    def send_command(self, command: str) -> bool:
        if not self.is_connected():
            return False
        try:
            if not command.endswith('\n'):
                command += '\n'
            self.socket.sendall(command.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False


class MQTTConnection(IConnection):
    def __init__(self, broker: str, port: int = 1883, 
                 topic_data: str = "gimbal/stabilizer",
                 topic_cmd: str = "gimbal/command"):
        if mqtt is None:
            raise ImportError("paho-mqtt library not installed. Run: pip install paho-mqtt")
        
        self.broker = broker
        self.port = port
        self.topic_data = topic_data
        self.topic_cmd = topic_cmd
        self.client = None
        self.connected = False
        self.data_queue = []
        self.data_callback: Optional[Callable[[str], None]] = None
    
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"MQTT Connected to {self.broker}:{self.port}")
            self.connected = True
            self.client.subscribe(self.topic_data)
            print(f"Subscribed to: {self.topic_data}")
        else:
            print(f"MQTT Connection failed with code {rc}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        print("MQTT Disconnected")
        self.connected = False
    
    def _on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode('utf-8')
            self.data_queue.append(payload)
        except Exception as e:
            print(f"Error processing MQTT message: {e}")
    
    def connect(self) -> bool:
        try:
            import random
            client_id = f"Dashboard-{random.randint(0, 0xFFFF):04X}"
            
            try:
                from paho.mqtt.client import CallbackAPIVersion
                self.client = mqtt.Client(
                    callback_api_version=CallbackAPIVersion.VERSION1,
                    client_id=client_id
                )
            except (ImportError, AttributeError):
                self.client = mqtt.Client(client_id)
            
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            print(f"Connecting to MQTT broker {self.broker}:{self.port}...")
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            
            import time
            timeout = 5
            start = time.time()
            while not self.connected and (time.time() - start) < timeout:
                time.sleep(0.1)
            
            return self.connected
        except Exception as e:
            print(f"Error membuka MQTT connection: {e}")
            return False
    
    def disconnect(self):
        if self.client:
            try:
                self.client.loop_stop()
                self.client.disconnect()
            except:
                pass
            self.client = None
        self.connected = False
        self.data_queue.clear()
    
    def is_connected(self) -> bool:
        return self.connected
    
    def read_line(self) -> Optional[str]:
        if not self.is_connected():
            return None
        if self.data_queue:
            return self.data_queue.pop(0)
        return None
    
    def send_command(self, command: str) -> bool:
        if not self.is_connected():
            return False
        try:
            result = self.client.publish(self.topic_cmd, command)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"Error mengirim MQTT command: {e}")
            return False
