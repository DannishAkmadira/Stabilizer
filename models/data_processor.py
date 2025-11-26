from typing import Optional
import random
import json
from .imu_data import IMUData


class DataParser:
    
    @staticmethod
    def parse(line: str) -> Optional[IMUData]:
        try:
            if line.strip().startswith('{'):
                data = json.loads(line)
                roll = float(data.get('r', 0))
                gyro_rate = float(data.get('g', 0))
                servo_pos = float(data.get('s', 90))
                return IMUData(roll=roll, gyro_rate=gyro_rate, servo_pos=servo_pos)
            
            if line.startswith("DATA:"):
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
    
    @staticmethod
    def generate() -> IMUData:
        roll = random.uniform(-30, 30)
        gyro_rate = random.uniform(-50, 50)
        servo_pos = random.uniform(0, 180)
        return IMUData(roll=roll, gyro_rate=gyro_rate, servo_pos=servo_pos)
