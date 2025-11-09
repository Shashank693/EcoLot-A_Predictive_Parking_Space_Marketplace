#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// --- Config: update for your network / server / spot ---
const char* ssid = "**********";
const char* password = "***********";
const char* serverName = "http://192.168.1.####:5000/api/sensor/update"; // no trailing slash

const int spot_id = 2;                 // unique spot id for this IR sensor (must match DB)
const char* lot_name = "Home";  // must match admin lot name
const char* spot_number = "A002";          // must match spot numbering

// --- IR sensor hardware config ---
const int irPin = 15;         // GPIO pin connected to IR sensor digital output
const bool irActiveLow = true; // set true if sensor outputs LOW when obstacle detected
const int SAMPLES = 5;       // readings to sample for stability
const int STABLE_REQUIRED = 3; // consecutive samples required to accept a change

// --- Timing ---
const unsigned long READING_INTERVAL = 5000UL;   // ms between sample rounds
const unsigned long FORCE_REPORT_MS = 300000UL; // force-report every 5 minutes

// --- State ---
String lastStatus = "";
unsigned long lastUpdate = 0;
int stableCount = 0;
String candidateStatus = "";

void setup() {
  Serial.begin(115200);
  pinMode(irPin, INPUT);
  WiFi.begin(ssid, password);
  Serial.print("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

bool readIrOnce() {
  int v = digitalRead(irPin);
  bool occupied = irActiveLow ? (v == LOW) : (v == HIGH);
  return occupied;
}

bool readIrStable() {
  // majority sampling
  int occCount = 0;
  for (int i = 0; i < SAMPLES; ++i) {
    if (readIrOnce()) occCount++;
    delay(20);
  }
  return (occCount * 2) >= SAMPLES; // majority -> occupied
}

bool sendStatus(const char* status) {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.reconnect();
    return false;
  }

  HTTPClient http;
  http.begin(serverName);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(10000);

  StaticJsonDocument<256> doc;
  doc["spot_id"] = spot_id;
  doc["lot_name"] = lot_name;
  doc["spot_number"] = spot_number;
  doc["status"] = status;       // "O" or "A"
  doc["device_id"] = WiFi.macAddress();
  doc["timestamp_ms"] = millis();

  String payload;
  serializeJson(doc, payload);

  Serial.print("POST -> ");
  Serial.println(payload);

  int code = http.POST(payload);
  if (code > 0) {
    String resp = http.getString();
    Serial.printf("HTTP %d : %s\n", code, resp.c_str());
    http.end();
    return (code >= 200 && code < 300);
  } else {
    Serial.printf("HTTP Error: %d (%s)\n", code, http.errorToString(code).c_str());
    http.end();
    return false;
  }
}

void loop() {
  // sample + debouncing logic
  String observed = readIrStable() ? "O" : "A";

  if (candidateStatus == "" || candidateStatus != observed) {
    candidateStatus = observed;
    stableCount = 1;
  } else {
    stableCount++;
  }

  bool shouldSend = false;
  if (stableCount >= STABLE_REQUIRED && candidateStatus != lastStatus) {
    // confirmed change
    shouldSend = true;
  } else if ((millis() - lastUpdate) >= FORCE_REPORT_MS) {
    // periodic forced report
    shouldSend = true;
    candidateStatus = observed; // report current observed even if same
  }

  if (shouldSend) {
    bool ok = sendStatus(candidateStatus.c_str());
    if (ok) {
      lastStatus = candidateStatus;
      lastUpdate = millis();
      Serial.printf("Reported status %s for spot %d\n", candidateStatus.c_str(), spot_id);
    } else {
      Serial.println("Report failed; will retry on next interval");
    }
    // reset debounce so repeated immediate sends don't occur
    stableCount = 0;
    candidateStatus = "";
  }

  delay(READING_INTERVAL);
}
