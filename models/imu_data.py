"""IMU data model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class IMUData:
    """Data class untuk menyimpan data IMU."""
    roll: float
    gyro_rate: float
    servo_pos: float
    timestamp: datetime = None
    
    def __post_init__(self):
        """Set timestamp jika belum diset."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
