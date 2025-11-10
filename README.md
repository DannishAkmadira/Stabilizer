# Ball Stabilizer Dashboard

Dashboard untuk monitoring dan kontrol sistem stabilizer bola menggunakan ESP32 dan sensor IMU (MPU6050).

## 📁 Project Structure

```
Stabilizer/
├── main.py                   # ✨ Application entry point
├── models/                   # ✨ Data models
│   ├── __init__.py
│   ├── imu_data.py          # IMU data structure
│   ├── connection.py        # Connection interfaces
│   ├── data_processor.py    # Data parsing & simulation
│   └── data_logger.py       # CSV logging
├── views/                    # ✨ UI components
│   ├── __init__.py
│   ├── plot_widget.py       # Matplotlib plots
│   └── main_window.py       # Main dashboard window
├── controllers/              # ✨ Business logic
│   ├── __init__.py
│   └── data_manager.py      # Data orchestration
├── dashboard.py              # Original dashboard (legacy)
├── imu_simulator.py          # IMU data simulator
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── WIFI_SETUP.md            # WiFi setup guide
├── TROUBLESHOOTING.md       # Troubleshooting guide
└── esp_firmware/            # ESP32 firmware
    └── src/
        └── main.cpp         # ESP32 code
```

## 🆕 What's New - MVC Architecture

Dashboard telah di-refactor menggunakan **Model-View-Controller (MVC)** pattern dengan struktur file yang proper!

### Key Improvements:
- ✅ **MVC Architecture** - Clean separation of concerns
- ✅ **Modular Files** - Each class in its own file
- ✅ **Python Naming Convention** - lowercase_with_underscores
- ✅ **Type Safety** - Using dataclasses and type hints
- ✅ **Abstract Interfaces** - Easy to add new connection types
- ✅ **Better Testing** - Each component can be tested independently
- ✅ **Professional Code** - Follows SOLID principles

### Architecture Overview:

**Models** (`models/`):
- `imu_data.py` - Data structure untuk IMU readings
- `connection.py` - Abstract interface dan implementasi (Serial, WiFi)
- `data_processor.py` - Parser dan simulator
- `data_logger.py` - CSV logging functionality

**Views** (`views/`):
- `plot_widget.py` - Matplotlib plotting widget
- `main_window.py` - PyQt5 main window UI

**Controllers** (`controllers/`):
- `data_manager.py` - Orchestrates data flow dan business logic

**Entry Point**:
- `main.py` - Run the application

## 🚀 Quick Start

### Run Dashboard
```bash
python main.py
```

### Old Version (Legacy)
```bash
python dashboard.py
```

---

## Ball Stabilizer Dashboard

Dashboard untuk monitoring dan kontrol sistem stabilizer bola menggunakan ESP32 dan sensor IMU (MPU6050).

## 🔌 Mode Koneksi

Dashboard mendukung 2 mode koneksi:

### 1. **Serial (USB)**
Koneksi langsung melalui kabel USB ke ESP32
- Port: COM3, COM4, dll (tergantung sistem)
- Baud rate: 115200

### 2. **WiFi (TCP)**
Koneksi wireless melalui jaringan WiFi
- Port: 8888
- IP Address: Sesuai IP ESP32 yang terhubung ke WiFi

## 📋 Cara Penggunaan

### Setup ESP32 dengan WiFi

1. **Upload firmware** ke ESP32 menggunakan PlatformIO
2. Saat pertama kali dinyalakan, ESP32 akan membuat Access Point dengan nama **"GimbalAP"**
3. Hubungkan laptop/HP ke WiFi **"GimbalAP"**
4. Browser akan otomatis terbuka untuk konfigurasi WiFi (atau buka `192.168.4.1`)
5. Pilih WiFi yang ingin dihubungkan dan masukkan password
6. ESP32 akan restart dan terhubung ke WiFi tersebut
7. Lihat IP Address ESP32 di Serial Monitor (contoh: `192.168.1.100`)

### Menjalankan Dashboard

1. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

2. **Jalankan dashboard**:
   ```cmd
   python dashboard.py
   ```

### Koneksi Serial (USB)

1. Pilih radio button **"Serial (USB)"**
2. Pilih **COM Port** dari dropdown (contoh: COM3)
3. Klik **"Connect"**
4. Klik **"Start"** untuk mulai menerima data

### Koneksi WiFi

1. Pastikan laptop dan ESP32 terhubung ke **WiFi yang sama**
2. Pilih radio button **"WiFi (TCP)"**
3. Masukkan **IP Address ESP32** (lihat di Serial Monitor)
4. Port default: **8888**
5. Klik **"Connect"**
6. Klik **"Start"** untuk mulai menerima data

## 📊 Format Data

ESP32 mengirim data dengan format:
```
DATA:roll,pitch,yaw,servo_pos
```

Contoh:
```
DATA:0,10.52,0,95
```

- **Roll**: Sudut roll dalam derajat (untuk 1-axis = 0)
- **Pitch**: Sudut pitch/angleY dalam derajat
- **Yaw**: Sudut yaw dalam derajat (untuk 1-axis = 0)
- **Servo Pos**: Posisi servo (45-135°)

## 🛠️ Fitur Dashboard

- ✅ Monitoring IMU data real-time (Roll, Pitch, Yaw)
- ✅ Grafik history Roll & Pitch
- ✅ PID Control parameter tuning
- ✅ Data logging ke CSV file (`imu_log.csv`)
- ✅ Manual control mode
- ✅ System reset
- ✅ Dual mode connection (Serial & WiFi)

## 📦 Dependencies

- PyQt5
- matplotlib
- pyserial

## 🔧 Troubleshooting

### ESP32 tidak terhubung ke WiFi
- Pastikan SSID dan password benar
- Coba reset ESP32 dan ulangi konfigurasi WiFi
- Gunakan Serial Monitor untuk melihat status koneksi

### Dashboard tidak terima data WiFi
- Pastikan laptop dan ESP32 di **WiFi yang sama**
- Cek IP Address ESP32 di Serial Monitor
- Cek firewall Windows tidak memblok port 8888
- Ping ESP32 dari CMD: `ping 192.168.1.100`

### Data tidak muncul
- Pastikan sudah klik **"Start"** setelah connect
- Cek koneksi serial/WiFi masih aktif
- Lihat console untuk error messages