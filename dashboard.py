import sys
import random
import csv
import os
import time
import serial
import serial.tools.list_ports
import socket
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QHBoxLayout, QGroupBox, QGridLayout, QComboBox, QMessageBox,
    QRadioButton, QButtonGroup
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
        
        # Connection variables
        self.connection_mode = "serial"  # "serial" or "wifi"
        self.serial_port = None
        self.serial_connected = False
        self.wifi_socket = None
        self.wifi_connected = False
        self.wifi_buffer = ""  # Buffer untuk data WiFi yang belum lengkap
        self.data_counter = 0  # Counter untuk debugging

        # Hapus file log lama saat program dijalankan
        if os.path.exists(self.csv_filename):
            os.remove(self.csv_filename)

        # Layout utama
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Connection Mode Group
        mode_group = QGroupBox("Connection Mode")
        mode_layout = QHBoxLayout()
        self.radio_serial = QRadioButton("Serial (USB)")
        self.radio_wifi = QRadioButton("WiFi (TCP)")
        self.radio_serial.setChecked(True)
        self.radio_serial.toggled.connect(self.on_mode_changed)
        self.radio_wifi.toggled.connect(self.on_mode_changed)
        mode_layout.addWidget(self.radio_serial)
        mode_layout.addWidget(self.radio_wifi)
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)

        # Serial Connection Group
        self.serial_group = QGroupBox("Serial Connection")
        serial_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.refresh_ports()
        self.btn_refresh = QPushButton("Refresh")
        self.btn_serial_connect = QPushButton("Connect")
        self.btn_serial_disconnect = QPushButton("Disconnect")
        self.btn_refresh.clicked.connect(self.refresh_ports)
        self.btn_serial_connect.clicked.connect(self.connect_serial)
        self.btn_serial_disconnect.clicked.connect(self.disconnect_serial)
        self.btn_serial_disconnect.setEnabled(False)
        serial_layout.addWidget(QLabel("Port:"))
        serial_layout.addWidget(self.port_combo)
        serial_layout.addWidget(self.btn_refresh)
        serial_layout.addWidget(self.btn_serial_connect)
        serial_layout.addWidget(self.btn_serial_disconnect)
        self.serial_group.setLayout(serial_layout)
        main_layout.addWidget(self.serial_group)

        # WiFi Connection Group
        self.wifi_group = QGroupBox("WiFi Connection")
        wifi_layout = QHBoxLayout()
        self.ip_input = QLineEdit("192.168.1.100")
        self.ip_input.setPlaceholderText("ESP32 IP Address")
        self.port_input = QLineEdit("8888")
        self.port_input.setPlaceholderText("Port")
        self.port_input.setMaximumWidth(80)
        self.btn_wifi_connect = QPushButton("Connect")
        self.btn_wifi_disconnect = QPushButton("Disconnect")
        self.btn_wifi_connect.clicked.connect(self.connect_wifi)
        self.btn_wifi_disconnect.clicked.connect(self.disconnect_wifi)
        self.btn_wifi_disconnect.setEnabled(False)
        wifi_layout.addWidget(QLabel("IP:"))
        wifi_layout.addWidget(self.ip_input)
        wifi_layout.addWidget(QLabel("Port:"))
        wifi_layout.addWidget(self.port_input)
        wifi_layout.addWidget(self.btn_wifi_connect)
        wifi_layout.addWidget(self.btn_wifi_disconnect)
        self.wifi_group.setLayout(wifi_layout)
        self.wifi_group.setVisible(False)  # Hidden by default
        main_layout.addWidget(self.wifi_group)

        # Status
        status_layout = QHBoxLayout()
        self.label_status = QLabel("Status: STOPPED")
        self.label_status.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
        self.label_connection = QLabel("Connection: NOT CONNECTED")
        self.label_connection.setStyleSheet("font-size: 14px; color: gray;")
        status_layout.addWidget(self.label_status)
        status_layout.addWidget(self.label_connection)
        main_layout.addLayout(status_layout)

        # IMU Data
        imu_group = QGroupBox("IMU Data")
        imu_layout = QVBoxLayout()
        self.label_roll = QLabel("Roll: 0°")
        self.label_gyro = QLabel("Gyro Rate: 0 deg/s")
        self.label_servo = QLabel("Servo Position: 90°")
        self.label_data_count = QLabel("Data received: 0")
        self.label_data_count.setStyleSheet("color: blue; font-size: 12px;")
        imu_layout.addWidget(self.label_roll)
        imu_layout.addWidget(self.label_gyro)
        imu_layout.addWidget(self.label_servo)
        imu_layout.addWidget(self.label_data_count)
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

        # Grafik (2 subplot: Roll Angle dan Gyro Rate)
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.ax_roll = self.figure.add_subplot(211)  # Top plot
        self.ax_gyro = self.figure.add_subplot(212)  # Bottom plot
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
        # Clear both subplots
        self.ax_roll.clear()
        self.ax_gyro.clear()
        
        # Setup Roll Angle plot
        self.ax_roll.set_title("Roll Angle over Time")
        self.ax_roll.set_ylabel("Angle (°)")
        self.ax_roll.grid(True)
        
        # Setup Gyro Rate plot
        self.ax_gyro.set_title("Gyro Rate over Time")
        self.ax_gyro.set_xlabel("Time (s)")
        self.ax_gyro.set_ylabel("Rate (deg/s)")
        self.ax_gyro.grid(True)
        
        # Data arrays
        self.time_data = []
        self.roll_data = []
        self.gyro_data = []
        
        self.figure.tight_layout()
        self.canvas.draw()

    # Tombol: Start
    def start_system(self):
        if not self.running:
            self.running = True
            # Update lebih cepat untuk WiFi/Serial real-time (100ms = 10Hz)
            # Lebih lambat dari ESP32 (10ms) tapi cukup untuk plotting smooth
            self.timer.start(100)  # update tiap 0.1 detik (10Hz)
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
        self.data_counter = 0

        # Reset label IMU
        self.label_roll.setText("Roll: 0°")
        self.label_gyro.setText("Gyro Rate: 0 deg/s")
        self.label_servo.setText("Servo Position: 90°")
        self.label_data_count.setText("Data received: 0")

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

    # Mode selection changed
    def on_mode_changed(self):
        if self.radio_serial.isChecked():
            self.connection_mode = "serial"
            self.serial_group.setVisible(True)
            self.wifi_group.setVisible(False)
        else:
            self.connection_mode = "wifi"
            self.serial_group.setVisible(False)
            self.wifi_group.setVisible(True)

    # Refresh available serial ports
    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(f"{port.device} - {port.description}")
        if self.port_combo.count() == 0:
            self.port_combo.addItem("No ports available")

    # Connect to serial port
    def connect_serial(self):
        port_text = self.port_combo.currentText()
        if "No ports available" in port_text:
            QMessageBox.warning(self, "Error", "No serial ports available!")
            return
        
        port_name = port_text.split(" - ")[0]
        try:
            self.serial_port = serial.Serial(port_name, 115200, timeout=1)
            time.sleep(2)  # Wait for Arduino/ESP32 to reset
            self.serial_connected = True
            self.btn_serial_connect.setEnabled(False)
            self.btn_serial_disconnect.setEnabled(True)
            self.port_combo.setEnabled(False)
            self.label_connection.setText(f"Connection: Serial ({port_name})")
            self.label_connection.setStyleSheet("font-size: 14px; color: green;")
            QMessageBox.information(self, "Success", f"Connected to {port_name}")
            print(f"[INFO] Connected to {port_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect: {str(e)}")
            print(f"[ERROR] Failed to connect: {str(e)}")

    # Disconnect from serial port
    def disconnect_serial(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.serial_connected = False
        self.btn_serial_connect.setEnabled(True)
        self.btn_serial_disconnect.setEnabled(False)
        self.port_combo.setEnabled(True)
        self.label_connection.setText("Connection: NOT CONNECTED")
        self.label_connection.setStyleSheet("font-size: 14px; color: gray;")
        print("[INFO] Disconnected from serial port")

    # Connect to WiFi (TCP Socket)
    def connect_wifi(self):
        ip_address = self.ip_input.text()
        port = int(self.port_input.text())
        
        try:
            self.wifi_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.wifi_socket.settimeout(5)  # 5 second timeout for connection
            print(f"[INFO] Connecting to {ip_address}:{port}...")
            self.wifi_socket.connect((ip_address, port))
            self.wifi_socket.settimeout(0.1)  # 100ms timeout for reading (non-blocking)
            self.wifi_buffer = ""  # Reset buffer
            self.wifi_connected = True
            self.btn_wifi_connect.setEnabled(False)
            self.btn_wifi_disconnect.setEnabled(True)
            self.ip_input.setEnabled(False)
            self.port_input.setEnabled(False)
            self.label_connection.setText(f"Connection: WiFi ({ip_address}:{port})")
            self.label_connection.setStyleSheet("font-size: 14px; color: green;")
            QMessageBox.information(self, "Success", f"Connected to {ip_address}:{port}")
            print(f"[INFO] WiFi connected to {ip_address}:{port}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect via WiFi: {str(e)}")
            print(f"[ERROR] WiFi connection failed: {str(e)}")
            if self.wifi_socket:
                self.wifi_socket.close()
                self.wifi_socket = None

    # Disconnect from WiFi
    def disconnect_wifi(self):
        if self.wifi_socket:
            self.wifi_socket.close()
            self.wifi_socket = None
        self.wifi_connected = False
        self.wifi_buffer = ""
        self.btn_wifi_connect.setEnabled(True)
        self.btn_wifi_disconnect.setEnabled(False)
        self.ip_input.setEnabled(True)
        self.port_input.setEnabled(True)
        self.label_connection.setText("Connection: NOT CONNECTED")
        self.label_connection.setStyleSheet("font-size: 14px; color: gray;")
        print("[INFO] Disconnected from WiFi")

    # Read data from serial port
    def read_serial_data(self):
        if not self.serial_port or not self.serial_port.is_open:
            return None, None, None
        
        try:
            if self.serial_port.in_waiting > 0:
                line = self.serial_port.readline().decode('utf-8').strip()
                if line:
                    print(f"[SERIAL RAW] {line}")  # Debug: tampilkan data mentah
                    return self.parse_data_line(line)
        except Exception as e:
            print(f"[ERROR] Reading serial data: {str(e)}")
        
        return None, None, None

    # Read data from WiFi socket
    def read_wifi_data(self):
        if not self.wifi_socket:
            return None, None, None
        
        try:
            # Terima data dari socket
            data = self.wifi_socket.recv(1024).decode('utf-8')
            if data:
                # Tambahkan ke buffer
                self.wifi_buffer += data
                
                # Cari line lengkap (yang diakhiri newline)
                while '\n' in self.wifi_buffer:
                    line, self.wifi_buffer = self.wifi_buffer.split('\n', 1)
                    line = line.strip()
                    
                    if line:
                        print(f"[WIFI RAW] {line}")  # Debug: tampilkan data mentah
                        result = self.parse_data_line(line)
                        if result[0] is not None:
                            return result
        except socket.timeout:
            pass  # No data available, normal behavior
        except Exception as e:
            print(f"[ERROR] Reading WiFi data: {str(e)}")
            self.wifi_connected = False
            if self.wifi_socket:
                self.wifi_socket.close()
                self.wifi_socket = None
        
        return None, None, None

    # Parse data line from ESP32
    def parse_data_line(self, line):
        try:
            # Parse format baru: "DATA:roll,gyro_rate,servo_pos"
            if line.startswith("DATA:"):
                data = line.replace("DATA:", "").split(",")
                if len(data) >= 3:
                    roll = float(data[0])
                    gyro_rate = float(data[1])
                    servo_pos = int(data[2])
                    return roll, gyro_rate, servo_pos
            
            # Fallback: Parse format lama "Roll Angle: 10.5° | Error: ..."
            elif "Roll Angle:" in line:
                parts = line.split("|")
                roll = float(parts[0].split(":")[1].replace("°", "").strip())
                # Extract gyro rate if available
                gyro_rate = 0
                for part in parts:
                    if "GyroRate:" in part:
                        gyro_rate = float(part.split(":")[1].replace("deg/s", "").strip())
                return roll, gyro_rate, 90  # Default servo 90
        except Exception as e:
            print(f"[ERROR] Parsing data: {str(e)}")
        
        return None, None, None

    # Update data (dari IMU real atau simulasi)
    def update_data(self):
        if not self.running:
            return

        current_time = time.time() - self.start_time
        
        # Coba baca dari koneksi aktif
        if self.serial_connected:
            roll, gyro_rate, servo_pos = self.read_serial_data()
            if roll is not None:
                self.data_counter += 1
                print(f"[SERIAL DATA #{self.data_counter}] Roll: {roll:.2f}°, Gyro: {gyro_rate:.2f} deg/s, Servo: {servo_pos}°")
        elif self.wifi_connected:
            roll, gyro_rate, servo_pos = self.read_wifi_data()
            if roll is not None:
                self.data_counter += 1
                print(f"[WIFI DATA #{self.data_counter}] Roll: {roll:.2f}°, Gyro: {gyro_rate:.2f} deg/s, Servo: {servo_pos}°")
        else:
            # Gunakan data simulasi jika tidak terkoneksi
            roll = random.uniform(-30, 30)
            gyro_rate = random.uniform(-50, 50)
            servo_pos = 90
            self.data_counter += 1

        # Jika tidak ada data valid, skip update kali ini
        if roll is None or gyro_rate is None or servo_pos is None:
            return

        self.time_data.append(current_time)
        self.roll_data.append(roll)
        self.gyro_data.append(gyro_rate)
        self.data_log.append((current_time, roll, gyro_rate, servo_pos))

        # Update label
        self.label_roll.setText(f"Roll: {roll:.2f}°")
        self.label_gyro.setText(f"Gyro Rate: {gyro_rate:.2f} deg/s")
        self.label_servo.setText(f"Servo Position: {servo_pos}°")
        self.label_data_count.setText(f"Data received: {self.data_counter}")

        # Update grafik Roll Angle
        self.ax_roll.clear()
        self.ax_roll.plot(self.time_data, self.roll_data, 'b-', label="Roll", linewidth=2)
        self.ax_roll.set_title("Roll Angle over Time")
        self.ax_roll.set_ylabel("Angle (°)")
        self.ax_roll.grid(True, alpha=0.3)
        self.ax_roll.legend(loc='upper right')
        
        # Update grafik Gyro Rate
        self.ax_gyro.clear()
        self.ax_gyro.plot(self.time_data, self.gyro_data, 'r-', label="Gyro Rate", linewidth=2)
        self.ax_gyro.set_title("Gyro Rate over Time")
        self.ax_gyro.set_xlabel("Time (s)")
        self.ax_gyro.set_ylabel("Rate (deg/s)")
        self.ax_gyro.grid(True, alpha=0.3)
        self.ax_gyro.legend(loc='upper right')
        
        self.figure.tight_layout()
        self.canvas.draw()

        # Simpan data ke CSV
        self.save_to_csv(current_time, roll, gyro_rate, servo_pos)

    # Simpan data ke CSV
    def save_to_csv(self, t, roll, gyro_rate, servo_pos):
        new_file = not os.path.exists(self.csv_filename)
        with open(self.csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            if new_file:
                writer.writerow(["Time (s)", "Roll (°)", "Gyro Rate (deg/s)", "Servo Position (°)"])
            writer.writerow([f"{t:.2f}", f"{roll:.2f}", f"{gyro_rate:.2f}", f"{servo_pos}"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BallStabilizerDashboard()
    window.show()
    sys.exit(app.exec_())
