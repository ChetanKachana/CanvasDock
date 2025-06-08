/*
 *  ESP32 Firebase Firestore - Read Array from Document Example
 *
 *  This sketch authenticates and fetches a single document from Firestore,
 *  then parses an array of strings from within that document.
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

//--- Your Wi-Fi details ---
const char* ssid = "name";
const char* password = "pass";

//--- Your Firebase project details ---
const char* firebase_api_key = "api_key";
const char* firebase_project_id = "project_id";
//-----------------------------------------------------

// Global variables to store auth data and state
String firebaseIdToken;
bool authenticated = false;
bool dataFetched = false;

// Function prototypes
void authenticateAnonymously();
void getAssignments();


void setup() {
  Serial.begin(115200);
  delay(100);

  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println("---------------------------");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    if (!authenticated) {
      authenticateAnonymously();
    }
    else if (!dataFetched) {
      getAssignments();
      dataFetched = true;
    }
  }
  delay(30000); 
}

void authenticateAnonymously() {
  Serial.println("Attempting to authenticate with Firebase...");
  String auth_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=";
  auth_url += firebase_api_key;

  HTTPClient http;
  http.begin(auth_url);
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST("{\"returnSecureToken\":true}");

  if (httpCode == HTTP_CODE_OK) {
    String payload = http.getString();
    JsonDocument doc;
    deserializeJson(doc, payload);
    firebaseIdToken = String(doc["idToken"].as<const char*>());
    if(firebaseIdToken.length() > 0) {
      Serial.println("Authentication successful!");
      authenticated = true;
    } else {
      Serial.println("Authentication failed: Could not parse ID token.");
    }
  } else {
    Serial.printf("Authentication failed. HTTP Code: %d\n", httpCode);
    String errorPayload = http.getString();
    Serial.println("Error response: " + errorPayload);
  }
  http.end();
  Serial.println("---------------------------");
}

void getAssignments() {
  Serial.println("Fetching Firestore assignments...");

  // Construct the Firestore REST API URL to get the 'assignments' document
  // from the 'display_data' collection.
  String firestore_url = "https://firestore.googleapis.com/v1/projects/";
  firestore_url += firebase_project_id;
  firestore_url += "/databases/(default)/documents/display_data/assignments";

  HTTPClient http;
  http.begin(firestore_url);

  // Add the Authorization header with the ID token
  http.addHeader("Authorization", "Bearer " + firebaseIdToken);

  int httpCode = http.GET();

  if (httpCode == HTTP_CODE_OK) {
    String payload = http.getString();
    Serial.println("Firestore response received.");
    // Serial.println(payload); // Uncomment for full response debugging

    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, payload);

    if (error) {
      Serial.print("deserializeJson() failed: ");
      Serial.println(error.c_str());
      return;
    }

    // Navigate through the JSON to find the "sorted_list" array
    JsonArray assignment_array = doc["fields"]["sorted_list"]["arrayValue"]["values"];

    Serial.println("\n--- Assignments List ---");
    for (JsonObject item : assignment_array) {
      // Each item in the array is an object with a "stringValue" key
      const char* assignment = item["stringValue"];
      if (assignment) {
        Serial.println(assignment);
      }
    }
    Serial.println("------------------------");


  } else {
    Serial.printf("Firestore request failed. HTTP Code: %d\n", httpCode);
    String errorPayload = http.getString();
    Serial.println("Error response: " + errorPayload);
    Serial.println("If error is 401/403, check your Firestore Security Rules.");
    Serial.println("If error is 404, check your Project ID and document path.");
  }

  http.end();
  Serial.println("---------------------------");
}