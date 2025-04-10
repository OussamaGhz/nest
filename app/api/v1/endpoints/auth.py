from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import verify_password, create_access_token, create_refresh_token, get_password_hash
from app.api.dependencies import get_db, get_current_admin_user
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate, User as UserSchema
from jose import jwt
from app.core.config import settings


router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


@router.post("/refresh", response_model=Token)
def refresh_token(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        new_access_token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


@router.post(
    "/create-user", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
def create_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(
    #     get_current_admin_user
    # ),  # Ensures only admins can create users
):
    # Check if user with this username already exists
    db_user = db.query(User).filter(User.username == user_create.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Create new user
    new_user = User(
        username=user_create.username,
        hashed_password=get_password_hash(user_create.password),
        role=user_create.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
