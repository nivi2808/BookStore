import logging

from fastapi import FastAPI
from auth import router as auth_router
from orders import router as orders_router
from bookstore import router as bookstore_router
from category import router as category_router
from reviews import router as reviews_router

app = FastAPI()

# Include the routers in main.py
app.include_router(auth_router)  # Include auth router here
app.include_router(bookstore_router)
app.include_router(orders_router)
app.include_router(category_router)
app.include_router(reviews_router)


# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set the logging level to DEBUG
logger = logging.getLogger(__name__)  # Use the correct logger


@app.on_event("startup")
async def startup():
    for route in app.routes:
        logging.debug(f"Registered route: {route.path} method: {route.methods}")
