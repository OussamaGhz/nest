import asyncio
import json
import logging
from asyncio_mqtt import Client, MqttError
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global MQTT client
mqtt_client = None

async def connect_mqtt():
    """Connect to MQTT broker"""
    global mqtt_client
    
    try:
        mqtt_client = Client(
            hostname=settings.MQTT_BROKER_HOST,
            port=settings.MQTT_BROKER_PORT,
            username=settings.MQTT_USERNAME,
            password=settings.MQTT_PASSWORD,
            client_id=settings.MQTT_CLIENT_ID
        )
        await mqtt_client.connect()
        logger.info(f"Connected to MQTT broker at {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
        return True
    except MqttError as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        return False

async def disconnect_mqtt():
    """Disconnect from MQTT broker"""
    global mqtt_client
    if mqtt_client:
        await mqtt_client.disconnect()
        logger.info("Disconnected from MQTT broker")

async def publish_message(topic, message):
    """Publish a message to an MQTT topic"""
    global mqtt_client
    
    if not mqtt_client:
        success = await connect_mqtt()
        if not success:
            return False
    
    try:
        if isinstance(message, dict):
            message = json.dumps(message)
        
        await mqtt_client.publish(topic, message)
        logger.info(f"Published message to {topic}: {message}")
        return True
    except MqttError as e:
        logger.error(f"Failed to publish message: {e}")
        return False

async def subscribe(topic, callback):
    """Subscribe to an MQTT topic with a callback function"""
    global mqtt_client
    
    if not mqtt_client:
        success = await connect_mqtt()
        if not success:
            return False
    
    try:
        await mqtt_client.subscribe(topic)
        logger.info(f"Subscribed to topic: {topic}")
        
        async with mqtt_client.filtered_messages(topic) as messages:
            async for message in messages:
                try:
                    payload = message.payload.decode()
                    logger.info(f"Received message on {topic}: {payload}")
                    await callback(topic, payload)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        
        return True
    except MqttError as e:
        logger.error(f"Failed to subscribe to topic: {e}")
        return False
