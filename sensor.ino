// include adafruit DHT sensor library
#include <DHT.h>

#define DHTPIN  12    // DHT sensor data pin
#define DHTTYPE DHT22 // DHT sensor type

// declare DHT sensor
DHT dht(DHTPIN, DHTTYPE);

// declare constants
const int delay_ms = 10;

// protocol constants
const char   message_delimiter       = '\n';
const String message_ok              = "ok";
const String message_invalid         = "invalid request";
const String message_get_environment = "getEnvironment";
const String message_set_digit       = "setDigit";
const String message_set_color       = "setColor";

// display constants            0   1   2    3    4   5   6    7    8    9
const byte encodedDigits[] = {119, 96, 59, 121, 108, 93, 95, 112, 127, 125};
const byte segmentPins[]   = {2, 3, 4, 5, 6, 7, 8, 9};

// rgb led constants
const byte redPin   = 13;
const byte greenPin = 11;
const byte bluePin  = 10;

void setup()
{
  // initialize segment display
  pinMode(segmentPins[0], OUTPUT);
  pinMode(segmentPins[1], OUTPUT);
  pinMode(segmentPins[2], OUTPUT);
  pinMode(segmentPins[3], OUTPUT);
  pinMode(segmentPins[4], OUTPUT);
  pinMode(segmentPins[5], OUTPUT);
  pinMode(segmentPins[6], OUTPUT);
  pinMode(segmentPins[7], OUTPUT);

  // initialize rgb led
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);

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

    if (request.equals(message_get_environment)) {
      response = getEnvironment();
    }
    if (request.startsWith(message_set_digit)) {
      String digit = request.substring(message_set_digit.length());
      displayDigit(digit.toInt());
      response = message_ok;
    }
    if (request.startsWith(message_set_color)) {
      String color = request.substring(message_set_color.length());
      displayColor(color.toInt());
      response = message_ok;
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

void displayDigit(long digit) {
  byte singleDigit = digit % 10;
  byte encodedDigit = encodedDigits[singleDigit];
  if (digit > 9) {
    encodedDigit += 128; // overflow
  }

  for (int i = 0; i < 8; i++) {
    if (bitRead(encodedDigit, i) == 1) {
      digitalWrite(segmentPins[i], LOW); // turn on segment
    } else {
      digitalWrite(segmentPins[i], HIGH); // turn off segment
    }
  }
}

void displayColor(long color) {
  byte red = (color >> 16) & 0xFF;
  byte green = (color >> 8) & 0xFF;
  byte blue = color & 0xFF;

  analogWrite(redPin, red);
  analogWrite(greenPin, green);
  analogWrite(bluePin, blue);
}
