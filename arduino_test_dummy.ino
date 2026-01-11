// HATSEYE Arduino Test - Dummy Sensor Data (No Hardware Required)
// Upload this to test the system without actual sensors

void setup()
{
    Serial.begin(9600);
}

void loop()
{
    // Generate random test data for 4 sensors
    Serial.print("{\"sensors\":[");

    for (int i = 0; i < 4; i++)
    {
        // Random distance between 10-100 cm
        int distance = random(10, 100);

        // Calculate intensity based on distance (closer = stronger)
        int intensity = map(distance, 10, 100, 150, 10);

        Serial.print("{\"id\":");
        Serial.print(i + 1);
        Serial.print(",\"distance\":");
        Serial.print(distance);
        Serial.print(",\"intensity\":");
        Serial.print(intensity);
        Serial.print("}");

        if (i < 3)
            Serial.print(",");
    }

    Serial.println("]}");

    delay(100); // Send data every 100ms
}
