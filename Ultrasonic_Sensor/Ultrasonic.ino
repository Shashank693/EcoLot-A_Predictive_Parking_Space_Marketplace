#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "*********";
const char* password = "**********";

// Ultrasonic sensor pins
const int trigPin = 5;  // GPIO5
const int echoPin = 18; // GPIO18

// Parking spot configuration - must match your database
const int spot_id = 1;                     // Update with actual spot ID from admin UI
const char* lot_name = "Home"; // Must match lot name exactly
const char* spot_number = "A001";          // Must match spot number format

// Flask server details - update with your PC's IP address
const char* serverName = "http://192.168.1.####:5000/api/sensor/update";

// Sensor configuration
const int DISTANCE_THRESHOLD = 50;  // cm - adjust based on mounting height
const int READING_INTERVAL = 10000; // ms between readings (10 seconds)
const int SAMPLES = 5;              // readings to average for stability
const int TIMEOUT = 30000;          // ultrasonic timeout (microseconds)

// Status tracking
String lastStatus = "";
unsigned long lastUpdateTime = 0;

void setup() {
  Serial.begin(115200);
  
  // Configure sensor pins
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("\nConnecting to WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nConnected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("MAC Address: ");
  Serial.println(WiFi.macAddress());
}

long readUltrasonicDistance() {
  // Clear trigger
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
  // Send pulse
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Read echo with timeout
  long duration = pulseIn(echoPin, HIGH, TIMEOUT);
  
  // Convert to distance or return max on timeout
  if (duration == 0) {
    return 999;
  }
  
  return duration * 0.034 / 2; // Speed of sound conversion
}

float getAverageDistance() {
  float total = 0;
  int validReadings = 0;
  
  for (int i = 0; i < SAMPLES; i++) {
    long distance = readUltrasonicDistance();
    if (distance < 900) { // Valid reading
      total += distance;
      validReadings++;
    }
    delay(50); // Brief pause between readings
  }
  
  if (validReadings == 0) return 999;
  return total / validReadings;
}

bool sendStatusToServer(const char* status) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected - reconnecting...");
    WiFi.reconnect();
    delay(5000);
    return false;
  }

  HTTPClient http;
  http.begin(serverName);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(10000); // 10 second timeout

  // Prepare JSON payload
  StaticJsonDocument<256> doc;
  doc["spot_id"] = spot_id;
  doc["lot_name"] = lot_name;
  doc["spot_number"] = spot_number;
  doc["status"] = status;
  doc["device_id"] = WiFi.macAddress();
  doc["timestamp"] = millis();
  doc["distance"] = String(getAverageDistance());

  String payload;
  serializeJson(doc, payload);

  Serial.print("Sending: ");
  Serial.println(payload);

  int httpCode = http.POST(payload);
  bool success = false;

  if (httpCode > 0) {
    String response = http.getString();
    Serial.printf("HTTP Response code: %d\n", httpCode);
    Serial.printf("Response: %s\n", response.c_str());
    success = (httpCode == 200);
  } else {
    Serial.printf("HTTP Error: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
  return success;
}

void loop() {
  float distance = getAverageDistance();
  String newStatus = (distance < DISTANCE_THRESHOLD) ? "O" : "A";
  
  // Print current readings
  Serial.printf("\nDistance: %.1f cm\n", distance);
  Serial.printf("Current Status: %s\n", newStatus.c_str());
  
  // Send updates on status change or every 5 minutes
  unsigned long now = millis();
  if (newStatus != lastStatus || (now - lastUpdateTime) > 300000) {
    if (sendStatusToServer(newStatus.c_str())) {
      lastStatus = newStatus;
      lastUpdateTime = now;
    }
  }
  
  delay(READING_INTERVAL);
}
