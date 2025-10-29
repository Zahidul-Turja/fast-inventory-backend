from fastapi import APIRouter
from app.api.v1.endpoints import auth, user, product_api

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(product_api.router, prefix="/products", tags=["Products"])
