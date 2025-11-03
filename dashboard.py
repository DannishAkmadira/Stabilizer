import sys
import random
import csv
import os
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QHBoxLayout, QGroupBox, QGridLayout
)
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class BallStabilizerDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ball Stabilizer Dashboard")
        self.setGeometry(100, 100, 1000, 700)

        # Variabel utama
        self.running = False
        self.data_log = []
        self.start_time = time.time()
        self.csv_filename = "imu_log.csv"

        # Hapus file log lama saat program dijalankan
        if os.path.exists(self.csv_filename):
            os.remove(self.csv_filename)

        # Layout utama
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Status
        self.label_status = QLabel("Status: STOPPED")
        self.label_status.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
        main_layout.addWidget(self.label_status)

        # IMU Data
        imu_group = QGroupBox("IMU Data")
        imu_layout = QVBoxLayout()
        self.label_roll = QLabel("Roll: 0°")
        self.label_pitch = QLabel("Pitch: 0°")
        self.label_yaw = QLabel("Yaw: 0°")
        imu_layout.addWidget(self.label_roll)
        imu_layout.addWidget(self.label_pitch)
        imu_layout.addWidget(self.label_yaw)
        imu_group.setLayout(imu_layout)
        main_layout.addWidget(imu_group)

        # PID Control
        pid_group = QGroupBox("PID Control")
        pid_layout = QGridLayout()
        self.kp_input = QLineEdit("1.0")
        self.ki_input = QLineEdit("0.5")
        self.kd_input = QLineEdit("0.1")
        pid_layout.addWidget(QLabel("Kp:"), 0, 0)
        pid_layout.addWidget(self.kp_input, 0, 1)
        pid_layout.addWidget(QLabel("Ki:"), 1, 0)
        pid_layout.addWidget(self.ki_input, 1, 1)
        pid_layout.addWidget(QLabel("Kd:"), 2, 0)
        pid_layout.addWidget(self.kd_input, 2, 1)
        pid_group.setLayout(pid_layout)
        main_layout.addWidget(pid_group)

        # Tombol kontrol
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.btn_reset = QPushButton("Reset")
        self.btn_manual = QPushButton("Manual Control")

        self.btn_start.clicked.connect(self.start_system)
        self.btn_stop.clicked.connect(self.stop_system)
        self.btn_reset.clicked.connect(self.reset_system)
        self.btn_manual.clicked.connect(self.manual_control)

        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addWidget(self.btn_manual)
        main_layout.addLayout(btn_layout)

        # Grafik IMU (Roll dan Pitch)
        self.figure = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.init_plot()
        main_layout.addWidget(self.canvas)

        # Timer update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)

        # Final layout
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    # Inisialisasi grafik
    def init_plot(self):
        self.ax.clear()
        self.ax.set_title("IMU Roll & Pitch over Time")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Angle (°)")
        self.ax.grid(True)
        self.time_data = []
        self.roll_data = []
        self.pitch_data = []
        self.canvas.draw()

    # Tombol: Start
    def start_system(self):
        if not self.running:
            self.running = True
            self.timer.start(500)  # update tiap 0.5 detik
            self.label_status.setText("Status: RUNNING")
            self.label_status.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
            print("[INFO] System started.")

    # Tombol: Stop
    def stop_system(self):
        self.running = False
        self.timer.stop()
        self.label_status.setText("Status: STOPPED")
        self.label_status.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
        print("[INFO] System stopped.")

    # Tombol: Reset 
    def reset_system(self):
        print("[ACTION] Reset system triggered")

        # Hentikan sistem & timer
        self.running = False
        self.timer.stop()

        # Reset label status
        self.label_status.setText("Status: RESET")
        self.label_status.setStyleSheet("font-size: 16px; font-weight: bold; color: orange;")

        # Reset data internal
        self.data_log.clear()
        self.init_plot()
        self.start_time = time.time()

        # Reset label IMU
        self.label_roll.setText("Roll: 0°")
        self.label_pitch.setText("Pitch: 0°")
        self.label_yaw.setText("Yaw: 0°")

        # Hapus file CSV log biar fresh
        if os.path.exists(self.csv_filename):
            os.remove(self.csv_filename)
            print("[INFO] Log file deleted and reset.")

        print("[INFO] System fully reset.")

    # Tombol: Manual Control
    def manual_control(self):
        print("[ACTION] Manual control activated")
        self.label_status.setText("Status: MANUAL")
        self.label_status.setStyleSheet("font-size: 16px; font-weight: bold; color: blue;")

    # Update data (simulasi IMU)
    def update_data(self):
        if not self.running:
            return

        current_time = time.time() - self.start_time
        roll = random.uniform(-30, 30)
        pitch = random.uniform(-30, 30)
        yaw = random.uniform(-180, 180)

        self.time_data.append(current_time)
        self.roll_data.append(roll)
        self.pitch_data.append(pitch)
        self.data_log.append((current_time, roll, pitch, yaw))

        # Update label
        self.label_roll.setText(f"Roll: {roll:.2f}°")
        self.label_pitch.setText(f"Pitch: {pitch:.2f}°")
        self.label_yaw.setText(f"Yaw: {yaw:.2f}°")

        # Update grafik
        self.ax.clear()
        self.ax.plot(self.time_data, self.roll_data, label="Roll")
        self.ax.plot(self.time_data, self.pitch_data, label="Pitch")
        self.ax.set_title("IMU Roll & Pitch over Time")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Angle (°)")
        self.ax.grid(True)
        self.ax.legend()
        self.canvas.draw()

        # Simpan data ke CSV
        self.save_to_csv(current_time, roll, pitch, yaw)

    # Simpan data ke CSV
    def save_to_csv(self, t, roll, pitch, yaw):
        new_file = not os.path.exists(self.csv_filename)
        with open(self.csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            if new_file:
                writer.writerow(["Time (s)", "Roll (°)", "Pitch (°)", "Yaw (°)"])
            writer.writerow([f"{t:.2f}", f"{roll:.2f}", f"{pitch:.2f}", f"{yaw:.2f}"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BallStabilizerDashboard()
    window.show()
    sys.exit(app.exec_())
