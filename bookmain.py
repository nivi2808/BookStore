import logging
from lib2to3.fixes.fix_input import context
from pyexpat.errors import messages
from typing import Optional
from fastapi import FastAPI, HTTPException, status, Depends, Query, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from schemas import Category, ApiResponse, BookData

from sqlalchemy.sql.coercions import expect

import models, schemas
from database import engine, get_db
import json
from models import Book

from schemas import BookResponse

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('_name_')

# Initialize FastAPI and create tables
app = FastAPI()
router = APIRouter()
# app.include_router(router)
models.Base.metadata.create_all(bind=engine)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO format string
        return super().default(obj)



logging.basicConfig(level=logging.DEBUG)

@app.on_event("startup")
async def startup():
    for route in app.routes:
        logging.debug(f"Registered route: {route.path} method: {route.methods}")


@router.post("/api/bookstore/books", response_model=schemas.ApiResponse, status_code=status.HTTP_201_CREATED)
async def add_book(book: schemas.BookData, db: Session = Depends(get_db)):
    try:
        # Check if the book already exists
        existing_book = db.query(models.Book).filter(
            models.Book.title == book.title,
            models.Book.author == book.author
        ).first()

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
            # Use % formatting for logger error to prevent format issues
            logger.error('Error during checking if the book already exists: %s', error_response)
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=error_response.dict()
            )

        # Create a new book instance
        db_book = models.Book(
            id=book.id,
            title=book.title,
            author=book.author,
            category=book.category.value,  # Use .value to get the string representation
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
            data=[
                schemas.BookData.from_orm(db_book)  # Populate with .from_orm for consistency
            ],
            timestamp=datetime.utcnow().isoformat(),
            errors=None
        )

        return response

    except Exception as e:
        # Error response
        error_response = schemas.ApiResponse(
            status="error",
            message="Error occurred while adding book",
            data=None,
            timestamp=datetime.utcnow().isoformat(),
            errors={
                "additionalProp1": str(e),
                "additionalProp2": "Database error" if "db" in str(e) else "Unknown error",
                "additionalProp3": "Ensure all fields are correctly formatted"
            }
        )
        # Correctly format the logging to prevent issues
        logger.error('Error at last exception: %s', error_response)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error_response.dict())


@router.get("/api/bookstore/books/{book_id}", response_model=schemas.ApiResponse)
async def get_book_id(book_id:int, db: Session = Depends(get_db)):
    try:

        logging.info(f"Fetching book with ID: {book_id}")
        book = db.query(models.Book).filter(models.Book.id == book_id).first()
        print(book.title)
        if  book:
            logging.info(f"fetched book successfully: {book.title}")

            # Convert the book SQLAlchemy object to a Pydantic BookResponse model
            book_data = schemas.BookResponse.from_orm(book)

            success_response = schemas.ApiResponse(
                status="success",
                message="Book found",
                data=[book_data],
                timestamp=datetime.utcnow().isoformat(),
                errors = None
            )
            return success_response


        logging.info("Book not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )


    except Exception as e:
        logging.error(f"An error occurred while fetching the book: {e}")
        error_response = schemas.ApiResponse(
            status="error",
            message="An error occurred while fetching the book",
            data=None,
            timestamp=datetime.utcnow().isoformat(),
            errors={
                "additionalProp1": str(e),
                "additionalProp2": "Database or server error",
                "additionalProp3": "Ensure correct book ID"

            }
        )
        # raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response.dict())
        # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  context=error_response.dict())
        # Return JSONResponse directly with the error content instead of raising it
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.dict()
        )



@router.get("/api/bookstore/search", response_model=schemas.ApiResponse, status_code=status.HTTP_200_OK)

