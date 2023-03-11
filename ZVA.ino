#include <ArduinoJson.h>

// Define LED pin
const int LED_PIN = 13;

// Variables to store previous measurement time values
int prevMinutes = 0;
int prevSeconds = 0;

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
}

void loop() 
{
  // Read the incoming data
  String data;
  if(Serial.available())
  {
    data = Serial.readString();
  }
  // Parse the JSON string
  StaticJsonDocument<200> doc;
  deserializeJson(doc, data);

  // Extract the measurement time values from the JSON document
  int minutes = doc["minutes"];
  int seconds = doc["seconds"];
  int totalSeconds = doc["total_seconds"];

  // Determine whether the measurement time values have changed
  if (minutes != prevMinutes || seconds != prevSeconds) {
    // Blink the LED for the specified measurement time
    int blinkCount = totalSeconds;
    while (blinkCount > 0) {
      digitalWrite(LED_PIN, HIGH);
      delay(500);
      digitalWrite(LED_PIN, LOW);
      delay(500);
      blinkCount--;
    }

    // Store the current measurement time values as previous values
    prevMinutes = minutes;
    prevSeconds = seconds;
  } else {
    // Blink the LED endlessly until new measurement time values are received
    while (true) {
      digitalWrite(LED_PIN, HIGH);
      delay(500);
      digitalWrite(LED_PIN, LOW);
      delay(500);
    }
  }
}