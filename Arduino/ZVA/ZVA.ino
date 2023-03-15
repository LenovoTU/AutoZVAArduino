#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 2

// Create a new instance of the oneWire class to communicate with any OneWire device:
OneWire oneWire(ONE_WIRE_BUS);

// Pass the oneWire reference to DallasTemperature library:
DallasTemperature sensors(&oneWire);

// Define LED pin
const int LED_PIN = 13;

// Variables to store previous measurement time values and blink delay
unsigned long prevMillis = 0;
unsigned long blinkDelay = 0;

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  sensors.begin();
}

void loop() {
  // Wait for incoming data
  StaticJsonDocument<200> doc;
  String data;
  unsigned long start_time = millis();
  
  while (millis() - start_time < 1000) { // wait for up to 1 second
    if (Serial.available()) {
        // Read the incoming data
        data = Serial.readString();  
        // Parse the JSON string
        deserializeJson(doc, data);
        
        unsigned long new_delay = doc["total_seconds"];
        new_delay *= 1000;
        if (new_delay != blinkDelay) {
          blinkDelay = new_delay;
          Serial.print("New blink delay: ");
          Serial.println(blinkDelay);
      } else {
        Serial.println("Input data received, but delay is unchanged.");
      }
      break;
    }
  }

  if (blinkDelay != 0) {
    unsigned long currentMillis = millis();

    // Determine whether it's time for a new measurement
    if (currentMillis - prevMillis >= blinkDelay) {
      // Update the previous measurement time value
      prevMillis += blinkDelay;

      // Blink the LED for the specified measurement time
      int blinkCount = blinkDelay / 1000;
      while (blinkCount > 0) {
        digitalWrite(LED_PIN, HIGH);
        delay(blinkDelay / 2);
        digitalWrite(LED_PIN, LOW);
        delay(blinkDelay / 2);
        blinkCount--;
        sensors.requestTemperatures();
        float tempC = sensors.getTempCByIndex(0); // the index 0 refers to the first device
        Serial.println(tempC);
      }
    }
  } else {
    Serial.println("Setup not loaded.");
  }
}