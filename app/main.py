from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.core.mqtt import mqtt_client
import json

# Create tables in database
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to Nest API"}

@app.on_event("startup")    
async def startup_event():
    routes = [{"path": route.path, "name": route.name} for route in app.routes]
    print("Available routes:", routes)
    
    # Save routes to a JSON file
    with open("routes.json", "w") as f:
        json.dump(routes, f, indent=4)
    mqtt_client.connect()

@app.on_event("shutdown")
async def shutdown_event():
    
    mqtt_client.disconnect()