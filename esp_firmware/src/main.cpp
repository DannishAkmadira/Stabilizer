#include <WiFi.h>
#include <WiFiManager.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <ESP32Servo.h>

// WiFi TCP Server
WiFiServer server(8888);  // Server pada port 8888
WiFiClient client;

// Create an instance of the MPU6050 sensor
Adafruit_MPU6050 mpu;

// Servo instance for 1-axis gimbal
Servo servoRoll;  // Servo untuk stabilisasi ROLL (miring kiri-kanan)

// Servo pin
const int SERVO_ROLL_PIN = 18;  // GPIO 18 for Roll servo

// Servo center position (90 degrees = horizontal/stable)
int servoRollPos = 90;

// PID control variables for Roll axis
float angleRoll = 0;
float targetAngleRoll = 0;  // Target angle (horizontal/stable = 0)
float errorRoll = 0;
float lastErrorRoll = 0;
float integralRoll = 0;
float derivativeRoll = 0;

// PID constants (tune these values for better performance)
float Kp = 5.0;   // Proportional gain - untuk respon lebih agresif
float Ki = 1.0;  // Integral gain - menghilangkan steady-state error
float Kd = 0.01;   // Derivative gain - mengurangi overshoot

// Timing variables
unsigned long lastTime = 0;
float dt = 0.01;  // Time step (10ms)

// Complementary filter constant
float alpha = 0.96;

void setup() {
  Serial.begin(115200);
  
  // Initialize WiFiManager
  WiFiManager wifiManager;
  
  // Attempt to connect to a saved WiFi network
  // If connection fails, it starts an access point with the name "GimbalAP"
  if (!wifiManager.autoConnect("GimbalAP")) {
    Serial.println("Failed to connect and hit timeout");
    // Restart the ESP32
    ESP.restart();
  }
  
  // If successfully connected to WiFi
  Serial.println("");
  Serial.println("WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  // Start TCP Server
  server.begin();
  Serial.println("TCP Server started on port 8888");
  Serial.println("Connect your laptop to the same WiFi network");
  Serial.print("Use IP: ");
  Serial.print(WiFi.localIP());
  Serial.println(":8888");
  
  // Initialize the MPU6050 sensor
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");
  
  // Set accelerometer range
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  // Set gyroscope range
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  // Set filter bandwidth
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  
  // Initialize servo
  ESP32PWM::allocateTimer(0);
  servoRoll.setPeriodHertz(50);    // Standard 50Hz servo
  
  servoRoll.attach(SERVO_ROLL_PIN, 500, 2400);  // Attach servo with min/max pulse width
  
  // Set servo to center position
  servoRoll.write(servoRollPos);
  
  Serial.println("Gimbal Stabilizer ROLL-Axis Initialized!");
  Serial.println("Calibrating... Keep the gimbal level and stable");
  delay(2000);
  
  lastTime = millis();
}

void loop() {
  // Check for new WiFi client connections
  if (!client.connected()) {
    client = server.available();
    if (client) {
      Serial.println("New client connected via WiFi!");
    }
  }
  
  // Get new sensor events with the readings
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  
  // Calculate time difference
  unsigned long currentTime = millis();
  dt = (currentTime - lastTime) / 1000.0;
  lastTime = currentTime;
  
  // Calculate ROLL angle from accelerometer (in degrees)
  // MPU6050 menghadap depan, Roll (miring kiri-kanan) ada di sumbu Y
  // Roll angle dihitung dari X dan Z acceleration
  float accelAngleRoll = atan2(a.acceleration.x, a.acceleration.z) * 180.0 / PI;
  
  // Integrate gyroscope data for Roll axis (convert rad/s to deg/s and integrate)
  // Roll rotation ada di sumbu Y, jadi gunakan gyro.y
  float gyroRateRoll = g.gyro.y * 180.0 / PI;
  
  // Complementary filter: combine accelerometer and gyroscope data for Roll
  angleRoll = alpha * (angleRoll + gyroRateRoll * dt) + (1 - alpha) * accelAngleRoll;
  
  // ===== PID STABILIZATION FOR ROLL AXIS (sumbu Y) =====
  
  // Calculate error (DIBALIK untuk kompensasi yang benar)
  // Ketika miring kanan (+), error positif → servo ke kanan (180°)
  // Ketika miring kiri (-), error negatif → servo ke kiri (0°)
  errorRoll = angleRoll - targetAngleRoll;  // DIBALIK: angle - target (bukan target - angle)
  
  // Integral term with anti-windup
  integralRoll += errorRoll * dt;
  integralRoll = constrain(integralRoll, -20, 20);  // Anti-windup limits
  
  // Derivative term
  derivativeRoll = (errorRoll - lastErrorRoll) / dt;
  
  // PID output calculation
  float outputRoll = Kp * errorRoll + Ki * integralRoll + Kd * derivativeRoll;
  
  // Store current error for next iteration
  lastErrorRoll = errorRoll;
  
  // Convert PID output to servo position
  // Ketika miring KANAN (angle positif) → servo ke KANAN (menuju 180°)
  // Ketika miring KIRI (angle negatif) → servo ke KIRI (menuju 0°)
  servoRollPos = 90 + constrain(outputRoll, -90, 90);  // Stabil=90°, Kanan=180°, Kiri=0°
  
  // Write to servo
  servoRoll.write(servoRollPos);
  
  // Print debug information untuk monitoring
  Serial.print("Roll Angle (sumbu Y): ");
  Serial.print(angleRoll, 2);
  Serial.print("° | Error: ");
  Serial.print(errorRoll, 2);
  Serial.print("° | Servo: ");
  Serial.print(servoRollPos);
  Serial.print("° | Gyro Y: ");
  Serial.print(gyroRateRoll, 2);
  Serial.println(" deg/s");
  
  // Kirim data dalam format untuk dashboard
  // Format: DATA:ROLL_ANGLE,GYRO_Y_RATE,SERVO_POS
  String data = "DATA:";
  data += String(angleRoll, 2);  // Roll angle (miring kiri-kanan pada sumbu Y)
  data += ",";
  data += String(gyroRateRoll, 2);  // Gyro rate dalam deg/s
  data += ",";
  data += String(servoRollPos);  // Posisi servo
  data += "\n";
  
  // Kirim ke Serial Monitor
  Serial.print(data);
  
  // Kirim ke WiFi client jika ada yang terhubung
  if (client && client.connected()) {
    client.print(data);
  }
  
  delay(10);  // 100Hz update rate untuk stabilisasi yang smooth
}