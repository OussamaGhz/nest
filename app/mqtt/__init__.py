import threading
from app.mqtt.broker import run_broker

# Start MQTT broker in a separate thread
broker_thread = None

def start_mqtt_broker():
    global broker_thread
    broker_thread = threading.Thread(target=run_broker, daemon=True)
    broker_thread.start()
    return broker_thread.is_alive()
