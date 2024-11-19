from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship

from backEnd.database import Base

from backEnd.enums import CategoryEnum


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable= False)
    password = Column(String(255), nullable=False)
    name = Column(String, nullable=False)

    # Relationship to reviews
    reviews = relationship("Review", back_populates="user")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    totalCount = Column(Integer, nullable=False)
    sold = Column(Integer, nullable=False)

    # Relationship with the Order model
    orders = relationship("Order", back_populates="book")
    # Add relationship to reviews
    reviews = relationship("Review", back_populates="book")


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category_type = Column(Enum(CategoryEnum), nullable=False)  # Enum for category_type

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    order_date = Column(DateTime, nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Define relationship with the Book model
    book = relationship("Book", back_populates="orders")


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Float, nullable=False)
    comment = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with Book
    book = relationship("Book", back_populates="reviews")
    # Relationship with User (Optional, for clarity and navigation)
    user = relationship("User", back_populates="reviews", lazy="joined")





