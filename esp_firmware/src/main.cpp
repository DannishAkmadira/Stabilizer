#include <WiFi.h>
#include <WiFiManager.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <ESP32Servo.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// OLED SPI Pin Configuration
#define OLED_MOSI   23  // Data (MOSI/SDA)
#define OLED_CLK    18  // Clock (SCK)
#define OLED_DC     16  // Data/Command
#define OLED_CS     5   // Chip Select
#define OLED_RESET  17  // Reset

// OLED Display dimensions
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

// Create OLED display object with SPI
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT,
  OLED_MOSI, OLED_CLK, OLED_DC, OLED_RESET, OLED_CS);

WiFiClient espClient;
PubSubClient mqttClient(espClient);

const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_topic = "gimbal/stabilizer";
const char* mqtt_topic_cmd = "gimbal/command";

unsigned long lastMqttPublish = 0;
const unsigned long mqttPublishInterval = 50;

Adafruit_MPU6050 mpu;
Servo servoRoll;

const int SERVO_ROLL_PIN = 19;  // Changed from 18 (conflicted with OLED_CLK)
int servoRollPos = 90;

// OLED update tracking
unsigned long lastOledUpdate = 0;
const unsigned long oledUpdateInterval = 100;  // Update every 100ms

float angleRoll = 0;
float targetAngleRoll = 0;
float errorRoll = 0;
float lastErrorRoll = 0;
float integralRoll = 0;
float derivativeRoll = 0;

float Kp = 5.0;
float Ki = 0.5;
float Kd = 0.3;

unsigned long lastTime = 0;
float dt = 0.01;
float alpha = 0.96;

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.print("MQTT [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);
  
  if (message.startsWith("PID:")) {
    String pidValues = message.substring(4);
    int firstComma = pidValues.indexOf(',');
    int secondComma = pidValues.indexOf(',', firstComma + 1);
    
    if (firstComma > 0 && secondComma > firstComma) {
      Kp = pidValues.substring(0, firstComma).toFloat();
      Ki = pidValues.substring(firstComma + 1, secondComma).toFloat();
      Kd = pidValues.substring(secondComma + 1).toFloat();
      integralRoll = 0;
      
      Serial.print("PID Updated: Kp=");
      Serial.print(Kp);
      Serial.print(", Ki=");
      Serial.print(Ki);
      Serial.print(", Kd=");
      Serial.println(Kd);
    }
  }
  else if (message.startsWith("TARGET:")) {
    targetAngleRoll = message.substring(7).toFloat();
    Serial.print("Target angle set to: ");
    Serial.println(targetAngleRoll);
  }
}

void updateOLED() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  
  // Title
  display.setCursor(0, 0);
  display.println(F("== GIMBAL STATUS =="));
  
  // WiFi Status
  display.setCursor(0, 10);
  if (WiFi.status() == WL_CONNECTED) {
    display.print(F("WiFi: OK "));
    display.println(WiFi.RSSI());
  } else {
    display.println(F("WiFi: Disconnected"));
  }
  
  // MQTT Status
  display.setCursor(0, 20);
  if (mqttClient.connected()) {
    display.println(F("MQTT: Connected"));
  } else {
    display.println(F("MQTT: Disconnected"));
  }
  
  // Roll Angle
  display.setCursor(0, 30);
  display.print(F("Roll: "));
  display.print(angleRoll, 1);
  display.println(F(" deg"));
  
  // Error
  display.setCursor(0, 40);
  display.print(F("Err:  "));
  display.print(errorRoll, 1);
  display.println(F(" deg"));
  
  // Servo Position
  display.setCursor(0, 50);
  display.print(F("Servo: "));
  display.print(servoRollPos);
  display.println(F(" deg"));
  
  // PID Values (small text)
  display.setCursor(0, 58);
  display.setTextSize(1);
  display.print(F("P:"));
  display.print(Kp, 1);
  display.print(F(" I:"));
  display.print(Ki, 1);
  display.print(F(" D:"));
  display.print(Kd, 1);
  
  display.display();
}

void reconnectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("Connecting to MQTT broker...");
    
    String clientId = "Gimbal-" + String(random(0xffff), HEX);
    
    if (mqttClient.connect(clientId.c_str())) {
      Serial.println("connected!");
      mqttClient.subscribe(mqtt_topic_cmd);
      Serial.print("Subscribed to: ");
      Serial.println(mqtt_topic_cmd);
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" retrying in 5s...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  WiFiManager wifiManager;
  if (!wifiManager.autoConnect("GimbalAP")) {
    Serial.println("Failed to connect and hit timeout");
    ESP.restart();
  }
  
  Serial.println("");
  Serial.println("WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  mqttClient.setServer(mqtt_server, mqtt_port);
  mqttClient.setCallback(mqttCallback);
  mqttClient.setBufferSize(512);
  
  Serial.println("\n=== MQTT Configuration ===");
  Serial.print("Broker: ");
  Serial.print(mqtt_server);
  Serial.print(":");
  Serial.println(mqtt_port);
  Serial.print("Publishing to: ");
  Serial.println(mqtt_topic);
  Serial.print("Listening on: ");
  Serial.println(mqtt_topic_cmd);
  Serial.println("=========================\n");
  
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");
  
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  
  // Initialize OLED display
  if(!display.begin(SSD1306_SWITCHCAPVCC)) {
    Serial.println(F("SSD1306 allocation failed"));
    // Continue without display
  } else {
    Serial.println("OLED Display Initialized!");
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0, 0);
    display.println(F("Gimbal Stabilizer"));
    display.println(F("Initializing..."));
    display.display();
    delay(1000);
  }
  
  ESP32PWM::allocateTimer(0);
  servoRoll.setPeriodHertz(50);
  servoRoll.attach(SERVO_ROLL_PIN, 500, 2400);
  servoRoll.write(servoRollPos);
  
  Serial.println("Gimbal Stabilizer ROLL-Axis Initialized!");
  Serial.println("Calibrating... Keep the gimbal level and stable");
  delay(2000);
  
  lastTime = millis();
}

