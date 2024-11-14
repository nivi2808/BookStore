from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, EmailStr, Field, constr
from enum import Enum
from models import CategoryEnum

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=20)
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


class Category(str, Enum):
    LITERATURE = "LITERATURE"
    NONFICTION = "NONFICTION"
    ACTION = "ACTION"
    THRILLER = "THRILLER"
    TECHNOLOGY = "TECHNOLOGY"
    DRAMA = "DRAMA"
    POETRY = "POETRY"
    MEDIA = "MEDIA"
    OTHERS = "OTHERS"
    # Add more categories if needed
    class Config:
        orm_mode = True
        from_attributes = True


class BookData(BaseModel):
    id: int
    title: str = Field(..., min_length=2)
    author: str = Field(..., min_length=1)
    # category: Category = Field(..., min_length=1)
    category: CategoryEnum
    price: float = Field(..., gt=1)
    totalCount: int = Field(..., gt=1)
    sold: int = Field(..., gt=1)

    class Config:
        orm_mode = True
        from_attributes = True

class ApiResponse(BaseModel):
    status: str
    message: str
    data: Optional[List[BookData]] = None
    # data: Optional[BookResponse]

    timestamp: str = datetime.utcnow().isoformat()
    errors: Optional[Dict[str, str]] = None

    class Config:
        orm_mode = True
        from_attributes = True

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    category: str
    price: float
    totalCount: int
    sold: int

    class Config:
        orm_mode = True
        from_attributes = True



