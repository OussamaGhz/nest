from pydantic import BaseModel

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role: str = "operator"  # Default to operator if not specified

class User(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True
        from_attributes = True  # For newer Pydantic versions