void loop() {
  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  mqttClient.loop();
  
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("PID:")) {
      String pidValues = command.substring(4);
      int firstComma = pidValues.indexOf(',');
      int secondComma = pidValues.indexOf(',', firstComma + 1);
      
      if (firstComma > 0 && secondComma > firstComma) {
        Kp = pidValues.substring(0, firstComma).toFloat();
        Ki = pidValues.substring(firstComma + 1, secondComma).toFloat();
        Kd = pidValues.substring(secondComma + 1).toFloat();
        integralRoll = 0;
        
        Serial.print("PID Updated via Serial - Kp: ");
        Serial.print(Kp, 2);
        Serial.print(", Ki: ");
        Serial.print(Ki, 2);
        Serial.print(", Kd: ");
        Serial.println(Kd, 2);
      }
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
  integralRoll = constrain(integralRoll, -25, 25);  // Anti-windup lebih ketat untuk stabilitas
  
  // Reset integral jika servo sudah mentok di batas (anti-windup protection)
  if ((servoRollPos >= 175 && errorRoll > 0) || (servoRollPos <= 5 && errorRoll < 0)) {
    integralRoll *= 0.5;  // Kurangi integral saat mentok
  }
  
  // Derivative term dengan filter agresif untuk mengurangi jitter
  float rawDerivative = (errorRoll - lastErrorRoll) / dt;
  derivativeRoll = 0.9 * derivativeRoll + 0.1 * rawDerivative;  // Heavy low-pass filter (90% old, 10% new)
  
  // PID output calculation
  float outputRoll = Kp * errorRoll + Ki * integralRoll + Kd * derivativeRoll;
  
  // Store current error for next iteration
  lastErrorRoll = errorRoll;
  
  // Convert PID output to servo position dengan batas yang lebih aman
  // Batasi output PID untuk menghindari mentok di 0° atau 180°
  float limitedOutput = constrain(outputRoll, -80, 80);  // Batas lebih kecil dari 90
  
  // Tambahkan deadband untuk mengurangi micro-jitter di sekitar target
  if (abs(errorRoll) < 0.5) {  // Deadband 0.5°
    limitedOutput *= 0.3;  // Kurangi output drastis saat sudah dekat target
  }
  
  int newServoPos = 90 + limitedOutput;
  
  // Safety check - pastikan servo tidak benar-benar mentok
  newServoPos = constrain(newServoPos, 10, 170);  // Margin 10° dari batas ekstrem
  
  // Smooth servo movement - hindari perubahan tiba-tiba
  // Hanya update servo jika perubahan cukup signifikan (mengurangi jitter kecil)
  if (abs(newServoPos - servoRollPos) > 1 || abs(errorRoll) > 2.0) {
    servoRollPos = newServoPos;
    servoRoll.write(servoRollPos);
  }
  
  // Print debug information untuk monitoring
  Serial.print("Roll: ");
  Serial.print(angleRoll, 2);
  Serial.print("° | Err: ");
  Serial.print(errorRoll, 2);
  Serial.print("° | PID(");
  Serial.print(outputRoll, 1);
  Serial.print(") | Servo: ");
  Serial.print(servoRollPos);
  Serial.print("° | I: ");
  Serial.print(integralRoll, 1);
  Serial.print(" | Gyro: ");
  Serial.print(gyroRateRoll, 1);
  Serial.println(" °/s");
  
  unsigned long currentMillis = millis();
  if (currentMillis - lastMqttPublish >= mqttPublishInterval) {
    lastMqttPublish = currentMillis;
    
    String jsonData = "{\"r\":";
    jsonData += String(angleRoll, 2);
    jsonData += ",\"g\":";
    jsonData += String(gyroRateRoll, 2);
    jsonData += ",\"s\":";
    jsonData += String(servoRollPos);
    jsonData += ",\"e\":";
    jsonData += String(errorRoll, 2);
    jsonData += ",\"i\":";
    jsonData += String(integralRoll, 1);
    jsonData += "}";
    
    if (mqttClient.connected()) {
      mqttClient.publish(mqtt_topic, jsonData.c_str());
    }
    
    Serial.println(jsonData);
  }
  
  // Update OLED display
  if (currentMillis - lastOledUpdate >= oledUpdateInterval) {
    lastOledUpdate = currentMillis;
    updateOLED();
  }
  
  delay(20);
}