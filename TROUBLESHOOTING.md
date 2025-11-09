# 🔧 Troubleshooting Guide - Ball Stabilizer Dashboard

## 📊 Masalah: Data Tidak Muncul / Grafik Tidak Plotting

### ✅ Checklist Debugging

#### 1. **Cek Status Koneksi**
- Lihat label **"Connection:"** di dashboard
- Harus berwarna **hijau** dan menunjukkan koneksi aktif
- Contoh: `Connection: WiFi (192.168.1.100:8888)` atau `Connection: Serial (COM3)`

#### 2. **Cek Data Counter**
- Lihat label **"Data received:"** di panel IMU Data
- Angka harus **naik** saat system running
- Jika angka 0 atau tidak naik = data tidak diterima

#### 3. **Cek Console Output**
Jalankan dashboard dari terminal untuk melihat log:
```cmd
python dashboard.py
```

**Output yang BAIK (WiFi):**
```
[INFO] Connecting to 192.168.1.100:8888...
[INFO] WiFi connected to 192.168.1.100:8888
[INFO] System started.
[WIFI RAW] DATA:5.23,0,0,95
[WIFI DATA #1] Roll: 5.23, Pitch: 0.00, Yaw: 0.00
[WIFI RAW] DATA:5.45,0,0,96
[WIFI DATA #2] Roll: 5.45, Pitch: 0.00, Yaw: 0.00
...
```

**Output yang BAIK (Serial):**
```
[INFO] Connected to COM3
[INFO] System started.
[SERIAL RAW] DATA:5.23,0,0,95
[SERIAL DATA #1] Roll: 5.23, Pitch: 0.00, Yaw: 0.00
[SERIAL RAW] DATA:5.45,0,0,96
[SERIAL DATA #2] Roll: 5.45, Pitch: 0.00, Yaw: 0.00
...
```

#### 4. **Cek ESP32 Serial Monitor**
Buka Serial Monitor di PlatformIO (115200 baud):

**Output yang BAIK:**
```
WiFi connected!
IP address: 192.168.1.100
TCP Server started on port 8888
MPU6050 Found!
Roll Angle: 5.23° | Error: -5.23° | Servo: 95° | GyroRate: 0.12 deg/s
DATA:5.23,0,0,95
New client connected via WiFi!  <-- Dashboard terhubung
Roll Angle: 5.45° | Error: -5.45° | Servo: 96° | GyroRate: 0.15 deg/s
DATA:5.45,0,0,96
...
```

---

## 🔍 Skenario Masalah & Solusi

### ❌ Problem 1: "Data received: 0" tidak naik

**Kemungkinan Penyebab:**
1. ESP32 tidak mengirim data
2. Format data salah
3. Parsing gagal

**Solusi:**

**A. Cek ESP32 mengirim data:**
- Buka Serial Monitor ESP32
- Lihat apakah ada output `DATA:x,x,x,x`
- Jika tidak ada → ESP32 bermasalah, coba reset/upload ulang

**B. Cek format data:**
- Dashboard mengharapkan format: `DATA:roll,pitch,yaw,servo`
- Contoh valid: `DATA:5.23,0,0,95`
- Jika format beda → ESP32 perlu diupdate

**C. Cek parsing:**
- Lihat console dashboard untuk `[WIFI RAW]` atau `[SERIAL RAW]`
- Jika tidak ada RAW output → data tidak sampai
- Jika ada RAW tapi tidak ada `[WIFI DATA]` → parsing gagal

---

### ❌ Problem 2: WiFi Connected tapi tidak ada data

**Cek 1: ESP32 tahu ada client?**
```
Serial Monitor ESP32 harus tampil:
"New client connected via WiFi!"
```

Jika tidak muncul:
- Restart ESP32
- Disconnect dan Connect ulang dari dashboard
- Cek firewall Windows tidak block

**Cek 2: Data dikirim via WiFi?**
```cpp
// Di main.cpp harus ada:
if (client && client.connected()) {
    client.print(data);  // ← Ini harus ada!
}
```

**Cek 3: Timeout terlalu pendek?**
Dashboard menggunakan timeout 100ms. Jika koneksi lambat, bisa miss data.

**Solusi:** Edit `dashboard.py` line ~287:
```python
self.wifi_socket.settimeout(0.5)  # Coba timeout lebih lama
```

---

### ❌ Problem 3: Serial Connected tapi tidak ada data

**Cek 1: Baud rate benar?**
- Dashboard: 115200
- ESP32: 115200
- Harus sama!

