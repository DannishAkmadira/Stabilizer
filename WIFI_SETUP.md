# 📡 Panduan Setup WiFi untuk Ball Stabilizer

## 🎯 Overview

ESP32 menggunakan **WiFiManager** untuk konfigurasi WiFi yang mudah. Tidak perlu hardcode SSID/password di kode!

## 🔧 Cara Setup WiFi (Pertama Kali)

### Step 1: Upload Firmware ke ESP32
```bash
# Di folder esp_firmware/
pio run --target upload
```

### Step 2: Koneksi ke ESP32 Access Point

1. **Nyalakan ESP32** (buka Serial Monitor untuk melihat status)
2. ESP32 akan tampilkan pesan:
   ```
   WiFi connected!
   IP address: 192.168.1.xxx
   TCP Server started on port 8888
   ```
   
3. Jika **belum pernah dikonfigurasi**, ESP32 akan membuat WiFi Access Point:
   - **SSID**: `GimbalAP`
   - **Password**: (tidak ada - open network)

### Step 3: Konfigurasi WiFi

1. **Hubungkan laptop/HP** ke WiFi **"GimbalAP"**
2. Browser akan **otomatis terbuka** halaman konfigurasi
   - Jika tidak otomatis, buka: `http://192.168.4.1`
3. **Pilih WiFi** yang ingin dihubungkan dari daftar
4. **Masukkan password** WiFi tersebut
5. Klik **"Save"**
6. ESP32 akan **restart** dan connect ke WiFi yang dipilih

### Step 4: Cari IP Address ESP32

Buka **Serial Monitor** (115200 baud), akan tampil:
```
WiFi connected!
IP address: 192.168.1.100  <-- Catat IP ini!
TCP Server started on port 8888
Use IP: 192.168.1.100:8888
```

## 💻 Cara Connect Dashboard ke ESP32

### Via WiFi (Wireless)

1. **Pastikan laptop** terhubung ke **WiFi yang sama** dengan ESP32
2. Jalankan dashboard:
   ```cmd
   python dashboard.py
   ```
3. Pilih **"WiFi (TCP)"**
4. Masukkan **IP Address** ESP32 (contoh: `192.168.1.100`)
5. Port: `8888`
6. Klik **"Connect"**
7. Klik **"Start"** untuk mulai monitoring

### Via Serial (USB Backup)

Jika WiFi bermasalah, masih bisa pakai USB:
1. Colok **kabel USB** ke ESP32
2. Pilih **"Serial (USB)"**
3. Pilih **COM Port** (contoh: COM3)
4. Klik **"Connect"**
5. Klik **"Start"**

## 🔍 Cara Cek IP ESP32 Tanpa Serial Monitor

### Cara 1: Gunakan Router Admin Panel
1. Login ke router (biasanya `192.168.1.1` atau `192.168.0.1`)
2. Cari menu **"Connected Devices"** atau **"DHCP Clients"**
3. Cari device dengan nama **"ESP32"** atau **"GimbalAP"**

### Cara 2: Gunakan IP Scanner
1. Download tool seperti **Advanced IP Scanner** atau **Angry IP Scanner**
2. Scan network: `192.168.1.1-254`
3. Cari device dengan port **8888** terbuka

### Cara 3: Ping dari CMD
```cmd
# Coba ping range IP
ping 192.168.1.100
ping 192.168.1.101
...dst
```

## 🛠️ Reset WiFi Configuration

Jika ingin **ganti WiFi** atau konfigurasi rusak:

### Opsi 1: Flash Ulang ESP32
```bash
pio run --target upload
```

### Opsi 2: WiFiManager Reset (Jika ada tombol)
- Tekan tombol reset pada ESP32
- Atau tambahkan tombol fisik untuk trigger `wifiManager.resetSettings()`

### Opsi 3: Erase Flash
```bash
pio run --target erase
pio run --target upload
```

## 📊 Monitoring Koneksi

### Serial Monitor Output (Normal)
```
WiFi connected!
IP address: 192.168.1.100
TCP Server started on port 8888
Connect your laptop to the same WiFi network
Use IP: 192.168.1.100:8888
MPU6050 Found!
Gimbal Stabilizer Y-Axis Initialized!
Calibrating... Keep the gimbal level and stable

AngleY: 2.45° | Error: -2.45° | ServoY: 85° | GyroY: 0.12 deg/s
DATA:0,2.45,0,85
New client connected via WiFi!  <-- Dashboard terhubung!
```

### Dashboard Console Output (Normal)
```
[INFO] WiFi connected to 192.168.1.100:8888
[INFO] System started.
```

## ⚠️ Troubleshooting

### ❌ Problem: ESP32 tidak connect ke WiFi
**Solusi:**
- Pastikan password WiFi benar
- Pastikan WiFi 2.4GHz (ESP32 tidak support 5GHz)
- Cek jarak ESP32 dari router
- Reset WiFi config dan setup ulang

### ❌ Problem: Dashboard tidak bisa connect
**Solusi:**
- Pastikan laptop dan ESP32 di **WiFi yang sama**
- Cek IP Address ESP32 di Serial Monitor
- Ping ESP32: `ping 192.168.1.100`
- Cek firewall Windows tidak block port 8888
- Coba connect via Serial dulu untuk pastikan ESP32 jalan

### ❌ Problem: IP Address berubah-ubah
**Solusi:**
- Setup **DHCP Reservation** di router
- Atau hardcode Static IP di kode (tidak recommended)

### ❌ Problem: Koneksi putus-putus
**Solusi:**
- Dekatkan ESP32 ke router
- Kurangi device lain di WiFi
- Gunakan koneksi Serial sebagai backup

## 🔐 Keamanan

⚠️ **WARNING**: TCP Server tidak terenkripsi!
- Jangan gunakan di **public WiFi**
- Data dikirim dalam **plain text**
- Untuk production, gunakan **TLS/SSL** atau **VPN**

## 🚀 Tips & Tricks

1. **Save IP Address**: Catat IP ESP32 untuk koneksi cepat
2. **Dual Mode**: Siapkan kabel USB sebagai backup jika WiFi bermasalah
3. **WiFi Stabil**: Gunakan WiFi 2.4GHz dengan sinyal kuat
4. **Static IP**: Setup DHCP reservation di router agar IP tidak berubah
5. **Multiple ESP32**: Bisa hubungkan beberapa ESP32 dengan port berbeda

## 📱 Future Improvements

- [ ] Web-based dashboard (akses via browser)
- [ ] WebSocket untuk latency lebih rendah
- [ ] HTTPS/TLS encryption
- [ ] mDNS support (connect via hostname, bukan IP)
- [ ] Mobile app (Android/iOS)
