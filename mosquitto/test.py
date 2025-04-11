import paho.mqtt.client as mqtt
import time

# MQTT Settings
broker = "localhost"  # Change to your broker address
port = 1883
username = "robot_operator"
password = "1107" # 
robot_id = "robot1"

# Create client
client = mqtt.Client()
client.username_pw_set(username, password)

# Callback functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe(f"robot/{robot_id}/position", qos=1)
        print(f"Subscribed to robot/{robot_id}/position")
    else:
        print(f"Failed to connect, return code: {rc}")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.topic} -> {msg.payload.decode()}")

# Set callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect
client.connect(broker, port, 60)
client.loop_start()

# Keep the script running to receive messages
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
    client.loop_stop()
    client.disconnect()