import logging
from fastapi import HTTPException, status, Depends, APIRouter
from sqlalchemy import cast, DateTime
from sqlalchemy.orm import Session
from datetime import datetime
from backEnd import models, schemas

from backEnd.database import engine, get_db
from backEnd.auth import get_current_user




# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI and router
# app = FastAPI()
router = APIRouter()

models.Base.metadata.create_all(bind=engine)

@router.post("/api/order", response_model=schemas.ApiResponseListOrder, status_code=status.HTTP_200_OK)
async def place_order(
    request: schemas.PlaceOrderRequest,  # Accept multiple book orders
    db: Session = Depends(get_db),
     current_user = Depends(get_current_user) ):
    try:
        logging.info("Placing an order")
        order_details = []
        total_amount = 0

        # Iterate over items in the order
        for item in request.items:
            # Fetch book and validate
            book = db.query(models.Book).filter(models.Book.id == item.book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail=f"Book ID {item.book_id} not found")
            if book.totalCount < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for Book ID {item.book_id}")

            # Process order
            total_price = book.price * item.quantity
            book.totalCount -= item.quantity
            book.sold += item.quantity
            db.add(book)

            order = models.Order(
                book_id=item.book_id,
                customer_id=current_user.id,
                quantity=item.quantity,
                total_price=total_price,
                order_date = cast(datetime.utcnow(), DateTime)
            )
            db.add(order)

            order_details.append({
                "book_id": item.book_id,
                "quantity": item.quantity,
                "total_price": total_price})
            total_amount += total_price

        db.commit()
        # Prepare the response
        response = schemas.ApiResponseListOrder(
            status="Success",
            message="Order placed successfully",
            data=[schemas.OrderDetail(**order) for order in order_details],
            timestamp=datetime.utcnow(),
            errors=[]
        )
        return response

    except HTTPException as e:
        db.rollback()
        logging.error(f"HTTPException occurred: {e.detail}")
        raise e
    except Exception as e:
        db.rollback()
        logging.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/api/orders", response_model=schemas.ApiResponseListOrder, status_code=status.HTTP_200_OK)
async def get_all_orders(db: Session = Depends(get_db),
                         current_user = Depends(get_current_user) ):
    try:
        logging.info("Get all orders")
        # Fetch orders for the current user
        orders = db.query(models.Order).filter(models.Order.customer_id == current_user.id).all()
        order_details = []
        total_amount = 0

        # Iterate over the orders and fetch the related book details
        for order in orders:
            book = db.query(models.Book).filter(models.Book.id == order.book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail=f"Book ID {order.book_id} not found")

            order_details.append({
                "book_id": order.book_id,
                "quantity": order.quantity,
                "total_price": order.total_price
            })
            total_amount += order.total_price

        # Construct the response data
        response_data = {
            "status": "Success",
            "message": "Order history fetched successfully",  # You can customize the message
            "data": order_details,
            "timestamp": datetime.utcnow(),
            "errors": []  # or any specific errors if necessary
        }

        return response_data

    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")