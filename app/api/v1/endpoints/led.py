from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
import json
from app.core.mqtt import mqtt_client

router = APIRouter()

class LEDCommand(BaseModel):
    state: str  # "on" or "off"

@router.post("/control", status_code=status.HTTP_200_OK)
async def control_led(command: LEDCommand):
    """Control the ESP32 LED via MQTT"""
    if command.state not in ["on", "off"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State must be 'on' or 'off'"
        )
    
    # Publish MQTT message to control the LED
    topic = "robot/esp32/commands"
    payload = json.dumps({"command": command.state})
    
    try:
        # Your mqtt_client.publish returns a boolean, not an object with an rc attribute
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
            
        return {"status": "success", "message": f"LED {command.state} command sent"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending MQTT message: {str(e)}"
        )