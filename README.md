# Ball Stabilizer Dashboard

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