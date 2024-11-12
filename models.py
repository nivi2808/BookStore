from sqlalchemy import Column, String, Integer
import database
from database import Base
from sqlalchemy.schema import CheckConstraint

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable= False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)

