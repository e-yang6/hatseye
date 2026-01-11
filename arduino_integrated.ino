// HATSEYE Arduino Integration - Ultrasonic Sensor Motor Control
// Array of pins
const int trigPins[] = {2, 4, 7, 8};
const int echoPins[] = {3, 11, 12, 13};
const int motorPins[] = {5, 6, 9, 10}; // All PWM pins

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < 4; i++) {
    pinMode(trigPins[i], OUTPUT);
    pinMode(echoPins[i], INPUT);
    pinMode(motorPins[i], OUTPUT);
  }
}

void loop() {
  // Store sensor data for all 4 sensors
  int distances[4];
  int intensities[4];
  
  for (int i = 0; i < 4; i++) {
    // 1. Trigger the specific sensor
    digitalWrite(trigPins[i], LOW);
    delayMicroseconds(2);
    digitalWrite(trigPins[i], HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPins[i], LOW);

    // 2. Measure distance
    long duration = pulseIn(echoPins[i], HIGH, 30000); // 30ms timeout
    int distance = duration * 0.034 / 2;
    distances[i] = distance;

    // 3. Logic: If no reading or out of range, turn off motor
    int intensity = 0;
    if (distance > 0 && distance < 150) {
      // Map 5cm (200 strength) to 50cm (0 strength)
      intensity = map(distance, 5, 150, 170, 1);
    }
    
    // Constrain and write to the specific motor
    intensity = constrain(intensity, 1, 170);
    analogWrite(motorPins[i], intensity);
    intensities[i] = intensity;
  }
  
  // Send all sensor data as JSON (best format for Flask integration)
  Serial.print("{\"sensors\":[");
  for (int i = 0; i < 4; i++) {
    Serial.print("{\"id\":");
    Serial.print(i + 1);
    Serial.print(",\"distance\":");
    Serial.print(distances[i]);
    Serial.print(",\"intensity\":");
    Serial.print(intensities[i]);
    Serial.print("}");
    if (i < 3) Serial.print(",");
  }
  Serial.println("]}");
  
  delay(20); // Short delay to prevent sensor cross-talk
}