**Cek 2: Port benar?**
- Coba unplug dan plug ulang USB
- Refresh port di dashboard
- Ganti kabel USB (kabel rusak bisa jadi masalah)

**Cek 3: Driver USB-Serial**
- Install driver CH340/CP2102 untuk ESP32
- Cek Device Manager Windows

---

### ❌ Problem 4: Data diterima tapi grafik tidak update

**Cek 1: System Running?**
- Status harus "RUNNING" (hijau)
- Jika "STOPPED" → klik tombol **Start**

**Cek 2: Data valid?**
- Lihat label Roll, Pitch, Yaw
- Jika update → parsing OK
- Jika tidak update → cek console untuk error

**Cek 3: List data terisi?**
```python
# Di update_data(), pastikan ini dijalankan:
self.time_data.append(current_time)
self.roll_data.append(roll)
self.pitch_data.append(pitch)
```

Tambahkan debug print setelah append:
```python
print(f"[PLOT] Data points: {len(self.time_data)}")
```

---

### ❌ Problem 5: "Connection: NOT CONNECTED" padahal sudah connect

**Kemungkinan:**
- Koneksi terputus tiba-tiba
- Socket error tidak terdeteksi

**Solusi:**
1. Klik **Disconnect**
2. Klik **Connect** lagi
3. Pastikan ESP32 masih online (cek Serial Monitor)

---

### ❌ Problem 6: Data jumping / tidak smooth

**Penyebab:**
- Update rate terlalu lambat
- Network latency (WiFi)
- Data loss

**Solusi:**

**A. Percepat timer update** (di `dashboard.py`):
```python
self.timer.start(50)  # 50ms = 20Hz (dari 100ms)
```

**B. Buffer data** untuk smooth plotting:
```python
# Keep last N data points
max_points = 100
if len(self.time_data) > max_points:
    self.time_data = self.time_data[-max_points:]
    self.roll_data = self.roll_data[-max_points:]
    self.pitch_data = self.pitch_data[-max_points:]
```

**C. Gunakan Serial** jika WiFi terlalu lambat/tidak stabil

---

## 📋 Debugging Commands

### Test ESP32 TCP Server (tanpa dashboard)
```cmd
# Windows - Test koneksi ke ESP32
telnet 192.168.1.100 8888

# Atau pakai Python
python -c "import socket; s=socket.socket(); s.connect(('192.168.1.100', 8888)); print(s.recv(1024).decode())"
```

### Test Serial Port
```cmd
# List available COM ports
python -c "import serial.tools.list_ports; [print(p) for p in serial.tools.list_ports.comports()]"
```

### Monitor Raw Data
Edit `dashboard.py` untuk always print raw data:
```python
def parse_data_line(self, line):
    print(f"[PARSING] Input: '{line}'")  # Debug print
    try:
        # ... existing code ...
```

---

## 🔄 Reset Everything Procedure

Jika semua gagal, reset total:

### 1. Reset ESP32
```bash
cd esp_firmware
pio run --target erase  # Hapus semua data
pio run --target upload # Upload fresh
```

### 2. Reset WiFi Config
- Tekan tombol reset pada ESP32
- Konfigurasi ulang WiFi via "GimbalAP"

### 3. Reset Dashboard
- Hapus `imu_log.csv`
- Restart dashboard
- Connect ulang

### 4. Restart Laptop
- Kadang Windows cache socket/port
- Restart bisa solve masalah aneh

---

## 📞 Masih Bermasalah?

Kumpulkan info ini:
1. **Console output dashboard** (copy semua)
2. **Serial Monitor ESP32** (copy semua)
3. **Screenshot dashboard**
4. **Versi Python**: `python --version`
5. **OS**: Windows 10/11?

Dengan info ini bisa diagnose lebih lanjut!

---

## 💡 Tips Debugging

1. **Selalu buka 2 windows**:
   - Window 1: Serial Monitor ESP32
   - Window 2: Dashboard Python console

2. **Test step by step**:
   - ✅ ESP32 upload OK?
   - ✅ ESP32 connect WiFi OK?
   - ✅ Laptop ping ESP32 OK?
   - ✅ Dashboard connect OK?
   - ✅ Data counter naik OK?
   - ✅ Grafik update OK?

3. **Gunakan Serial sebagai backup**:
   - WiFi bermasalah? Pakai USB
   - USB bermasalah? Pakai WiFi

4. **Log everything**:
   - Tambahkan `print()` di mana-mana
   - Better too much log than no log!
