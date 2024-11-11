from sqlalchemy import Column, String, Integer
import database
from database import Base
from sqlalchemy.schema import CheckConstraint

class User(Base):
    _tablename_ = "users"

    email = Column(String, unique=True, index=True, nullable= False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)


    __table_args__ = (
        CheckConstraint('LENGTH(password) BETWEEN 6 AND 20', name='password_length_check'),
    )
