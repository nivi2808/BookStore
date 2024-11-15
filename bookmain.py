import logging
from http.client import responses
from lib2to3.fixes.fix_input import context
from pyexpat.errors import messages
from typing import Optional
from urllib.request import Request

from fastapi import FastAPI, HTTPException, status, Depends, Query, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from schemas import Category, ApiResponse, BookData, PlaceOrderRequest
# from schemas import ApiResponseOrder,
from schemas import ApiResponseBook, QuantityUpdateRequest, ApiResponseOrder
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


@router.get("/api/bookstore/sales", response_model=schemas.ApiResponseSold, status_code=status.HTTP_200_OK)
async def get_books_sold(
    title: Optional[str] = Query(None, description="Filter by book title", min_length=2),
    category: Optional[str] = Query(None, description="Filter by book category", min_length=2),
    db: Session = Depends(get_db),
    is_authenticated: bool = Depends(lambda: True)  # Mock authentication check
    ):
    try:
        logging.info("Retrieving sold books data.")

        # Check authentication
        if not is_authenticated:
            logging.error("Unauthorized access attempt.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized access."
            )

        # Build filters based on query parameters
        filters = []
        if title:
            filters.append(models.Book.title.ilike(f"%{title}%"))
        if category:
            filters.append(models.Book.category.ilike(f"%{category}%"))

        # Fetch data from the database
        books = db.query(models.Book).filter(*filters).all()

        if not books:
            logging.info(f"No books found matching the title '{title}' and category '{category}'.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No books found matching the search criteria."
            )

            # Prepare response data
        book_data = [
                schemas.SoldBookResponse(
                    title=book.title,
                    category=book.category,
                    sold=book.sold
                ) for book in books
            ]


        # Return success response
        response = schemas.ApiResponseSold(
            status="success",
            message="Books retrieved successfully.",
            data=book_data,
            timestamp=datetime.utcnow().isoformat(),
            errors=None
        )

        logging.info(f"Retrieved {len(book_data)} books.")
        return response

    except HTTPException as http_err:
        logging.error(f"HTTP error occurred: {http_err.detail}")
        raise http_err

    except SQLAlchemyError as sql_err:
        logging.error(f"Database error occurred: {str(sql_err)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while retrieving sales data."
        )

    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the request."
        )


@router.get("/api/bookstore/books", response_model=schemas.ApiResponseListBook, status_code=status.HTTP_200_OK)
async def get_all_books(
        db: Session = Depends(get_db),
        is_authenticated: bool = Depends(lambda: True)
):
    try:
        logging.info("Retrieving all books from bookstore.")

        # Check for authentication
        if not is_authenticated:
            logging.error("Unauthorized access attempt.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized access."
            )

        # Fetch books from the database
        books = db.query(models.Book).all()

        if not books:
            logging.info("No books found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No books found"
            )

        # Prepare the book data list
        book_data = [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
            }
            for book in books
        ]

        # Prepare the response
        response = schemas.ApiResponseBook(
            status="success",
            message="Books retrieved successfully.",
            data=book_data,
            timestamp=datetime.utcnow().isoformat(),
            errors=None
        )
        return response

    except HTTPException as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        raise http_err

    except ValueError as value_err:
        logging.error(f"Value error occurred: {value_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input, book ID must be an integer"
        )

    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.put("/api/bookstore/books/{book_id}", response_model=schemas.ApiResponse, status_code=status.HTTP_200_OK)
