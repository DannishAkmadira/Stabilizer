# Changelog

## [Unreleased] - 2025-11-10

### Changed
- **UI Improvement**: Input fields sekarang hanya menampilkan field yang relevan berdasarkan mode koneksi yang dipilih
  - Mode Serial: Hanya tampil Serial Port dropdown dan Refresh button
  - Mode WiFi: Hanya tampil ESP32 IP dan Port input fields
  
### Removed
- **Simulation Mode**: Mode simulasi dihapus dari UI
  - Radio button "Simulation" dihapus
  - Fungsi `start_simulation()` tidak lagi dapat diakses dari UI
  
### Technical Details
- Added `on_mode_changed()` method untuk handle visibility toggle
- Updated `connect()` method untuk remove simulation case
- Updated `update_status()` untuk remove "Simulation" dari mode text array
- Connected radio button `toggled` signals ke `on_mode_changed()` slot

### Benefits
- UI lebih bersih dan tidak membingungkan
- User hanya melihat input yang relevan untuk mode yang dipilih
- Menghindari input error dari field yang tidak terpakai
