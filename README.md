# Ball Stabilizer Dashboard

Dashboard untuk monitoring dan kontrol sistem stabilizer bola menggunakan ESP32 dan sensor IMU (MPU6050).

## Authors
- Muhammad Alif Iqbal
- Dannish Rafi Akmadira

## Project Structure

```
Stabilizer/
├── main.py                   # Application entry point
├── models/                   # Data models
│   ├── imu_data.py          # IMU data structure
│   ├── connection.py        # Connection interfaces (Serial, MQTT)
│   ├── data_processor.py    # Data parsing & simulation
│   └── data_logger.py       # CSV logging
├── views/                    # UI components
│   ├── plot_widget.py       # Matplotlib plots
│   └── main_window.py       # Main dashboard window
├── controllers/             
│   └── data_manager.py      # Data orchestration
├── requirements.txt          # Python dependencies
└── esp_firmware/            # ESP32 firmware
    └── src/
        └── main.cpp         # ESP32 code
```

## Quick Start

```bash
python main.py
```

## Mode Koneksi

Dashboard mendukung 2 mode koneksi:

### Serial (USB)
Koneksi langsung melalui kabel USB ke ESP32.
- Port: COM3, COM4, dll (tergantung sistem)
- Baud rate: 115200

### MQTT (WiFi)
Koneksi wireless melalui MQTT broker.
- Broker: broker.hivemq.com (atau gunakan broker lokal)
- Port: 1883
- Topics:
  - Data: `gimbal/stabilizer`
  - Command: `gimbal/command`

## Cara Penggunaan

### Hardware Wiring

**MPU6050 (I2C):**
- SDA → GPIO 21
- SCL → GPIO 22
- VCC → 3.3V
- GND → GND

**Servo Motor:**
- Signal → GPIO 19
- VCC → 5V
- GND → GND

**OLED SSD1306 (SPI) - Optional:**
- MOSI → GPIO 23
- CLK → GPIO 18
- DC → GPIO 16
- RST → GPIO 17
- CS → GPIO 5
- VCC → 3.3V
- GND → GND

See [OLED_WIRING.md](OLED_WIRING.md) for detailed wiring diagram.

### Setup ESP32

1. Wire all components according to pinout above
2. Upload firmware ke ESP32 menggunakan PlatformIO
3. ESP32 akan membuat Access Point "GimbalAP" saat pertama kali
4. Hubungkan ke WiFi "GimbalAP"
5. Browser akan terbuka untuk konfigurasi WiFi (atau buka 192.168.4.1)
6. Pilih WiFi dan masukkan password
7. ESP32 akan restart dan connect ke WiFi
8. OLED akan menampilkan status WiFi dan MQTT

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Koneksi Serial

1. Pilih "Serial (USB)"
2. Pilih COM Port
3. Klik "Connect"

### Koneksi MQTT

1. Pastikan ESP32 terhubung ke WiFi
2. Pilih "MQTT (WiFi)"
3. Masukkan MQTT Broker (default: broker.hivemq.com)
4. Port: 1883
5. Klik "Connect"

## Format Data

MQTT JSON format:
```json
{"r":5.23,"g":12.45,"s":95,"e":2.1,"i":0.5}
```

Fields:
- r: Roll angle (degrees)
- g: Gyro rate (deg/s)
- s: Servo position (0-180)
- e: PID error
- i: PID integral term

Serial format:
```
DATA:roll,gyro_rate,servo_pos
```

## Fitur

- Real-time monitoring roll angle dan gyro rate
- Grafik history data
- PID control tuning dari aplikasi
- Data logging ke CSV
- Dual mode connection (Serial & MQTT)
- **OLED Display**: Real-time status on device (WiFi, MQTT, Roll, Error, Servo, PID values)

## PID Tuning

1. Connect ke ESP32
2. Masukkan nilai Kp, Ki, Kd di PID Control group
3. Klik "Send PID to ESP32"
4. Amati perubahan di grafik

Default values: Kp=5.0, Ki=0.5, Kd=0.3

Tips:
- Kp: Tingkatkan untuk respons lebih cepat
- Ki: Tingkatkan untuk melawan beban
- Kd: Tingkatkan untuk damping lebih baik

## Hardware Components

- ESP32 Development Board
- MPU6050 IMU Sensor (I2C)
- Servo Motor (for gimbal control)
- SSD1306 OLED Display 128x64 (SPI) - Optional
- Power Supply (5V for servo, 3.3V for ESP32)

## Dependencies

### Python (Dashboard)
- PyQt5
- matplotlib
- pyserial
- paho-mqtt

### ESP32 Firmware
- WiFiManager
- Adafruit MPU6050
- Adafruit SSD1306 (OLED)
- Adafruit GFX Library
- ESP32Servo
- PubSubClient (MQTT)

## Troubleshooting

### ESP32 tidak connect ke WiFi
- Cek SSID dan password
- Reset ESP32 dan ulangi konfigurasi
- Lihat Serial Monitor untuk status

### Dashboard tidak terima data
- Pastikan ESP32 sudah connect ke WiFi
- Cek MQTT broker address benar
- Cek firewall tidak block port 1883
- Install library: `pip install paho-mqtt`

### MQTT connection failed
- Cek internet connection
- Coba broker lain: test.mosquitto.org
- Untuk local broker gunakan IP lokal
- Ping ESP32 dari CMD: `ping 192.168.1.100`

### Data tidak muncul
- Pastikan sudah klik **"Start"** setelah connect
- Cek koneksi serial/WiFi masih aktif
- Lihat console untuk error messages