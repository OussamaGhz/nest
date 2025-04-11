import asyncio
import logging
from gmqtt import Server
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MQTT Authentication handler
async def authenticate(client_id, username, password, **kwargs):
    # In production, you should validate against your database
    if username == settings.MQTT_USERNAME and password == settings.MQTT_PASSWORD:
        return True
    logger.warning(f"Failed authentication attempt: {client_id}, {username}")
    return False

# Message handler
async def on_message(client_id, topic, payload, qos, **kwargs):
    logger.info(f"Message received from {client_id} on topic {topic}: {payload.decode()}")
    return 0

# Create and configure MQTT server
server = Server()

# Setup broker events
server.on_connect = authenticate
server.on_message = on_message

async def start_broker():
    await server.start(host=settings.MQTT_BROKER_HOST, port=settings.MQTT_BROKER_PORT)
    logger.info(f"MQTT broker started on {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
    
    # Keep the broker running
    while True:
        await asyncio.sleep(1)

async def stop_broker():
    await server.stop()
    logger.info("MQTT broker stopped")

def run_broker():
    """Run the MQTT broker in a separate thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(start_broker())
    except KeyboardInterrupt:
        loop.run_until_complete(stop_broker())
    finally:
        loop.close()
