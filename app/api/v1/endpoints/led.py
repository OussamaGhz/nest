from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import json
import time
from app.core.mqtt import mqtt_client

router = APIRouter()

# Store the last received state
last_led_state = None
state_received = False

class LEDCommand(BaseModel):
    state: str  # "on" or "off"

class LEDState(BaseModel):
    state: str
    status: str

# MQTT Callback to handle state updates
def on_state_message(client, userdata, msg):
    global last_led_state, state_received
    try:
        payload = json.loads(msg.payload.decode())
        last_led_state = payload
        state_received = True
    except json.JSONDecodeError:
        pass

# Subscribe to state topic when starting
mqtt_client.on_message = on_state_message
mqtt_client.subscribe("robot/esp32/state")

@router.post("/control", status_code=status.HTTP_200_OK)
async def control_led(command: LEDCommand):
    """Control the ESP32 LED via MQTT with confirmation"""
    global state_received
    
    if command.state not in ["on", "off"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State must be 'on' or 'off'"
        )
    
    topic = "robot/esp32/commands"
    payload = json.dumps({"command": command.state})
    state_received = False
    
    try:
        success = mqtt_client.publish(
            topic=topic,
            payload=payload,
            qos=1
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to publish MQTT message"
            )
        
        # Wait for confirmation (timeout after 3 seconds)
        timeout = 3
        start_time = time.time()
        while not state_received and (time.time() - start_time) < timeout:
            mqtt_client.loop()  # Process MQTT messages
            time.sleep(0.1)
        
        if not state_received:
            return {
                "status": "pending",
                "message": "Command sent but no confirmation received",
                "confirmed": False
            }
        
        return {
            "status": "success",
            "message": f"LED {command.state} command confirmed",
            "confirmed": True,
            "device_state": last_led_state
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending MQTT message: {str(e)}"
        )