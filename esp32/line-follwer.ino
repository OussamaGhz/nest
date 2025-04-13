#include <QTRSensors.h>

// QTR-8A sensor array configuration
#define NUM_SENSORS    8
#define TIMEOUT        2500  // waits for 2500 microseconds for sensor outputs to go low
QTRSensorsAnalog qtr((unsigned char[]) {36, 39, 34, 35, 32, 33, 25, 26}, NUM_SENSORS);
unsigned int sensorValues[NUM_SENSORS];

// L298N motor driver configuration
// Motor A - Left motor
#define MOTOR_LEFT_IN1     13
#define MOTOR_LEFT_IN2     12
#define MOTOR_LEFT_EN      14  // PWM pin for speed control

// Motor B - Right motor
#define MOTOR_RIGHT_IN1    27
#define MOTOR_RIGHT_IN2    26
#define MOTOR_RIGHT_EN     25  // PWM pin for speed control

// PWM properties for ESP32
#define PWM_FREQUENCY      1000
#define PWM_RESOLUTION     8
#define PWM_CHANNEL_LEFT   0
#define PWM_CHANNEL_RIGHT  1

// Line following parameters
#define LINE_POSITION_SETPOINT 3500  // Center position (0-7000)
#define MAX_SPEED           255      // Maximum motor speed
#define BASE_SPEED          150      // Default motor speed

// PID control variables
float Kp = 0.25;  // Proportional gain - adjust based on testing
float Ki = 0.0;   // Integral gain
float Kd = 0.5;   // Derivative gain
int lastError = 0;
int integral = 0;

// Button pin for starting the robot after calibration
#define START_BUTTON_PIN   0  // GPIO0 (often the BOOT button)

// LED for indicating calibration status
#define LED_PIN            2  // Built-in LED on most ESP32 boards

void setup() {
  Serial.begin(115200);
  
  // Setup motor control pins
  pinMode(MOTOR_LEFT_IN1, OUTPUT);
  pinMode(MOTOR_LEFT_IN2, OUTPUT);
  pinMode(MOTOR_RIGHT_IN1, OUTPUT);
  pinMode(MOTOR_RIGHT_IN2, OUTPUT);
  
  // Configure PWM for motor speed control
  ledcSetup(PWM_CHANNEL_LEFT, PWM_FREQUENCY, PWM_RESOLUTION);
  ledcSetup(PWM_CHANNEL_RIGHT, PWM_FREQUENCY, PWM_RESOLUTION);
  ledcAttachPin(MOTOR_LEFT_EN, PWM_CHANNEL_LEFT);
  ledcAttachPin(MOTOR_RIGHT_EN, PWM_CHANNEL_RIGHT);
  
  // Configure indicator LED and button
  pinMode(LED_PIN, OUTPUT);
  pinMode(START_BUTTON_PIN, INPUT_PULLUP);
  
  // Stop motors initially
  setMotorSpeeds(0, 0);
  
  // Calibration indicator
  digitalWrite(LED_PIN, HIGH);
  delay(1000);
  
  // Calibrate the QTR sensors
  Serial.println("Calibrating sensors. Move the robot over the line back and forth...");
  for (int i = 0; i < 200; i++) {
    // Flash the LED during calibration
    if (i % 20 == 0) {
      digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    }
    qtr.calibrate();
    delay(10);
  }
  
  Serial.println("Calibration complete");
  
  // Indicate calibration is complete
  digitalWrite(LED_PIN, LOW);
  
  // Print calibration values for debugging
  Serial.println("Calibration values:");
  for (int i = 0; i < NUM_SENSORS; i++) {
    Serial.print(qtr.calibratedMinimumOn[i]);
    Serial.print(" ");
  }
  Serial.println();
  
  for (int i = 0; i < NUM_SENSORS; i++) {
    Serial.print(qtr.calibratedMaximumOn[i]);
    Serial.print(" ");
  }
  Serial.println();
  
  // Wait for button press to start line following
  Serial.println("Press the start button to begin line following");
  while (digitalRead(START_BUTTON_PIN) == HIGH) {
    delay(10);
  }
  delay(500);  // Debounce
}

void loop() {
  // Read the line position (0-7000, with 3500 being the center)
  unsigned int position = qtr.readLine(sensorValues);
  
  // Calculate the error from the line position
  int error = position - LINE_POSITION_SETPOINT;
  
  // Calculate PID components
  integral += error;
  int derivative = error - lastError;
  
  // Apply constraints to integral to prevent wind-up
  integral = constrain(integral, -1000, 1000);
  
  // Calculate motor adjustment
  int motorAdjustment = Kp * error + Ki * integral + Kd * derivative;
  
  // Store the current error for the next iteration
  lastError = error;
  
  // Calculate motor speeds
  int leftSpeed = BASE_SPEED - motorAdjustment;
  int rightSpeed = BASE_SPEED + motorAdjustment;
  
  // Ensure speeds are within valid range
  leftSpeed = constrain(leftSpeed, -MAX_SPEED, MAX_SPEED);
  rightSpeed = constrain(rightSpeed, -MAX_SPEED, MAX_SPEED);
  
  // Set motor speeds
  setMotorSpeeds(leftSpeed, rightSpeed);
  
  // Optional debugging
  Serial.print("Position: ");
  Serial.print(position);
  Serial.print(" Error: ");
  Serial.print(error);
  Serial.print(" Left: ");
  Serial.print(leftSpeed);
  Serial.print(" Right: ");
  Serial.println(rightSpeed);
  
  // Short delay to prevent overwhelming serial output
  delay(10);
}

// Function to set the speed of both motors
void setMotorSpeeds(int leftSpeed, int rightSpeed) {
  // Control left motor direction and speed
  if (leftSpeed >= 0) {
    // Forward
    digitalWrite(MOTOR_LEFT_IN1, HIGH);
    digitalWrite(MOTOR_LEFT_IN2, LOW);
    ledcWrite(PWM_CHANNEL_LEFT, leftSpeed);
  } else {
    // Backward
    digitalWrite(MOTOR_LEFT_IN1, LOW);
    digitalWrite(MOTOR_LEFT_IN2, HIGH);
    ledcWrite(PWM_CHANNEL_LEFT, -leftSpeed);
  }
  
  // Control right motor direction and speed
  if (rightSpeed >= 0) {
    // Forward
    digitalWrite(MOTOR_RIGHT_IN1, HIGH);
    digitalWrite(MOTOR_RIGHT_IN2, LOW);
    ledcWrite(PWM_CHANNEL_RIGHT, rightSpeed);
  } else {
    // Backward
    digitalWrite(MOTOR_RIGHT_IN1, LOW);
    digitalWrite(MOTOR_RIGHT_IN2, HIGH);
    ledcWrite(PWM_CHANNEL_RIGHT, -rightSpeed);
  }
}