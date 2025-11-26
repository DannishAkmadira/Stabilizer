from dataclasses import dataclass
from datetime import datetime


@dataclass
class IMUData:
    roll: float
    gyro_rate: float
    servo_pos: float
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
