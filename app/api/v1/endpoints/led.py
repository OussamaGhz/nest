from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any
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
    payload = {"command": command.state}
    
    try:
        result = mqtt_client.publish(
            topic=topic,
            payload=str(payload).replace("'", "\""),
            qos=1
        )
        
        if result.rc != 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to publish MQTT message: {result.rc}"
            )
            
        return {"status": "success", "message": f"LED {command.state} command sent"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending MQTT message: {str(e)}"
        )