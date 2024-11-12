from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import models, schemas
import database
from database import engine, get_db

# Create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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
        
        # Create and save the new user
        new_user = models.User(email=user.email, password=user.password, name=user.name)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return schemas.UserResponse(email=new_user.email, name=new_user.name)

    except HTTPException as e:
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
        error_response = format_error_response(
            status_code=500,
            error="Internal Server Error",
            message="An unexpected error occurred",
            path=str(request.url)
        )
        return JSONResponse(status_code=500, content=error_response)