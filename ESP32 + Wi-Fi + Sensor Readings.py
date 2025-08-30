#include <WiFi.h>
#include <DHT.h>

// Wi-Fi credentials
const char* ssid = "ESP33";         // 🔁 Your mobile hotspot SSID
const char* password = "12345678";  // 🔁 Your mobile hotspot password

// Sensor Pins
#define DHTPIN 15
#define DHTTYPE DHT11
#define TRIG 19      // ✅ TRIG moved to GPIO 19
#define ECHO 18      // ✅ ECHO moved to GPIO 18
#define WATER A0     // Analog water level sensor

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n✅ WiFi connected!");
  Serial.print("📡 IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Read humidity
  float hum = dht.readHumidity();

  // Read distance
  digitalWrite(TRIG, LOW); delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  long duration = pulseIn(ECHO, HIGH);
  float dist = duration * 0.034 / 2;

  // Read water level (analog)
  int water = analogRead(WATER);

  // Print formatted sensor data to Serial
  Serial.print("Humidity:"); Serial.print(hum);
  Serial.print(",Distance:"); Serial.print(dist);
  Serial.print(",WaterLevel:"); Serial.println(water);

  delay(3000); // 3 seconds delay
}
