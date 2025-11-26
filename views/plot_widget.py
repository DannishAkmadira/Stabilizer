from collections import deque
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from models import IMUData


class PlotWidget(FigureCanvas):
    
    def __init__(self, parent=None, max_points=500):
        self.figure = Figure(figsize=(10, 6))
        super().__init__(self.figure)
        self.setParent(parent)
        
        self.max_points = max_points
        
        self.times = deque(maxlen=max_points)
        self.rolls = deque(maxlen=max_points)
        self.gyro_rates = deque(maxlen=max_points)
        
        self.ax1 = self.figure.add_subplot(211)
        self.ax2 = self.figure.add_subplot(212)
        
        self.line1, = self.ax1.plot([], [], 'b-', label='Roll Angle')
        self.line2, = self.ax2.plot([], [], 'r-', label='Gyro Rate')
        
        self.ax1.set_xlabel('Time (s)')
        self.ax1.set_ylabel('Roll Angle (°)')
        self.ax1.legend()
        self.ax1.grid(True)
        
        self.ax2.set_xlabel('Time (s)')
        self.ax2.set_ylabel('Gyro Rate (°/s)')
        self.ax2.legend()
        self.ax2.grid(True)
        
        self.figure.tight_layout()
        
        self.start_time = None
    
    def update_data(self, data: IMUData):
        if self.start_time is None:
            self.start_time = data.timestamp
        
        elapsed = (data.timestamp - self.start_time).total_seconds()
        
        self.times.append(elapsed)
        self.rolls.append(data.roll)
        self.gyro_rates.append(data.gyro_rate)
        
        self.line1.set_data(list(self.times), list(self.rolls))
        self.line2.set_data(list(self.times), list(self.gyro_rates))
        
        if len(self.times) > 0:
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.ax2.relim()
            self.ax2.autoscale_view()
        
        self.draw()
    
    def clear_plot(self):
        self.times.clear()
        self.rolls.clear()
        self.gyro_rates.clear()
        self.start_time = None
        
        self.line1.set_data([], [])
        self.line2.set_data([], [])
        
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.ax2.relim()
        self.ax2.autoscale_view()
        
        self.draw()
