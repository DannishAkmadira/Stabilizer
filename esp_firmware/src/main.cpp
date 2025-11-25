#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <ESP32Servo.h>
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define OLED_MOSI   23
#define OLED_CLK    18
#define OLED_DC     16
#define OLED_CS     5
#define OLED_RESET  17

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT,
  OLED_MOSI, OLED_CLK, OLED_DC, OLED_RESET, OLED_CS);

bool enableWiFi = false;
bool enableMQTT = false;

unsigned long lastDataPublish = 0;
const unsigned long dataPublishInterval = 20;

Adafruit_MPU6050 mpu;
Servo servoRoll;

const int SERVO_ROLL_PIN = 19;
const int RESET_WIFI_PIN = 0;
int servoRollPos = 90;

unsigned long lastOledUpdate = 0;
const unsigned long oledUpdateInterval = 100;

float angleRoll = 0;
float targetAngleRoll = 0;
float errorRoll = 0;
float lastErrorRoll = 0;
float integralRoll = 0;
float derivativeRoll = 0;

float Kp = 7.0;
float Ki = 0.5;
float Kd = 0;

unsigned long lastTime = 0;
float dt = 0.01;
float alpha = 0.96;

void updateOLED() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  
  display.setCursor(0, 0);
  display.println(F("== GIMBAL SERIAL =="));
  
  display.setCursor(0, 10);
  display.println(F("Mode: USART"));
  
  display.setCursor(0, 25);
  display.print(F("Roll: "));
  display.print(angleRoll, 1);
  display.println(F(" deg"));
  
  display.setCursor(0, 35);
  display.print(F("Err:  "));
  display.print(errorRoll, 1);
  display.println(F(" deg"));
  
  display.setCursor(0, 45);
  display.print(F("Servo: "));
  display.print(servoRollPos);
  display.println(F(" deg"));
  
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

void setup() {
  Serial.begin(921600);
  delay(100);
  
  Serial.println("\n\n=================================");
  Serial.println("  GIMBAL STABILIZER - SERIAL MODE");
  Serial.println("  Baud Rate: 921600");
  Serial.println("  Update Rate: 50Hz (20ms)");
  Serial.println("=================================\n");
  
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
  
  if(!display.begin(SSD1306_SWITCHCAPVCC)) {
    Serial.println(F("SSD1306 allocation failed"));
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
  delay(500);
  
  lastTime = millis();
  
  Serial.println("\n🚀 === SYSTEM READY - GIMBAL RUNNING ===");
  Serial.println("⚡ Serial/USART mode - Data streaming enabled!\n");
}

void loop() {
  yield();
  
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
  
  sensors_event_t a, g, temp;
  if (!mpu.getEvent(&a, &g, &temp)) {
    Serial.println("⚠️ MPU6050 read error!");
    delay(10);
    return;
  }
  
  unsigned long currentTime = millis();
  dt = (currentTime - lastTime) / 1000.0;
  if (dt <= 0 || dt > 1.0) dt = 0.02;
  lastTime = currentTime;
  
  float accelAngleRoll = atan2(a.acceleration.x, a.acceleration.z) * 180.0 / PI;
  float gyroRateRoll = g.gyro.y * 180.0 / PI;
  angleRoll = alpha * (angleRoll + gyroRateRoll * dt) + (1 - alpha) * accelAngleRoll;
  
  errorRoll = angleRoll - targetAngleRoll;
  
  integralRoll += errorRoll * dt;
  integralRoll = constrain(integralRoll, -25, 25);
  
  if ((servoRollPos >= 175 && errorRoll > 0) || (servoRollPos <= 5 && errorRoll < 0)) {
    integralRoll *= 0.5;
  }
  
  float rawDerivative = (errorRoll - lastErrorRoll) / dt;
  derivativeRoll = 0.9 * derivativeRoll + 0.1 * rawDerivative;
  
  float outputRoll = Kp * errorRoll + Ki * integralRoll + Kd * derivativeRoll;
  lastErrorRoll = errorRoll;
  
  float limitedOutput = constrain(outputRoll, -80, 80);
  
  if (abs(errorRoll) < 0.5) {
    limitedOutput *= 0.3;
  }
  
  int newServoPos = 90 + limitedOutput;
  newServoPos = constrain(newServoPos, 10, 170);
  
  if (abs(newServoPos - servoRollPos) > 1 || abs(errorRoll) > 2.0) {
    servoRollPos = newServoPos;
    servoRoll.write(servoRollPos);
  }
  
  unsigned long currentMillis = millis();
  if (currentMillis - lastDataPublish >= dataPublishInterval) {
    lastDataPublish = currentMillis;
    
    Serial.print("{\"r\":");
    Serial.print(angleRoll, 2);
    Serial.print(",\"g\":");
    Serial.print(gyroRateRoll, 2);
    Serial.print(",\"s\":");
    Serial.print(servoRollPos);
    Serial.print(",\"e\":");
    Serial.print(errorRoll, 2);
    Serial.print(",\"i\":");
    Serial.print(integralRoll, 1);
    Serial.println("}");
  }
  
  if (currentMillis - lastOledUpdate >= oledUpdateInterval) {
    lastOledUpdate = currentMillis;
    updateOLED();
  }
  
  delay(10);
}