import random
import time

class IMUSimulator:
    def __init__(self):
        self.running = True

    def get_data(self):
        """Generate random IMU-like data"""
        return {
            "roll": round(random.uniform(-30, 30), 2),
            "pitch": round(random.uniform(-30, 30), 2),
            "yaw": round(random.uniform(-180, 180), 2)
        }

    def stop(self):
        self.running = False
