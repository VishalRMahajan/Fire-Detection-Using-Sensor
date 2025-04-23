#include <ESP8266WiFi.h>
#include <WebSocketsClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// Wi-Fi credentials
const char* ssid = "Vishal Mahajan 2";
const char* password = "qwerty@12345";

// WebSocket server details
const char* websocket_host = "192.168.15.222";
const uint16_t websocket_port = 8000;
const char* websocket_path = "/ws";

// Location (St. Francis Institute of Technology)
const float latitude = 19.2436162;
const float longitude = 72.8558439;

// Sensor Pins
#define DHTPIN D4
#define DHTTYPE DHT11
#define MQ2_PIN A0
#define FLAME_SENSOR_PIN D0

// Sensor & WebSocket Setup
DHT dht(DHTPIN, DHTTYPE);
WebSocketsClient webSocket;

void setup() {
  Serial.begin(115200);
  delay(500);

  // Wi-Fi connection
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 30) {
    delay(500);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ Wi-Fi Connected");
    Serial.print("📡 IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ Wi-Fi failed. Restarting...");
    ESP.restart();
  }

  // Init sensors
  dht.begin();
  pinMode(FLAME_SENSOR_PIN, INPUT);

  // Init WebSocket
  webSocket.begin(websocket_host, websocket_port, websocket_path);
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
}

void loop() {
  webSocket.loop();

  static unsigned long lastRead = 0;
  if (millis() - lastRead >= 2000) {
    lastRead = millis();

    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    int smoke_level = analogRead(MQ2_PIN);
    bool flame_detected = digitalRead(FLAME_SENSOR_PIN) == LOW;

    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("⚠️ DHT11 read error");
      return;
    }

    // 🔥 Fire Detection Logic
    bool temp_high = temperature > 45.0;
    bool smoke_high = smoke_level > 400;
    bool fire_detected = flame_detected || (smoke_high && temp_high);

    // 📟 Debug Output
    Serial.printf("Temp: %.2f °C, Hum: %.2f %%, Smoke: %d, Flame: %s, Fire: %s\n",
                  temperature, humidity, smoke_level,
                  flame_detected ? "YES" : "NO",
                  fire_detected ? "🔥 YES" : "NO");

    // 📤 Prepare JSON
    StaticJsonDocument<512> doc;
    doc["temperature"] = temperature;
    doc["humidity"] = humidity;
    doc["smoke_level"] = smoke_level;
    doc["flame_detected"] = flame_detected ? 1 : 0;
    doc["fire_detected"] = fire_detected ? 1 : 0;
    doc["latitude"] = static_cast<float>(latitude);
    doc["longitude"] = static_cast<float>(longitude);

    char buffer[512];
    serializeJson(doc, buffer);
    Serial.println(buffer); // 📄 Print outgoing JSON
    webSocket.sendTXT(buffer);
  }
}

void webSocketEvent(WStype_t type, uint8_t* payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      Serial.println("🔴 WebSocket disconnected");
      break;
    case WStype_CONNECTED:
      Serial.println("🟢 WebSocket connected");
      break;
    case WStype_TEXT:
      Serial.printf("📩 Received: %s\n", payload);
      break;
    case WStype_ERROR:
      Serial.printf("⚠️ Error: %s\n", payload);
      break;
    default:
      break;
  }
}
