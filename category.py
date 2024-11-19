import logging
from datetime import datetime
from typing import List
from fastapi import FastAPI, APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import CategoryResponse, CategoryEnum, ApiResponseListCategory
import models, schemas


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router= APIRouter()

@router.get("/api/categories", response_model=schemas.ApiResponseListCategory, status_code=status.HTTP_200_OK)
async def get_all_categories():
    try:

        logger.info("Fetching categories")# Return a list of CategoryResponse instances, ensuring it is structured correctly
        categories = [category.value for category in CategoryEnum]
        # categories = [CategoryResponse(category=category) for category in CategoryEnum]

        return {
            "status": "success",
            "message": "Categories retrieved successfully.",
            "data": categories,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException as e:
        logging.info(e)
        # Handle specific HTTP exceptions
        raise e

    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )



@router.get("/api/categories/{category}/books",response_model=List[schemas.BookResponse], status_code=status.HTTP_200_OK)
async def get_books_by_category(category: CategoryEnum, db: Session = Depends(get_db)):

    try:
        """
           Fetch books based on the category.
           """

        # Query books based on the category
        books = db.query(models.Book).filter(models.Book.category == category.value).all()

        # If no books are found, raise a 404 error
        if not books:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"No books found for category: {category.value}")

        # Return the books in the response
        return books

    except HTTPException as e:
        logging.info(e)
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An unexpected error occurred: {str(e)}"
                            )

















