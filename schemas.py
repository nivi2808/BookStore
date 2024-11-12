from pydantic import BaseModel, EmailStr, Field, constr

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(...,min_length=1)


    # work seamlessy with the ORM and convert the database models to API response
    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    email: EmailStr
    name: str

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True

