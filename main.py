import os
import logging
from typing import Optional
import jwt
import pdb
from fastapi import FastAPI, Depends, HTTPException, Request, status, Header
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import models, schemas
from database import engine, get_db
from passlib.context import CryptContext
from datetime import datetime, timedelta



# from venv.bin import uvicorn

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('_name_')

# Create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

# JWT Secret and Algorithm
SECRET_KEY = 'SECRET_KEY'  # Use a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiry time

# Simulate a blacklist in memory (use Redis or a database for production)
blacklist = set()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



app = FastAPI()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# create JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def is_token_blacklisted(token: str) -> bool:
    return token in blacklist

# decode JWT token
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if is_token_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been invalidated. Please log in again.",
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired. Please log in again.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token. Please log in again.",
        )


def format_error_response(status_code: int, error: str, message: str, path: str) -> dict:
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "status": status_code,
        "error": error,
        "message": message,
        "details": None,
        "path": path
    }



@app.post("/api/auth/signup", response_model=schemas.UserResponse, status_code=200)
async def signup(user: schemas.UserCreate, request: Request, db: Session = Depends(get_db)):
    # pdb.set_trace/()
    try:
        # Check if the email already exists
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            error_response = format_error_response(
                status_code=409,
                error="Conflict",
                message="User already exists",
                path=str(request.url)
            )
            return JSONResponse(status_code=409, content=error_response)

        hashed_password = hash_password(user.password)
        
        # Create and save the new user
        new_user = models.User(email=user.email, password=hashed_password, name=user.name)
        db.add(new_user)
        db.commit()
        logger.info('user added to database sucessfully')
        db.refresh(new_user)

        return schemas.UserResponse(email=new_user.email, name=new_user.name)

    except HTTPException as e:
        logger.error('during signup-',e)
        raise e

    except ValueError as ve:
        error_response = format_error_response(
            status_code=400,
            error="Bad Request",
            message=str(ve),
            path=str(request.url)
        )
        return JSONResponse(status_code=400, content=error_response)

    except Exception as e:
        logger.error('during signup-last exception block',e)
        error_response = format_error_response(
            status_code=500,
            error="Internal Server Error",
            message="An unexpected error occurred",
            path=str(request.url)
        )
        return JSONResponse(status_code=500, content=error_response)

@app.post("/api/auth/signin",  status_code=200)
async def signin(user: schemas.UserLogin, request: Request, db: Session = Depends(get_db)):
    try:
        # Query user from the database
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if not db_user or not verify_password(user.password, db_user.password):
            error_response = format_error_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                error="Unauthorized",
                message="Incorrect email or password",
                path=str(request.url)
            )
            logger.error('error during sigin in on first condition', error_response)
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=error_response)

        # Generate JWT token if user authentication succeeds
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.email}, expires_delta=access_token_expires
        )

        return {
            "token": access_token,
            "token_type": "bearer",
            "user": {"email": db_user.email, "name": db_user.name}
        }

    except HTTPException as e:
        logger.error('during signin-',e)
        raise e

    except Exception as e:
        logger.error('during signin-last exception block',e)
        error_response = format_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Internal Server Error",
            message="An unexpected error occurred",
            path=str(request.url)
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response)

# @app.post("/api/auth/logout")
# async def logout(token: str = Depends(oauth2_scheme)):
#     # Check if token is already blacklisted
#     if token in blacklist:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Token is already logged out or invalid"
#         )
#
#     # Add the token to the blacklist
#     blacklist.add(token)
#     return {"message": "Successfully logged out"}


# Logout endpoint
@app.post("/api/auth/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    # Check if token is valid or already blacklisted
    try:
        decode_access_token(token)  # Validate the token and check blacklist
        if token in blacklist:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Token already logged out or invalid"}
            )
        blacklist.add(token)  # Add the token to the blacklist
        return {"message": "Successfully logged out"}
    except HTTPException as e:
        logger.error("HTTP Exception during logout", e)
        raise e
    except Exception as e:
        logger.error("Unhandled exception during logout", e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An unexpected error occurred"}
        )









