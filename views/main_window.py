"""Main window UI for Ball Stabilizer Dashboard."""

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
    """Main window untuk Ball Stabilizer Dashboard."""
    
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.data_count = 0
        self.init_ui()
        
        # Setup timer untuk membaca data
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)  # Update setiap 100ms
    
    def init_ui(self):
        """Setup UI components."""
        self.setWindowTitle('Ball Stabilizer Dashboard')
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Connection group
        connection_group = self.create_connection_group()
        main_layout.addWidget(connection_group)
        
        # Data info group
        info_group = self.create_info_group()
        main_layout.addWidget(info_group)
        
        # Plot widget
        self.plot_widget = PlotWidget(max_points=500)
        main_layout.addWidget(self.plot_widget)
        
        # Control buttons
        control_layout = self.create_control_buttons()
        main_layout.addLayout(control_layout)
    
    def create_connection_group(self):
        """Create connection settings group."""
        group = QGroupBox("Connection Settings")
        layout = QVBoxLayout()
        
        # Connection mode selection
        mode_layout = QHBoxLayout()
        self.connection_mode_group = QButtonGroup()
        
        self.serial_radio = QRadioButton("Serial (USB)")
        self.wifi_radio = QRadioButton("WiFi (TCP)")
        
        self.connection_mode_group.addButton(self.serial_radio, 0)
        self.connection_mode_group.addButton(self.wifi_radio, 1)
        self.serial_radio.setChecked(True)
        
        # Connect radio buttons to slot
        self.serial_radio.toggled.connect(self.on_mode_changed)
        self.wifi_radio.toggled.connect(self.on_mode_changed)
        
        mode_layout.addWidget(self.serial_radio)
        mode_layout.addWidget(self.wifi_radio)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        # Serial settings
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
        
        # WiFi settings
        self.wifi_layout = QHBoxLayout()
        self.esp32_ip_label = QLabel("ESP32 IP:")
        self.wifi_layout.addWidget(self.esp32_ip_label)
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("192.168.4.1")
        self.wifi_layout.addWidget(self.ip_input)
        
        self.port_label = QLabel("Port:")
        self.wifi_layout.addWidget(self.port_label)
        self.port_input = QLineEdit()
        self.port_input.setText("8888")
        self.port_input.setMaximumWidth(80)
        self.wifi_layout.addWidget(self.port_input)
        self.wifi_layout.addStretch()
        layout.addLayout(self.wifi_layout)
        
        # Connect button
        button_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        button_layout.addWidget(self.connect_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Set initial visibility
        self.on_mode_changed()
        
        group.setLayout(layout)
        return group
    
    def on_mode_changed(self):
        """Handle mode change to show/hide relevant input fields."""
        is_serial = self.serial_radio.isChecked()
        
        # Show/hide serial widgets
        self.serial_port_label.setVisible(is_serial)
        self.port_combo.setVisible(is_serial)
        self.refresh_btn.setVisible(is_serial)
        
        # Show/hide WiFi widgets
        self.esp32_ip_label.setVisible(not is_serial)
        self.ip_input.setVisible(not is_serial)
        self.port_label.setVisible(not is_serial)
        self.port_input.setVisible(not is_serial)
    
    def create_info_group(self):
        """Create data info group."""
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
    
    def create_control_buttons(self):
        """Create control buttons."""
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
        """Refresh daftar serial ports."""
        self.port_combo.clear()
        ports = SerialConnection.list_ports()
        self.port_combo.addItems(ports)
    
    def toggle_connection(self):
        """Toggle connect/disconnect."""
        if self.data_manager.is_connected():
            self.disconnect()
        else:
            self.connect()
    
    def connect(self):
        """Connect ke data source."""
        mode = self.connection_mode_group.checkedId()
        success = False
        
        if mode == 0:  # Serial
            port = self.port_combo.currentText()
            if not port:
                QMessageBox.warning(self, "Error", "Please select a serial port")
                return
            success = self.data_manager.connect_serial(port)
        
        elif mode == 1:  # WiFi
            ip = self.ip_input.text().strip()
            port_str = self.port_input.text().strip()
            
            if not ip:
                QMessageBox.warning(self, "Error", "Please enter ESP32 IP address")
                return
            
            try:
                port = int(port_str)
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid port number")
                return
            
            success = self.data_manager.connect_wifi(ip, port)
        
        if success:
            self.connect_btn.setText("Disconnect")
            self.update_status()
            self.data_count = 0
        else:
            QMessageBox.warning(self, "Error", "Failed to connect")
    
    def disconnect(self):
        """Disconnect dari data source."""
        self.data_manager.disconnect()
        self.connect_btn.setText("Connect")
        self.update_status()
    
    def toggle_logging(self):
        """Toggle logging on/off."""
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
        """Clear plot data."""
        self.plot_widget.clear_plot()
        self.data_count = 0
        self.data_count_label.setText("Data Count: 0")
    
    def update_data(self):
        """Update data dari data manager."""
        if not self.data_manager.is_connected():
            return
        
        data = self.data_manager.read_data()
        if data:
            self.plot_widget.update_data(data)
            self.data_count += 1
            self.data_count_label.setText(f"Data Count: {self.data_count}")
    
    def update_status(self):
        """Update status labels."""
        if self.data_manager.is_connected():
            mode = self.connection_mode_group.checkedId()
            mode_text = ["Serial", "WiFi"][mode]
            self.status_label.setText(f"Status: Connected ({mode_text})")
        else:
            self.status_label.setText("Status: Disconnected")
        
        if self.data_manager.is_logging():
            filename = self.data_manager.get_log_filename()
            self.log_status_label.setText(f"Logging: {filename}")
        else:
            self.log_status_label.setText("Logging: Off")
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.data_manager.is_connected():
            self.data_manager.disconnect()
        event.accept()
