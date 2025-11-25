# Pin Configuration Summary

## Complete ESP32 Pin Mapping

```
┌─────────────────────────────────────────────────────────────┐
│                         ESP32                               │
│                                                             │
│  GPIO 21 (I2C SDA) ──────────► MPU6050 (SDA)              │
│  GPIO 22 (I2C SCL) ──────────► MPU6050 (SCL)              │
│                                                             │
│  GPIO 19 (PWM)     ──────────► Servo Signal                │
│                                                             │
│  GPIO 23 (SPI MOSI)──────────► OLED (MOSI/SDA)            │
│  GPIO 18 (SPI CLK) ──────────► OLED (CLK/SCK)             │
│  GPIO 16 (GPIO)    ──────────► OLED (DC)                   │
│  GPIO 17 (GPIO)    ──────────► OLED (RST)                  │
│  GPIO 5  (GPIO)    ──────────► OLED (CS)                   │
│                                                             │
│  3.3V ─────────────┬─────────► MPU6050 (VCC)               │
│                    └─────────► OLED (VCC)                   │
│                                                             │
│  5V   ─────────────────────► Servo (VCC)                   │
│                                                             │
│  GND  ─────────────┬─────────► MPU6050 (GND)               │
│                    ├─────────► OLED (GND)                   │
│                    └─────────► Servo (GND)                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Pin Usage Table

| GPIO | Function | Connected To | Protocol | Direction |
|------|----------|--------------|----------|-----------|
| 5    | CS       | OLED         | SPI      | Output    |
| 16   | DC       | OLED         | SPI      | Output    |
| 17   | RST      | OLED         | SPI      | Output    |
| 18   | CLK      | OLED         | SPI      | Output    |
| 19   | PWM      | Servo        | PWM      | Output    |
| 21   | SDA      | MPU6050      | I2C      | Bi-dir    |
| 22   | SCL      | MPU6050      | I2C      | Bi-dir    |
| 23   | MOSI     | OLED         | SPI      | Output    |

## Available Pins

These pins are still available for future expansion:

- GPIO 0, 2, 4, 12, 13, 14, 15, 25, 26, 27, 32, 33, 34, 35, 36, 39

**Note:** Some pins have restrictions:
- GPIO 34-39: Input only (no PWM/pull-up)
- GPIO 0, 2, 12, 15: Boot configuration pins (use with caution)

## OLED Display Layout

```
┌────────────────────────────┐
│ == GIMBAL STATUS ==        │ ← Header (line 0)
│ WiFi: OK -45               │ ← WiFi status + RSSI (line 10)
│ MQTT: Connected            │ ← MQTT status (line 20)
│ Roll: 5.2 deg              │ ← Roll angle (line 30)
│ Err:  0.3 deg              │ ← PID error (line 40)
│ Servo: 95 deg              │ ← Servo position (line 50)
│ P:5.0 I:0.5 D:0.3          │ ← PID parameters (line 58)
└────────────────────────────┘
   128x64 pixels
```

## Power Requirements

| Component | Voltage | Current (typ) | Current (max) | Notes |
|-----------|---------|---------------|---------------|-------|
| ESP32     | 3.3V    | 160mA         | 240mA         | Via USB or regulator |
| MPU6050   | 3.3V    | 3.5mA         | 10mA          | Very low power |
| OLED      | 3.3V    | 20mA          | 50mA          | Depends on pixels lit |
| Servo     | 5V      | 100mA         | 1000mA        | High current under load |

**Total:** ~300mA idle, up to 1.3A peak (when servo moves)

### Power Supply Recommendations

1. **USB Power (5V):**
   - Good for testing and development
   - Use ESP32 dev board with onboard regulator (5V → 3.3V)
   - Servo powered from USB 5V (might brownout with heavy load)

2. **External Power (Recommended for Production):**
   - 5V/2A power supply or battery pack
   - ESP32 gets 3.3V from onboard regulator
   - Servo gets 5V directly
   - Add 100µF capacitor near servo for stability

3. **Battery Operation:**
   - 2S LiPo (7.4V) with 5V buck converter
   - 3S LiPo (11.1V) with 5V buck converter
   - Include low-voltage cutoff protection

## Communication Protocols Used

### I2C Bus (MPU6050)
- **Frequency:** 400kHz (Fast Mode)
- **Address:** 0x68 (default) or 0x69
- **Wires:** 2 (SDA, SCL) + Power

### SPI Bus (OLED)
- **Frequency:** Up to 10MHz
- **Mode:** Master
- **Wires:** 4 (MOSI, CLK, DC, CS) + Reset + Power

### PWM (Servo)
- **Frequency:** 50Hz (20ms period)
- **Pulse Width:** 500-2400µs
- **Resolution:** 0.5° - 1° typical

### UART (Serial Debug)
- **Baud Rate:** 115200
- **Used for:** Debug output and PID commands via USB

### WiFi
- **Standard:** 802.11 b/g/n
- **Frequency:** 2.4GHz
- **Used for:** MQTT communication

## Timing Summary

| Task | Interval | Frequency | Priority |
|------|----------|-----------|----------|
| IMU Read & PID | 20ms | 50Hz | Critical |
| MQTT Publish | 50ms | 20Hz | High |
| OLED Update | 100ms | 10Hz | Medium |
| MQTT Loop | ~1ms | ~1kHz | High |
| Serial Debug | 50ms | 20Hz | Low |

## Software Architecture

```
┌─────────────────────────────────────────────────┐
│                  Main Loop                      │
│                   (20ms)                        │
└────────┬────────────────────────────────────────┘
         │
         ├─► Read MPU6050 (I2C)
         │   ├─► Complementary Filter
         │   └─► Calculate Roll Angle
         │
         ├─► PID Controller
         │   ├─► Calculate Error
         │   ├─► Update Integral
         │   ├─► Calculate Derivative
         │   └─► Compute Output
         │
         ├─► Update Servo (PWM)
         │
         ├─► MQTT Handler (if connected)
         │   ├─► Publish Data (50ms)
         │   └─► Process Commands
         │
         ├─► Serial Handler
         │   ├─► Read Commands
         │   └─► Send Debug Info
         │
         └─► Update OLED (100ms)
             ├─► Clear Display
             ├─► Draw Status
             └─► Display Buffer
```
