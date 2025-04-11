import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Nest API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
     # MQTT Settings
    MQTT_BROKER: str = os.getenv("MQTT_BROKER", "mosquitto")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", 1883))
    MQTT_USERNAME: str = os.getenv("MQTT_USERNAME", "admin")
    MQTT_PASSWORD: str = os.getenv("MQTT_PASSWORD", "1107")


settings = Settings()