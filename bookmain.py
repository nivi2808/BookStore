import logging
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import models, schemas
from database import engine, get_db
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('_name_')

# Initialize FastAPI and create tables
app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO format string
        return super().default(obj)


@app.post("/api/bookstore/books/", response_model=schemas.ApiResponse, status_code=status.HTTP_201_CREATED)
async def add_book(book: schemas.BookData, db: Session = Depends(get_db)):
    try:

        existing_book = db.query(models.Book).filter(
            models.Book.title== book.title,
            models.Book.author == book.author,
            models.Book.category == book.category).first()
        if existing_book:
            error_response = schemas.ApiResponse(
                status="error",
                message="Book already exists",
                data=None,
                timestamp=datetime.utcnow().isoformat(),
                errors={
                    "additionalProp1": "A book with this title and author already exists.",
                    "additionalProp2": "Duplicate entry error",
                    "additionalProp3": "Check the book title and author"
                }
            )
            logger.error('error during checking if the book already exists ', error_response)
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=error_response.dict(),
                encoder = DateTimeEncoder)

        # Create a new book instance
        db_book = models.Book(
            title=book.title,
            author=book.author,
            category=book.category,
            price=book.price,
            totalCount=book.totalCount,
            sold=book.sold
        )
        db.add(db_book)
        db.commit()
        db.refresh(db_book)

        # Successful response
        response = schemas.ApiResponse(
            status="success",
            message="Book added successfully",
            data=schemas.BookData(
                id=db_book.id,
                title=db_book.title,
                author=db_book.author,
                category=db_book.category,
                price=db_book.price,
                totalCount=db_book.totalCount,
                sold=db_book.sold
            ),
            timestamp=datetime.utcnow().isoformat(),
            errors=None
        )

        return response

    except Exception as e:
        # Error response
        error_response = schemas.ApiResponse(
            status="error",
            message="Already exists",
            data=None,
            timestamp=datetime.utcnow().isoformat(),
            errors={
                "additionalProp1": str(e),
                "additionalProp2": "Database error" if "db" in str(e) else "Unknown error",
                "additionalProp3": "Ensure all fields are correctly formatted"
            }
        )
        logger.error('error at last exception', error_response)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error_response.dict())


@app.get("/api/bookstore/books/{book_id}", response_model=schemas.ApiResponse, status_code=status.HTTP_200_OK)
async def get_book(book_id:int, db: Session = Depends(get_db)):
    try:

        book = db.query(models.Book).filter(models.Book.id == book_id).first()
        if  book:
            error_response = schemas.ApiResponse(
                status="error",
                message="Book exists",
                data=None,
                timestamp=datetime.utcnow().isoformat(),
                errors=None
            errors = {
                "additionalProp1": "A book with this title and author already exists.",
                "additionalProp2": "Duplicate entry error",
                "additionalProp3": "Check the book title and author"
                }
            )
        return book



