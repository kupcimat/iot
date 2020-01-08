// include adafruit DHT sensor library
#include <DHT.h>

// DHT sensor data pin
#define DHTPIN 2
// DHT sensor type
#define DHTTYPE DHT22

// declare DHT sensor
DHT dht(DHTPIN, DHTTYPE);

// declare constants
const int delay_ms = 10;
// protocol constants
const char message_delimiter = '\n';
const String message_get_environment = "get environment";
const String message_invalid = "invalid request";

void setup()
{
  // initialize DHT sensor
  dht.begin();
  // initialize serial and wait for port to open
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect, needed for native USB
  }
}

void loop()
{
  if (Serial.available() > 0) {
    String request = Serial.readStringUntil(message_delimiter);
    String response = message_invalid;

    if (request == message_get_environment) {
      response = getEnvironment();
    }

    Serial.println(response);
  }

  // wait before next read
  delay(delay_ms);
}

String getEnvironment()
{
  // read sensor values
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // return sensor values
  String result = "humidity=";
  result += humidity;
  result += ";temperature=";
  result += temperature;
  return result;
}
