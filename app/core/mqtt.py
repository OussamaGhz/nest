import paho.mqtt.client as mqtt
from app.core.config import settings
import logging
import time
import uuid

logger = logging.getLogger(__name__)


class MQTTClient:
    def __init__(self):
        client_id = f"{settings.PROJECT_NAME}-{uuid.uuid4().hex[:8]}"
        self.client = mqtt.Client(client_id=client_id)

        # Only set username/password if they're provided
        if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
            self.client.username_pw_set(
                username=settings.MQTT_USERNAME, password=settings.MQTT_PASSWORD
            )

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.connected = False

    def connect(self):
        try:
            logger.info(
                f"Connecting to MQTT broker at {settings.MQTT_BROKER}:{settings.MQTT_PORT}"
            )
            self.client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            # Try localhost as fallback
            if settings.MQTT_BROKER != "localhost":
                logger.info("Trying localhost as fallback")
                try:
                    self.client.connect("localhost", settings.MQTT_PORT, 60)
                    self.client.loop_start()
                    # Update settings if successful
                    settings.MQTT_BROKER = "localhost"
                    logger.info(
                        f"Successfully connected to localhost:{settings.MQTT_PORT}"
                    )
                except Exception as e2:
                    logger.error(f"Failed to connect to localhost: {e2}")

    def disconnect(self):
        if hasattr(self, "client"):
            try:
                self.client.loop_stop()
                self.client.disconnect()
                logger.info("Disconnected from MQTT broker")
            except Exception as e:
                logger.error(f"Error disconnecting from MQTT: {e}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info("Successfully connected to MQTT broker")
            client.subscribe("robot/+/position", qos=1)
        else:
            conn_codes = {
                1: "incorrect protocol version",
                2: "invalid client identifier", 
                3: "server unavailable",
                4: "bad username or password",
                5: "not authorized",
                6: "server unavailable (duplicate)",
                7: "not authorized (duplicate)"
            }
            error_message = conn_codes.get(rc, f"unknown error {rc}")
            logger.error(f"Failed to connect to MQTT broker: {error_message}")
            self.connected = False

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker: {rc}")

    def on_message(self, client, userdata, msg):
        logger.debug(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
        # Process messages here or dispatch to handlers

    def publish(self, topic, payload, qos=1, retain=False):
        if not self.connected:
            logger.warning(f"Cannot publish to {topic}: Not connected to MQTT broker")
            return False

        try:
            result = self.client.publish(topic, payload, qos=qos, retain=retain)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logger.error(f"Failed to publish to {topic}: {result.rc}")
                return False
            return True
        except Exception as e:
            logger.error(f"Error publishing to {topic}: {e}")
            return False


# Create a global MQTT client instance
mqtt_client = MQTTClient()
