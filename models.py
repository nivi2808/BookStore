import enum
from sqlalchemy import Column, String, Integer, Float
import database
from database import Base
from sqlalchemy.schema import CheckConstraint

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable= False)
    password = Column(String(255), nullable=False)
    name = Column(String, nullable=False)


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    totalCount = Column(Integer, nullable=False)
    sold = Column(Integer, nullable=False)

class CategoryEnum(str, enum.Enum):
    LITERATURE = "LITERATURE"
    NONFICTION = "NONFICTION"
    ACTION = "ACTION"
    THRILLER = "THRILLER"
    TECHNOLOGY= "TECHNOLOGY"
    DRAMA = "DRAMA"
    POETRY = "POETRY"
    MEDIA = "MEDIA"
    OTHERS = "OTHERS"


    # Add other categories as needed
