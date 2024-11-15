import enum
from datetime import datetime
from typing import Optional, Dict, List, Union, Any
from pydantic import BaseModel, EmailStr, Field, constr
from enum import Enum

from pydantic._internal._known_annotated_metadata import schemas

# from starlette import schemas

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
    category: CategoryEnum
    price: float = Field(..., gt=1)
    totalCount: int = Field(..., gt=1)
    sold: int = Field(..., gt=1)

    class Config:
        orm_mode = True
        from_attributes = True


class SoldBookResponse(BaseModel):
    title: str
    category: str
    sold: int

    class Config:
        orm_mode = True
        from_attributes = True


class ApiResponse(BaseModel):
    status: str
    message: str

    data: Optional[List[BookData]] = None
    timestamp: str = datetime.utcnow().isoformat()
    errors: Optional[Dict[str, str]] = None

    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

class ApiResponseSold(BaseModel):
    status: str
    message: str
    data: Optional[List[SoldBookResponse]] = None
    timestamp: str = datetime.utcnow().isoformat()
    errors: Optional[Dict[str, str]] = None

    class Config:
        orm_mode = True
        from_attributes = True

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    category: Category
    price: float
    totalCount: int
    sold: int

    class Config:
        orm_mode = True
        from_attributes = True


class ApiResponseListBook(BaseModel):
    status: str
    message: str
    data: Optional[List[dict]] = None
    timestamp: str = datetime.utcnow().isoformat()
    errors: Optional[dict] = None

    class Config:
        from_attributes = True
        orm_mode = True

class ApiResponseBook(BaseModel):
    status: str
    message: str
    # data: Union[BookResponse, List[BookResponse]] = None  # No "schemas." prefix here
    # data: Optional[Union[dict, List[dict]]] = None  # Accept both a dict and a list
    # data: Union[schemas.BookResponse, List[schemas.BookResponse]] = None
    data: Union["BookResponse", List["BookResponse"]] = None
    timestamp: str = datetime.utcnow().isoformat()
    errors: Optional[dict] = None

    class Config:
        from_attributes = True
        orm_mode = True

class QuantityUpdateRequest(BaseModel):
    quantity: int

class order(BaseModel):
    status: str
    message: str
    data: Union[BookResponse, List[BookResponse]] = None
    timestamp: str = datetime.utcnow().isoformat()
    errors: Optional[dict] = None

    class Config:
        orm_mode = True



class ApiResponseOrder(BaseModel):
    status: str
    message: str
    data: Union[BookResponse, List[BookResponse]] = None  # No "schemas." prefix here
    # data: Union["BookResponse", List["BookResponse"]] = None  # Use forward reference
    # data: Union[schemas.OrderResponse, List[schemas.OrderResponse]] = None
    timestamp: str = datetime.utcnow().isoformat()
    errors: Optional[dict] = None

    class Config:
        orm_mode = True
        from_attributes = True

class OrderItemRequest(BaseModel):
    book_id: int
    quantity: int

class Order(BaseModel):
    quantity: int

class OrderRequest(BaseModel):
    orders: List[Order]

class PlaceOrderRequest(BaseModel):
    orders: List[OrderItemRequest]

class OrderDetail(BaseModel):
    id: int
    title: str
    author: str
    category: str
    price: float
    total_price: float


class PlaceOrderResponse(BaseModel):
    order_details: List[OrderDetail]
    total_amount: float
    order_timestamp: str



class ApiResponseListOrder(BaseModel):
    status: str
    message: str
    data: dict  # Or define a model if you want stricter validation
    timestamp: str
    errors: Optional[List[str]]

    class Config:
        orm_mode = True
        from_attributes = True

