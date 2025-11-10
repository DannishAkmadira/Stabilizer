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

### Setup ESP32

1. Upload firmware ke ESP32 menggunakan PlatformIO
2. ESP32 akan membuat Access Point "GimbalAP" saat pertama kali
3. Hubungkan ke WiFi "GimbalAP"
4. Browser akan terbuka untuk konfigurasi WiFi (atau buka 192.168.4.1)
5. Pilih WiFi dan masukkan password
6. ESP32 akan restart dan connect ke WiFi

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

## Dependencies

- PyQt5
- matplotlib
- pyserial
- paho-mqtt

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