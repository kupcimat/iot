// include adafruit DHT sensor library
#include <DHT.h>

// DHT sensor data pin
#define DHTPIN 2
// DHT sensor type
#define DHTTYPE DHT22

// declare DHT sensor
DHT dht(DHTPIN, DHTTYPE);

// declare constants
const int delay_ms = 2000;

// declare variables
float humidity;
float temperature;

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
  // read sensor values
  humidity = dht.readHumidity();
  temperature = dht.readTemperature();

  // send sensor values
  Serial.print("humidity=");
  Serial.print(humidity);
  Serial.print(";temperature=");
  Serial.println(temperature);

  // wait before next read
  delay(delay_ms);
}
