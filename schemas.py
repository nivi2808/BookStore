from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=20)
    name: str

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    email: EmailStr
    name: str

    class Config:
        orm_mode = True