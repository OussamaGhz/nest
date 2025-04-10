from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

# Create tables in database
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to Nest API"}