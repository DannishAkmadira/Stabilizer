"""Data processing utilities."""

from typing import Optional
import random
import json
from .imu_data import IMUData


class DataParser:
    """Parser untuk data dari format string ke IMUData."""
    
    @staticmethod
    def parse(line: str) -> Optional[IMUData]:
        """
        Parse string format "DATA:roll,gyro_rate,servo_pos" atau JSON ke IMUData.
        
        Supports:
        1. Legacy format: "DATA:roll,gyro_rate,servo_pos"
        2. MQTT JSON format: {"r":roll,"g":gyro,"s":servo,"e":error,"i":integral}
        
        Args:
            line: String data dari sensor
            
        Returns:
            IMUData object atau None jika parsing gagal
        """
        try:
            # Try JSON format first (MQTT)
            if line.strip().startswith('{'):
                data = json.loads(line)
                # JSON format: {"r":roll,"g":gyro,"s":servo,"e":error,"i":integral}
                roll = float(data.get('r', 0))
                gyro_rate = float(data.get('g', 0))
                servo_pos = float(data.get('s', 90))
                return IMUData(roll=roll, gyro_rate=gyro_rate, servo_pos=servo_pos)
            
            # Legacy CSV format (Serial/TCP)
            if line.startswith("DATA:"):
                # Ambil bagian data setelah "DATA:"
                data_str = line[5:]
                parts = data_str.split(',')
                
                if len(parts) != 3:
                    return None
                
                roll = float(parts[0])
                gyro_rate = float(parts[1])
                servo_pos = float(parts[2])
                
                return IMUData(roll=roll, gyro_rate=gyro_rate, servo_pos=servo_pos)
            
            return None
        except Exception as e:
            print(f"Error parsing data: {e}")
            return None


class DataSimulator:
    """Simulator untuk generate data random (untuk testing)."""
    
    @staticmethod
    def generate() -> IMUData:
        """Generate random IMU data untuk testing."""
        roll = random.uniform(-30, 30)
        gyro_rate = random.uniform(-50, 50)
        servo_pos = random.uniform(0, 180)
        return IMUData(roll=roll, gyro_rate=gyro_rate, servo_pos=servo_pos)
