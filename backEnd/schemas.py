from datetime import datetime
from typing import Optional, Dict, List, Union
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


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

class AuthResponse(BaseModel):
    token: str
    token_type:str
    class Config:
        orm_mode = True



class CategoryEnum(str, Enum):
    LITERATURE = "LITERATURE"
    NONFICTION = "NONFICTION"
    ACTION = "ACTION"
    THRILLER = "THRILLER"
    TECHNOLOGY = "TECHNOLOGY"
    DRAMA = "DRAMA"
    POETRY = "POETRY"
    MEDIA = "MEDIA"
    OTHERS = "OTHERS"



class CategoryResponse(BaseModel):
    category: CategoryEnum  # Use the Enum directly in the response model

    class Config:
        use_enum_values = True  # Ensures the response returns the string values instead of the enum type

class Category(BaseModel):
    id: int
    name: str
    category_type: CategoryEnum

    class Config:
        orm_mode = True


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
    category: str
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
    timestamp: str = datetime.utcnow().isoformat()
    errors: Optional[dict] = None

    class Config:
        orm_mode = True
        from_attributes = True



class Order(BaseModel):
    quantity: int

class OrderRequest(BaseModel):
    orders: List[Order]

class OrderItemRequest(BaseModel):
    book_id: int
    quantity: int

class PlaceOrderRequest(BaseModel):
    items: List[OrderItemRequest]



class OrderDetail(BaseModel):
    book_id: int
    quantity: int
    total_price: float


class PlaceOrderResponse(BaseModel):
    order_details: List[OrderDetail]
    total_amount: float
    order_timestamp: str



class ApiResponseListOrder(BaseModel):
    status: str
    message: str
    data: List[OrderDetail] # Or define a model if you want stricter validation
    timestamp: datetime
    errors: Optional[List[str]]

    class Config:
        orm_mode = True
        from_attributes = True

class OrderResponse(BaseModel):
    status: str
    message: Optional[str] = None  # Add a message field
    data: Optional[List[OrderDetail]] = None  # The order details (data)
    total_amount: float
    timestamp: str  # For example, you can use the current time
    errors: Optional[List[str]] = []  # List of error messages if any


class ApiResponseListCategory(BaseModel):
    status: str
    message: str
    data: List[str]
    timestamp: str
    # errors: Optional[List[str]] = []


class ReviewRequest(BaseModel):
    rating: float = Field(..., ge= 0, le= 5,description="Rating should be between 0 and 5")
    comment: str = Field(None, min_length=2,max_length=100,description="Optional comments for the review")

    class Config:
         orm_mode = True



class ReviewResponse(BaseModel):
    id: int
    rating: float
    comment: str
    userEmail: str
    createdAt: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class ErrorResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict] = None
    timestamp: datetime
    errors: Dict[str, str]
    details: Optional[Dict] = None
    path: str
    class Config:
        orm_mode = True
        from_attributes = True



