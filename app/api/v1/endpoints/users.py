from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.schemas.user import User as UserSchema

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def read_user_data(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/admin", response_model=UserSchema)
def read_admin_data(current_user: User = Depends(get_current_admin_user)):
    return current_user