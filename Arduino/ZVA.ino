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
int prevMinutes = 0;
int prevSeconds = 0;
int prevBlinkDelay = 0;
int blinkDelay = 0;

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
        int new_delay = doc["total_seconds"];
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
  if(blinkDelay != 0 )
  {
    // Extract the measurement time values from the JSON document
    int minutes = doc["minutes"];
    int seconds = doc["seconds"];

    // If this is the first measurement, use the total seconds as the initial blink delay
    if (prevBlinkDelay == 0) {
      prevBlinkDelay = doc["total_seconds"];
      prevBlinkDelay *= 1000;
    }

    // Determine whether the measurement time values have changed
    if (minutes != prevMinutes || seconds != prevSeconds) {
      // Update the blink delay based on the total seconds
      int blinkDelay = doc["total_seconds"];
      blinkDelay *= 1000;

      // Blink the LED for the specified measurement time
      int blinkCount = blinkDelay / 1000;
      while (blinkCount > 0) {
        digitalWrite(LED_PIN, HIGH);
        delay(blinkDelay / 2);
        digitalWrite(LED_PIN, LOW);
        delay(blinkDelay / 2);
        blinkCount--;
        sensors.requestTemperatures();
        getDataFromSensor();

      }

      // Store the current measurement time values and blink delay as previous values
      prevMinutes = minutes;
      prevSeconds = seconds;
      prevBlinkDelay = blinkDelay;
    } else {
      // Blink the LED with the previous delay
      digitalWrite(LED_PIN, HIGH);
      delay(prevBlinkDelay / 2);
      digitalWrite(LED_PIN, LOW);
      delay(prevBlinkDelay / 2);
      getDataFromSensor();
    }
  }
  else
  {
    Serial.println("Setup not Load.");
    }
}

void getDataFromSensor()
{
  float tempC = sensors.getTempCByIndex(0); // the index 0 refers to the first device
  Serial.println(tempC);
}