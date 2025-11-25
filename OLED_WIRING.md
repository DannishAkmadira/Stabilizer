# OLED SPI Display Wiring Guide

## Hardware Requirements
- **OLED Display**: SSD1306 128x64 (SPI version)
- **ESP32 Development Board**

## Pin Configuration

### OLED SPI Pin Mapping

| OLED Pin | ESP32 Pin | Description |
|----------|-----------|-------------|
| GND      | GND       | Ground |
| VCC      | 3.3V      | Power (3.3V or 5V depending on module) |
| SCK/CLK  | GPIO 18   | SPI Clock |
| MOSI/SDA | GPIO 23   | SPI Data (Master Out Slave In) |
| RES/RST  | GPIO 17   | Reset |
| DC       | GPIO 16   | Data/Command Select |
| CS       | GPIO 5    | Chip Select |

### Visual Wiring Diagram

```
ESP32                    OLED SSD1306 (SPI)
┌──────────┐            ┌──────────┐
│          │            │          │
│  GPIO 23 ├───────────►│ MOSI/SDA │
│  GPIO 18 ├───────────►│ SCK/CLK  │
│  GPIO 16 ├───────────►│ DC       │
│  GPIO 17 ├───────────►│ RES/RST  │
│  GPIO 5  ├───────────►│ CS       │
│  3.3V    ├───────────►│ VCC      │
│  GND     ├───────────►│ GND      │
│          │            │          │
└──────────┘            └──────────┘
```

## ⚠️ Important Notes

### Servo Pin Change
**The servo pin has been changed from GPIO 18 to GPIO 19** to avoid conflict with OLED CLK pin.

| Component | Old Pin | New Pin | Reason |
|-----------|---------|---------|--------|
| Servo     | GPIO 18 | GPIO 19 | GPIO 18 is now used for OLED SCK |

### MPU6050 (I2C) Pins
MPU6050 uses I2C, which is on different pins:
- **SDA**: GPIO 21 (default I2C)
- **SCL**: GPIO 22 (default I2C)

## Display Information Shown

The OLED displays the following real-time information:

```
== GIMBAL STATUS ==
WiFi: OK -45
MQTT: Connected
Roll: 5.2 deg
Err:  0.3 deg
Servo: 95 deg
P:5.0 I:0.5 D:0.3
```

### Display Elements:
1. **WiFi Status**: Connection status and signal strength (RSSI)
2. **MQTT Status**: MQTT broker connection status
3. **Roll Angle**: Current roll angle in degrees
4. **Error**: PID error value
5. **Servo Position**: Current servo position (0-180°)
6. **PID Parameters**: Current Kp, Ki, Kd values

## Update Rate
- **OLED Update**: 100ms (10 Hz)
- **MQTT Publish**: 50ms (20 Hz)
- **Control Loop**: 20ms (50 Hz)

## Troubleshooting

### Display Not Working
1. **Check Wiring**: Verify all connections match the pinout
2. **Check Display Type**: Ensure you have SPI version (not I2C)
3. **Check Power**: OLED should light up when powered (may show random pixels)
4. **Check Serial Monitor**: Look for "OLED Display Initialized!" message

### Display Shows Garbled Text
- Check SCK and MOSI connections
- Verify DC pin is connected correctly
- Try adding 100nF capacitor near VCC/GND on OLED

### Display Is Dim
- Check VCC voltage (should be 3.3V or 5V depending on module)
- Some OLED modules have adjustable contrast

### System Won't Start
- The code will continue to run even if OLED fails to initialize
- Check Serial Monitor for initialization messages
- If MPU6050 fails, system will halt (as IMU is critical)

## Software Configuration

### Key Code Sections

**Pin Definitions:**
```cpp
#define OLED_MOSI   23  // Data
#define OLED_CLK    18  // Clock
#define OLED_DC     16  // Data/Command
#define OLED_CS     5   // Chip Select
#define OLED_RESET  17  // Reset
```

**Initialization:**
```cpp
if(!display.begin(SSD1306_SWITCHCAPVCC)) {
    Serial.println(F("SSD1306 allocation failed"));
} else {
    Serial.println("OLED Display Initialized!");
}
```

**Update Function:**
```cpp
void updateOLED() {
    display.clearDisplay();
    // ... draw text and data
    display.display();
}
```

## Alternative OLED Modules

### If You Have I2C OLED (Not SPI)
Change the initialization to:
```cpp
#define OLED_ADDR   0x3C  // or 0x3D
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// In setup():
if(!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    // error
}
```

I2C Wiring (Much Simpler):
- SDA → GPIO 21
- SCL → GPIO 22
- VCC → 3.3V
- GND → GND

## Performance Considerations

- **SPI is faster** than I2C (but uses more pins)
- **Update interval** of 100ms is a good balance between readability and performance
- Display update takes ~10-20ms, which doesn't interfere with 20ms control loop
- If experiencing jitter, increase `oledUpdateInterval` to 200ms

## Future Enhancements

Possible additions to display:
- [ ] Graph/bar for roll angle visualization
- [ ] Battery voltage (if using battery)
- [ ] Uptime counter
- [ ] Temperature from MPU6050
- [ ] Network strength indicator (graphical)
- [ ] Animated stabilization indicator

## Testing Without OLED

The system will work fine without OLED:
- All serial debug output remains active
- MQTT publishing continues normally
- Dashboard app still receives data
- Only visual feedback on device is missing

This is useful for initial testing or if display is not yet available.