async def update_book(
        book_id: int,
        updated_book: schemas.BookResponse,
        db: Session = Depends(get_db),
        is_authenticated: bool = Depends(lambda: True)
):

    try:
        logging.info("Updating book data.")
        if not is_authenticated:
            logging.error("Unauthorized access attempt.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized access."
            )

        # Find the book to update in the database
        book = db.query(models.Book).filter(models.Book.id == book_id).first()

        if not book:
            logging.info(f"Book with ID {book_id} does not exist.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} does not exist."

            )

            # Update the book details with the new data
        book.title = updated_book.title
        book.author = updated_book.author
        book.category = updated_book.category
        book.price = updated_book.price
        book.totalCount = updated_book.totalCount
        book.sold = updated_book.sold

        db.commit()

        updated_book_data = {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "category": book.category,
            "price": book.price,
            "totalCount": book.totalCount,
            "sold": book.sold

        }

        response = schemas.ApiResponseBook(
            status="success",
            message="Book updated successfully.",
            data=[updated_book_data],
            timestamp=datetime.utcnow().isoformat(),
            errors=None

        )

        return response

    except HTTPException as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        raise http_err

    except ValueError as value_err:
        logging.error(f"Value error occurred: {value_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input, book ID must be an integer"

        )
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.put("/api/bookstore/books/{book_id}/increase-quantity", response_model=schemas.ApiResponseBook, status_code=status.HTTP_200_OK)
async def increase_book_quantity(
    book_id: int,
    quantity_update: schemas.QuantityUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Increases the quantity of a book by the specified amount.

    Args:
        book_id (int): ID of the book to update.
        quantity_update (schemas.QuantityUpdateRequest): Request body containing the quantity to add.

    Returns:
        schemas.ApiResponseBook: Structured API response containing the updated book data.
    """
    try:
        # Log the request
        logging.info(f"Received request to increase quantity for book ID {book_id} by {quantity_update.quantity}")

        # Validate the quantity input
        if quantity_update.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than zero."
            )

        # Retrieve the book from the database
        book = db.query(models.Book).filter(models.Book.id == book_id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} does not exist."
            )

        # Update the book's quantity
        book.totalCount += quantity_update.quantity
        db.commit()
        db.refresh(book)  # Refresh the instance to reflect the updated state

        # Prepare the response
        updated_book = schemas.BookResponse(
            id=book.id,
            title=book.title,
            author=book.author,
            category=book.category,
            price=book.price,
            totalCount=book.totalCount,
            sold=book.sold
        )

        return schemas.ApiResponseBook(
            status="success",
            message="Book quantity updated successfully.",
            data=updated_book,
            timestamp=datetime.utcnow().isoformat(),
            errors=None
        )

    except HTTPException as e:
        # Log and re-raise HTTP exceptions
        logging.error(f"HTTP exception: {e.detail}")
        raise e
    except Exception as e:
        # Handle unexpected errors
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )

@router.put("/api/bookstore/orders", response_model=schemas.ApiResponseListOrder, status_code=status.HTTP_201_CREATED)
async def place_order(
        request: PlaceOrderRequest,
        db: Session = Depends(get_db),
        is_authenticated: bool = Depends(lambda: True)
):
    try:
        logging.info(f"Received request to place order")
        if not is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        order_details = []

        for order in request.orders:
            # Fetch the book details
            book = db.query(models.Book).filter(models.Book.id == order.book_id).first()
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Book with ID {order.book_id} does not exist."
                )
            # Check stock availability
            if book.totalCount < order.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for book ID {order.book_id}. Available: {book.totalCount}"
                )

            # Update stock and sold count
            book.totalCount -= order.quantity
            book.sold += order.quantity
            db.add(book)
            db.flush()

            # Add this book's details to the order
            order_details.append({
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "category": book.category,
                "price": book.price,
                "total_price": book.price * order.quantity
            })

        # Commit the transaction
        db.commit()

        # Calculate total amount for the entire order
        total_amount = sum(item["total_price"] for item in order_details)

        # Prepare the response
        response = schemas.ApiResponseListOrder(
            status="success",
            message="Order placed successfully.",
            data={
                "order_details": order_details,
                "total_amount": total_amount,
                "order_timestamp": datetime.utcnow().isoformat()
            },
            timestamp=datetime.utcnow().isoformat(),
            errors=[]
        )

        return response

    except HTTPException as e:
        logging.error(f"HTTP exception: {e.detail}")
        raise e

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/api/bookstore/order/{book_id}", response_model=schemas.ApiResponseListOrder,
            status_code=status.HTTP_200_OK)
async def place_order(
        book_id: int,  # book_id is passed as a path parameter
        request: schemas.Order,  # The request body only contains quantity
        db: Session = Depends(get_db),
        is_authenticated: bool = Depends(lambda: True)  # Assuming authentication logic here
):
    try:
        logging.info(f"Received request to place order for book ID {book_id}")

        # Check if the user is authenticated
        if not is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        # Query the book by the provided book_id
        book = db.query(models.Book).filter(models.Book.id == book_id).first()

        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} does not exist."
            )

        # Get the quantity from the request body
        quantity = request.quantity

        # Check if sufficient stock is available
        if book.totalCount < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for book ID {book_id}. Available: {book.totalCount}"
            )

        # Update the stock and sold count
        book.totalCount -= quantity
        book.sold += quantity
        db.add(book)
        db.flush()

        # Prepare the order details
        order_details = [{
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "category": book.category,
            "price": book.price,
            "total_price": book.price * quantity
        }]

        # Calculate the total amount for the order
        total_amount = sum(item["total_price"] for item in order_details)

        # Prepare the response data
        response = schemas.ApiResponseListOrder(
            status="success",
            message="Order placed successfully.",
            data={
                "order_details": order_details,
                "total_amount": total_amount,
                "order_timestamp": datetime.utcnow().isoformat()
            },
            timestamp=datetime.utcnow().isoformat(),
            errors=[]
        )

        # Commit the transaction to the database
        db.commit()

        # Return the response
        return response

    except HTTPException as e:
        logging.error(f"HTTP exception: {e.detail}")
        raise e

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
















app.include_router(router)










