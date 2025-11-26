from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox,
    QGroupBox, QRadioButton, QButtonGroup, QMessageBox
)
from PyQt5.QtCore import QTimer
from models.connection import SerialConnection
from controllers import DataManager
from .plot_widget import PlotWidget


class BallStabilizerDashboard(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.data_count = 0
        self.init_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)
    
    def init_ui(self):
        self.setWindowTitle('Ball Stabilizer Dashboard')
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        connection_group = self.create_connection_group()
        main_layout.addWidget(connection_group)
        
        info_group = self.create_info_group()
        main_layout.addWidget(info_group)
        
        pid_group = self.create_pid_control_group()
        main_layout.addWidget(pid_group)
        
        self.plot_widget = PlotWidget(max_points=500)
        main_layout.addWidget(self.plot_widget)
        
        control_layout = self.create_control_buttons()
        main_layout.addLayout(control_layout)
    
    def create_connection_group(self):
        group = QGroupBox("Connection Settings")
        layout = QVBoxLayout()
        
        mode_layout = QHBoxLayout()
        self.connection_mode_group = QButtonGroup()
        
        self.serial_radio = QRadioButton("Serial (USB)")
        self.mqtt_radio = QRadioButton("MQTT (WiFi)")
        
        self.connection_mode_group.addButton(self.serial_radio, 0)
        self.connection_mode_group.addButton(self.mqtt_radio, 1)
        self.serial_radio.setChecked(True)
        
        self.serial_radio.toggled.connect(self.on_mode_changed)
        self.mqtt_radio.toggled.connect(self.on_mode_changed)
        
        mode_layout.addWidget(self.serial_radio)
        mode_layout.addWidget(self.mqtt_radio)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        self.serial_layout = QHBoxLayout()
        self.serial_port_label = QLabel("Serial Port:")
        self.serial_layout.addWidget(self.serial_port_label)
        self.port_combo = QComboBox()
        self.refresh_ports()
        self.serial_layout.addWidget(self.port_combo)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        self.serial_layout.addWidget(self.refresh_btn)
        self.serial_layout.addStretch()
        layout.addLayout(self.serial_layout)
        
        self.mqtt_layout = QHBoxLayout()
        self.broker_label = QLabel("MQTT Broker:")
        self.mqtt_layout.addWidget(self.broker_label)
        self.broker_input = QLineEdit()
        self.broker_input.setPlaceholderText("broker.hivemq.com")
        self.broker_input.setText("broker.hivemq.com")
        self.mqtt_layout.addWidget(self.broker_input)
        
        self.mqtt_port_label = QLabel("Port:")
        self.mqtt_layout.addWidget(self.mqtt_port_label)
        self.mqtt_port_input = QLineEdit()
        self.mqtt_port_input.setText("1883")
        self.mqtt_port_input.setMaximumWidth(80)
        self.mqtt_layout.addWidget(self.mqtt_port_input)
        self.mqtt_layout.addStretch()
        layout.addLayout(self.mqtt_layout)
        
        button_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        button_layout.addWidget(self.connect_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.on_mode_changed()
        
        group.setLayout(layout)
        return group
    
    def on_mode_changed(self):
        is_serial = self.serial_radio.isChecked()
        
        self.serial_port_label.setVisible(is_serial)
        self.port_combo.setVisible(is_serial)
        self.refresh_btn.setVisible(is_serial)
        
        self.broker_label.setVisible(not is_serial)
        self.broker_input.setVisible(not is_serial)
        self.mqtt_port_label.setVisible(not is_serial)
        self.mqtt_port_input.setVisible(not is_serial)
    
    def create_info_group(self):
        group = QGroupBox("Data Info")
        layout = QHBoxLayout()
        
        self.status_label = QLabel("Status: Disconnected")
        layout.addWidget(self.status_label)
        
        self.data_count_label = QLabel("Data Count: 0")
        layout.addWidget(self.data_count_label)
        
        self.log_status_label = QLabel("Logging: Off")
        layout.addWidget(self.log_status_label)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def create_pid_control_group(self):
        group = QGroupBox("PID Control")
        layout = QHBoxLayout()
        
        layout.addWidget(QLabel("Kp:"))
        self.kp_input = QLineEdit()
        self.kp_input.setText("7.0")
        self.kp_input.setMaximumWidth(80)
        layout.addWidget(self.kp_input)
        
        layout.addWidget(QLabel("Ki:"))
        self.ki_input = QLineEdit()
        self.ki_input.setText("0.5")
        self.ki_input.setMaximumWidth(80)
        layout.addWidget(self.ki_input)
        
        layout.addWidget(QLabel("Kd:"))
        self.kd_input = QLineEdit()
        self.kd_input.setText("0.0")
        self.kd_input.setMaximumWidth(80)
        layout.addWidget(self.kd_input)
        
        self.send_pid_btn = QPushButton("Send PID to ESP32")
        self.send_pid_btn.clicked.connect(self.send_pid_values)
        layout.addWidget(self.send_pid_btn)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def create_control_buttons(self):
        layout = QHBoxLayout()
        
        self.log_btn = QPushButton("Start Logging")
        self.log_btn.clicked.connect(self.toggle_logging)
        layout.addWidget(self.log_btn)
        
        self.clear_btn = QPushButton("Clear Plot")
        self.clear_btn.clicked.connect(self.clear_plot)
        layout.addWidget(self.clear_btn)
        
        layout.addStretch()
        
        return layout
    
    def refresh_ports(self):
        self.port_combo.clear()
        ports = SerialConnection.list_ports()
        self.port_combo.addItems(ports)
    
    def toggle_connection(self):
        if self.data_manager.is_connected():
            self.disconnect()
        else:
            self.connect()
    
    def connect(self):
        mode = self.connection_mode_group.checkedId()
        success = False
        
        if mode == 0:
            port = self.port_combo.currentText()
            if not port:
                QMessageBox.warning(self, "Error", "Please select a serial port")
                return
            success = self.data_manager.connect_serial(port)
        
        elif mode == 1:
            broker = self.broker_input.text().strip()
            port_str = self.mqtt_port_input.text().strip()
            
            if not broker:
                QMessageBox.warning(self, "Error", "Please enter MQTT broker address")
                return
            
            try:
                port = int(port_str)
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid port number")
                return
            
            success = self.data_manager.connect_mqtt(broker, port)
        
        if success:
            self.connect_btn.setText("Disconnect")
            self.update_status()
            self.data_count = 0
        else:
            QMessageBox.warning(self, "Error", "Failed to connect")
    
    def disconnect(self):
        self.data_manager.disconnect()
        self.connect_btn.setText("Connect")
        self.update_status()
    
    def toggle_logging(self):
        if self.data_manager.is_logging():
            self.data_manager.stop_logging()
            self.log_btn.setText("Start Logging")
        else:
            self.data_manager.start_logging()
            self.log_btn.setText("Stop Logging")
            filename = self.data_manager.get_log_filename()
            QMessageBox.information(self, "Logging Started", 
                                  f"Logging to: {filename}")
        
        self.update_status()
    
    def clear_plot(self):
        self.plot_widget.clear_plot()
        self.data_count = 0
        self.data_count_label.setText("Data Count: 0")
    
    def send_pid_values(self):
        if not self.data_manager.is_connected():
            QMessageBox.warning(self, "Error", "Not connected to ESP32")
            return
        
        try:
            kp = float(self.kp_input.text())
            ki = float(self.ki_input.text())
            kd = float(self.kd_input.text())
            
            success = self.data_manager.send_pid_values(kp, ki, kd)
            
            if success:
                QMessageBox.information(self, "Success", 
                                      f"PID values sent to ESP32:\nKp={kp}, Ki={ki}, Kd={kd}")
            else:
                QMessageBox.warning(self, "Error", "Failed to send PID values")
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid PID values. Please enter numbers.")
    
    def update_data(self):
        if not self.data_manager.is_connected():
            return
        
        data = self.data_manager.read_data()
        if data:
            self.plot_widget.update_data(data)
            self.data_count += 1
            self.data_count_label.setText(f"Data Count: {self.data_count}")
    
    def update_status(self):
        if self.data_manager.is_connected():
            mode = self.connection_mode_group.checkedId()
            mode_text = ["Serial", "MQTT"][mode]
            self.status_label.setText(f"Status: Connected ({mode_text})")
        else:
            self.status_label.setText("Status: Disconnected")
        
        if self.data_manager.is_logging():
            filename = self.data_manager.get_log_filename()
            self.log_status_label.setText(f"Logging: {filename}")
        else:
            self.log_status_label.setText("Logging: Off")
    
    def closeEvent(self, event):
        if self.data_manager.is_connected():
            self.data_manager.disconnect()
        event.accept()