async def search_books(
            query:Optional[str] = Query(None, min_length=2, description="search a book by title and author"),
            category:Optional[str] = Query(None, min_length=2, description="Category of a book to search"),
            db: Session = Depends(get_db)):
    try:
        logging.info(f"Searching books with query: {query} and category: {category}")

        filters = []


        # If there's a search query, apply it to title, author, and category fields
        if query:
            filters.append(or_(
                models.Book.title.ilike(f"%{query}%"),
                models.Book.author.ilike(f"%{query}%"),
                models.Book.category.ilike(f"%{query}%")
            ))
    # If there's a category filter, apply it to the category field
        if category:
            filters.append(models.Book.category.in_(category.split(",")))

    # Fetch the matching books

        books = db.query(models.Book).filter(*filters).all()  # Apply all filters

    # If no books found, raise 404
        if not books:
            logging.info(f"No books found with query {query}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No books found matching the search criteria."
            )

        # Convert the books to BookResponse models

        # book_data = schemas.BookResponse.from_orm(books[0])
        book_data = [schemas.BookResponse.from_orm(book) for book in books]

        # return the success response
        success_response = schemas.ApiResponse(
            status="success",
            message="Books found",
            data=book_data,
            timestamp=datetime.utcnow().isoformat(),
            errors=None

        )

        logging.info(f"Found {len(books)} books.")
        return success_response

    except HTTPException as http_error:
        logging.error(f"HTTP error occurred: {http_error.detail}")
        raise http_error  # Reraise the HTTPException to handle it with the appropriate status code
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        error_response = schemas.ApiResponse(
            status="error",
            message="Internal server error",
            data=None,
            timestamp=datetime.utcnow().isoformat(),
            errors={
                "additionalProp1": "An unexpected error occurred during the search."
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response.dict()
        )


@router.delete("/api/bookstore/books/{book_id}", response_model=schemas.ApiResponse, status_code=status.HTTP_200_OK)
async def delete_book(book_id:int, db: Session = Depends(get_db)):
    try:
        logging.info("Finding the book")
        book = db.query(models.Book).filter(models.Book.id == book_id).first()

        if not book:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} not found."
            )
        db.delete(book)
        db.commit()
        logging.info("Book deleted")

        # Return success response
        success_response = schemas.ApiResponse(
            status="success",
            message=f"Book with ID {book_id} has been successfully deleted.",
            data=None,
            timestamp=datetime.utcnow().isoformat(),
            errors=None
        )

        logging.info(f"Book with ID {book_id} deleted successfully.")
        return success_response

    except NoResultFound:
        # This is a specific error if the record does not exist
        logging.error(f"Book with ID {book_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found."
        )

    except SQLAlchemyError as sql_error:
        # Handle any database related issues like SQL conflicts
        logging.error(f"SQL error occurred while deleting the book: {str(sql_error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while trying to delete the book."
        )

    except Exception as e:
        # Catch other unexpected errors
        logging.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )


@router.get("/api/bookstore/count/{book_id}", response_model=schemas.ApiResponse, status_code=status.HTTP_200_OK)
async def get_book_count(book_id: int, db: Session = Depends(get_db)):
    try:
        logging.info(f"Received book_id: {book_id}")
        book = db.query(models.Book).filter(models.Book.id == book_id).first()

        if not book:
            logging.info(f"Book with ID {book_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} not found."
            )

        # Log book details for debugging
        logging.info(f"Book ID: {book.id}")
        logging.info(f"Book Title: {book.title}")
        logging.info(f"Book Author: {book.author}")
        logging.info(f"Book Category: {book.category}")
        logging.info(f"Book TotalCount: {book.totalCount}")

        # Create a list with a single BookResponse
        book_data = schemas.BookResponse(
            id=book.id,
            title=book.title,
            author=book.author,
            category=book.category,
            price=book.price,
            totalCount=book.totalCount,
            sold=book.sold
        )

        # Create the ApiResponse
        response = schemas.ApiResponse(
            status="success",
            message=f"Book with ID {book_id} has been successfully counted.",
            data=[book_data],  # Wrap the book_data in a list
            timestamp=datetime.utcnow().isoformat(),
            errors=None
        )

        logging.info(f"Book with ID {book_id} counted successfully.")
        return response

    except HTTPException as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        raise http_err  # Return specific HTTP exceptions (e.g., 404 Not Found)

    except ValueError:
        # Bad request due to incorrect parameter type (400)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input, book ID must be an integer"
        )

    except SQLAlchemyError as sql_err:
        # Database-specific errors (500)
        logging.error(f"SQL error occurred: {str(sql_err)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while retrieving book count"
        )

    except Exception as e:
        # Catch-all for unexpected errors (500)
        logging.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )






app.include_router(router)










