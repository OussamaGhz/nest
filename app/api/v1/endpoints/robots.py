from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_current_active_user
from app.core.mqtt import mqtt_client
from app.models.user import User
import json

router = APIRouter()

@router.post("/{robot_id}/command")
def send_command(
    robot_id: str,
    command: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Send a command to a specific robot"""
    topic = f"robot/{robot_id}/commands"
    success = mqtt_client.publish(topic, json.dumps(command), qos=1)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send command to robot"
        )
    
    return {"status": "success", "detail": f"Command sent to robot {robot_id}"}

@router.get("/{robot_id}/status")
def get_robot_status(
    robot_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the latest status of a specific robot
    Note: This is a placeholder. You'll need to implement a way to store
    and retrieve the latest status from each robot.
    """
    # You could implement this using a database or in-memory cache
    # that's updated whenever you receive messages on robot/{id}/position
    
    return {"status": "Robot status would be returned here"}