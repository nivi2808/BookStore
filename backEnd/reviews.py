import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.exc import SQLAlchemyError
from backEnd.database import get_db
from backEnd.models import Book, Review, User
from sqlalchemy.orm import Session
from backEnd.schemas import ReviewRequest, ReviewResponse
from backEnd.auth import get_current_user


router= APIRouter()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@router.post("/api/books/{book_id}/reviews", status_code=status.HTTP_200_OK)
async def add_review(
        book_id: int,
        review: ReviewRequest,

        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)):

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to add a review."
        )

    try:

        # Check if the book exists
        logger.debug(f"Checking for book with ID: {book_id}")
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            logger.debug(f"Book ID {book_id} not found in database.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} not found."
            )

        # Optional: Check if the user has already reviewed this book
        logger.debug(f"Current user ID: {current_user.id}")
        duplicate_review_check = (
            db.query(Review)
            .filter(Review.book_id == book_id, Review.user_id ==  current_user.id)
            .first()
        )
        if duplicate_review_check:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"You have already reviewed this book."
            )



        # Create a new review
        logger.debug(f"Creating review: rating={review.rating}, comment={review.comment}")
        new_review = Review(
            book_id=book_id,
            user_id=current_user.id,
            rating=review.rating,
            comment=review.comment,
            created_at=datetime.utcnow()
        )
        db.add(new_review)
        db.commit()
        db.refresh(new_review)

        # Build the response
        response = {
            "status": "OK",
            "message": "Review added successfully",
            "data": {
                "id": new_review.id,
                "rating": new_review.rating,
                "comment": new_review.comment,
                "userEmail": current_user.email,
                "createdAt": new_review.created_at.isoformat(),
            },
            "timestamp": datetime.utcnow().isoformat(),
            "errors": {}
        }
        return response



    except HTTPException as e:
        logger.error(f"HTTP error: {e.detail}")
        return {
            "status": "error",
            "message": e.detail,
            "data": {},
            "timestamp": datetime.utcnow().isoformat(),
            "errors": {
                "additionalProp1": "string",
                "additionalProp2": "string",
                "additionalProp3": "string"
            }
        }

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {e}", exc_info=True)
        return {
            "status": "error",
            "message": "A database error occurred.",
            "data": {},
            "timestamp": datetime.utcnow().isoformat(),
            "errors": {
                "additionalProp1": "Database error details",
                "additionalProp2": "Please contact support",
                "additionalProp3": str(e)
            }
        }

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "status": "error",
            "message": "An unexpected error occurred.",
            "data": {},
            "timestamp": datetime.utcnow().isoformat(),
            "errors": {
                "additionalProp1": "Unexpected error details",
                "additionalProp2": "Please contact support",
                "additionalProp3": str(e)
            }
        }
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {e}", exc_info=True)  # Include the full traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )

@router.get("/api/books/{book_id}/reviews", response_model = List[ReviewResponse],status_code=status.HTTP_200_OK)
async def get_book_reviews(
        book_id: int = Path(..., title="The ID of the book to retrieve reviews for", ge=1),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)):

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to retrieve reviews for this book."

        )

    try:
        reviews = db.query(Review).filter(Review.book_id == book_id).all()

        if not reviews:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "status": "error",
                    "message": "No reviews found for the specified book.",
                    "data": {},
                    "timestamp": datetime.utcnow().isoformat(),
                    "errors": {}
                }
            )
        reviews_data = [
            ReviewResponse(
            id=review.id,
            rating=review.rating,
            comment=review.comment,
            userEmail=review.user.email if review.user else "Unknown",
            createdAt=review.created_at
            )
            for review in reviews
        ]
        return reviews_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "An unexpected error occurred.",
                "data": {},
                "timestamp": datetime.utcnow().isoformat(),
                "errors": {"detail": str(e)}
            }
        )





