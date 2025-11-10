# MVC Architecture Guide

## Struktur Project

Project ini menggunakan **Model-View-Controller (MVC)** pattern untuk memisahkan concerns dan membuat kode lebih modular.

```
Stabilizer/
├── main.py                   # Entry point aplikasi
├── models/                   # Data models dan business logic
│   ├── __init__.py
│   ├── imu_data.py          # Data structure
│   ├── connection.py        # Connection interfaces
│   ├── data_processor.py    # Data parsing
│   └── data_logger.py       # Logging
├── views/                    # UI components
│   ├── __init__.py
│   ├── plot_widget.py       # Plot widget
│   └── main_window.py       # Main window
└── controllers/              # Business logic
    ├── __init__.py
    └── data_manager.py      # Data orchestration
```

## Komponen Utama

### Models (`models/`)

**1. imu_data.py**
- `IMUData`: Dataclass untuk menyimpan data IMU
  - Fields: `roll`, `gyro_rate`, `servo_pos`, `timestamp`

**2. connection.py**
- `IConnection`: Abstract interface untuk koneksi
- `SerialConnection`: Implementasi koneksi USB/Serial
- `WiFiConnection`: Implementasi koneksi TCP/WiFi

**3. data_processor.py**
- `DataParser`: Parse string "DATA:x,y,z" ke `IMUData`
- `DataSimulator`: Generate random data untuk testing

**4. data_logger.py**
- `DataLogger`: Log data ke file CSV

### Views (`views/`)

**1. plot_widget.py**
- `PlotWidget`: Widget matplotlib untuk menampilkan grafik
  - Dual subplot: Roll Angle dan Gyro Rate
  - Auto-scaling dan buffering

**2. main_window.py**
- `BallStabilizerDashboard`: Main window PyQt5
  - Connection controls
  - Mode selection (Serial/WiFi/Simulation)
  - Start/stop logging
  - Clear plot

### Controllers (`controllers/`)

**1. data_manager.py**
- `DataManager`: Orchestrates semua komponen
  - Manages connection (serial/wifi/simulation)
  - Handles data parsing
  - Controls logging
  - Coordinates data flow

## Data Flow

```
ESP32/Simulator
      ↓
  Connection (Serial/WiFi)
      ↓
  DataManager.read_data()
      ↓
  DataParser.parse()
      ↓
    IMUData
      ↓
  ├─→ DataLogger.log()     (jika logging aktif)
  └─→ PlotWidget.update()  (via callback)
```

## Cara Menambahkan Fitur Baru

### Tambah Connection Type Baru

1. Buat class baru di `models/connection.py`:
```python
class BluetoothConnection(IConnection):
    def connect(self) -> bool:
        # Implementation
        pass
    
    def disconnect(self):
        pass
    
    def is_connected(self) -> bool:
        pass
    
    def read_line(self) -> Optional[str]:
        pass
```

2. Add method di `DataManager`:
```python
def connect_bluetooth(self, address: str) -> bool:
    self.disconnect()
    self.connection = BluetoothConnection(address)
    return self.connection.connect()
```

3. Update UI di `main_window.py` untuk tambah radio button dan input fields.

### Tambah Data Processing

1. Edit `models/data_processor.py`:
```python
class DataFilter:
    @staticmethod
    def moving_average(data: List[float], window: int) -> float:
        return sum(data[-window:]) / window
```

2. Gunakan di `DataManager`:
```python
def read_data(self):
    data = super().read_data()
    if data:
        filtered_roll = DataFilter.moving_average(self.roll_buffer, 5)
        # ...
```

### Tambah Widget Baru

1. Buat file baru di `views/`:
```python
# views/status_widget.py
from PyQt5.QtWidgets import QWidget

class StatusWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Implementation
```

2. Import dan gunakan di `main_window.py`:
```python
from .status_widget import StatusWidget

class BallStabilizerDashboard(QMainWindow):
    def init_ui(self):
        self.status_widget = StatusWidget()
        main_layout.addWidget(self.status_widget)
```

## Python Naming Conventions

Project ini mengikuti **PEP 8** naming conventions:

- **Modules**: `lowercase_with_underscores.py`
  - ✅ `data_processor.py`
  - ❌ `DataProcessor.py`

- **Classes**: `PascalCase`
  - ✅ `DataManager`
  - ❌ `data_manager`

- **Functions/Methods**: `lowercase_with_underscores()`
  - ✅ `read_data()`
  - ❌ `readData()`

- **Constants**: `UPPERCASE_WITH_UNDERSCORES`
  - ✅ `MAX_BUFFER_SIZE`
  - ❌ `maxBufferSize`

- **Private**: `_leading_underscore`
  - ✅ `_write_header()`
  - ❌ `writeHeader()`

## Testing

### Unit Test Example

```python
# test_data_parser.py
import unittest
from models import DataParser

class TestDataParser(unittest.TestCase):
    def test_parse_valid_data(self):
        line = "DATA:10.5,20.3,95.0"
        data = DataParser.parse(line)
        self.assertIsNotNone(data)
        self.assertEqual(data.roll, 10.5)
        self.assertEqual(data.gyro_rate, 20.3)
        self.assertEqual(data.servo_pos, 95.0)
    
    def test_parse_invalid_data(self):
        line = "INVALID:data"
        data = DataParser.parse(line)
        self.assertIsNone(data)

if __name__ == '__main__':
    unittest.main()
```

### Integration Test

```python
# test_integration.py
from models import IMUData
from controllers import DataManager

def test_simulation_mode():
    manager = DataManager()
    manager.start_simulation()
    
    data = manager.read_data()
    assert data is not None
    assert isinstance(data, IMUData)
    
    manager.disconnect()
```

## Tips & Best Practices

1. **Import Organization**:
```python
# Standard library
import sys
from typing import Optional

# Third-party
from PyQt5.QtWidgets import QMainWindow
import serial

# Local modules
from models import IMUData
from controllers import DataManager
```

2. **Type Hints**:
```python
def parse(line: str) -> Optional[IMUData]:
    pass
```

3. **Docstrings**:
```python
def connect_serial(self, port: str) -> bool:
    """
    Koneksi ke serial port.
    
    Args:
        port: Nama port serial (e.g., "COM3")
        
    Returns:
        True jika berhasil connect
    """
```

4. **Error Handling**:
```python
try:
    # risky operation
except SpecificException as e:
    print(f"Error: {e}")
    return None
```

## Running the Application

```bash
# Main application
python main.py

# With specific Python version
python3 main.py

# In virtual environment (Windows)
.venv\Scripts\activate
python main.py

# In virtual environment (Linux/Mac)
source .venv/bin/activate
python main.py
```

## Troubleshooting

**Import errors**:
- Make sure you're in the project root directory
- Check that `__init__.py` files exist in all packages

**Module not found**:
```bash
pip install -r requirements.txt
```

**PyQt5 display issues**:
- Update graphics drivers
- Try: `pip install --upgrade PyQt5`
