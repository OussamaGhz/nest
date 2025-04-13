#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h> // Add at top of file

// WiFi credentials
const char* ssid = "wizards";
const char* password = "wizards 123";

// MQTT Broker settings (replace with your Ngrok TCP URL if testing remotely)
const char* mqtt_server = "192.168.137.113";  // e.g., "192.168.1.100" or "4.tcp.ngrok.io"
const int mqtt_port = 1883;  // Default MQTT port (or Ngrok-assigned port)
const char* mqtt_user = "admin";
const char* mqtt_password = "1107";

// MQTT Topics
const char* command_topic = "robot/esp32/commands";  // Matches FastAPI topic

// LED Pin (adjust based on your wiring)
const int led_pin = 15;  // Built-in LED (GPIO2)

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println("\nConnecting to WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

// Add a state topic for confirmation
const char* state_topic = "robot/esp32/state";

// Track current LED state
bool current_led_state = false;

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("]: ");
  
  // Print raw message
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

  // Parse JSON
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, payload, length);
  
  if (error) {
    Serial.print("JSON parse failed: ");
    Serial.println(error.c_str());
    return;
  }

  const char* command = doc["command"];
  bool state_changed = false;
  
  if (strcmp(command, "on") == 0 && !current_led_state) {
    digitalWrite(led_pin, HIGH);
    current_led_state = true;
    state_changed = true;
    Serial.println("LED turned ON");
  } 
  else if (strcmp(command, "off") == 0 && current_led_state) {
    digitalWrite(led_pin, LOW);
    current_led_state = false;
    state_changed = true;
    Serial.println("LED turned OFF");
  }

  // Publish state confirmation
  if (state_changed) {
    StaticJsonDocument<100> state_doc;
    state_doc["state"] = current_led_state ? "on" : "off";
    state_doc["status"] = "success";
    
    char buffer[100];
    serializeJson(state_doc, buffer);
    client.publish(state_topic, buffer);
  }
}


void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String client_id = "esp32-client-" + String(random(0xffff), HEX);

    if (client.connect(client_id.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("Connected to MQTT broker!");
      client.subscribe(command_topic);
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(led_pin, OUTPUT);
  digitalWrite(led_pin, LOW);  // Initialize LED off

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}