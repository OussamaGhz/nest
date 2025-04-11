from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, robots, led

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(robots.router, prefix="/robots", tags=["robots"])
api_router.include_router(led.router, prefix="/led", tags=["led"])
