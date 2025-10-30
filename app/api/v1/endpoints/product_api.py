import os
from uuid import uuid4

from fastapi import APIRouter, Depends, status, Form, File, UploadFile, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.product_model import Product
from app.utilities.auth import get_current_user
from app.models.user_model import User
from app.schemas.product_schema import ProductSchema

PRODUCT_IMAGE_DIR = "app/static/product_images"

router = APIRouter()


@router.post("/")
async def create_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    cost_price: float = Form(None),
    discount_price: float = Form(None),
    primary_image: UploadFile = File(None),
    images: list[UploadFile] = File([]),
    sku: str = Form(...),
    quantity: int = Form(...),
    min_stock_level: int = Form(...),
    category: str = Form(...),
    subcategory: str = Form(None),
    brand: str = Form(None),
    tags: str = Form(None),
    weight: float = Form(None),
    unit: str = Form(None),
    dimensions: str = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    os.makedirs(PRODUCT_IMAGE_DIR, exist_ok=True)

    primary_image_path = None
    if primary_image:
        ext = primary_image.filename.split(".")[-1]
        filename = f"{uuid4()}.{ext}"
        file_path = os.path.join(PRODUCT_IMAGE_DIR, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await primary_image.read())

        primary_image_path = f"/static/product_images/{filename}"

    image_urls = []
    for image in images:
        if image.filename == "":
            continue
        ext = image.filename.split(".")[-1]
        filename = f"{uuid4()}.{ext}"
        file_path = os.path.join(PRODUCT_IMAGE_DIR, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())

        image_urls.append(f"/static/product_images/{filename}")

    product = Product(
        name=name,
        description=description,
        price=price,
        cost_price=cost_price,
        discount_price=discount_price,
        sku=sku,
        quantity=quantity,
        min_stock_level=min_stock_level,
        category=category,
        subcategory=subcategory,
        brand=brand,
        tags=tags,
        weight=weight,
        unit=unit,
        dimensions=dimensions,
        primary_image=primary_image_path,
        images=",".join(image_urls),
        owner_id=user.id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    base_url = str(request.base_url).rstrip("/")
    full_primary = (
        f"{base_url}{product.primary_image}" if product.primary_image else None
    )
    full_images = [f"{base_url}{url}" for url in image_urls]

    return {
        "message": "Product created successfully",
        "data": {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "price": product.price,
            "primary_image": full_primary,
            "images": full_images,
        },
    }


@router.get("/{product_slug}")
async def get_product(
    product_slug: str,
    request: Request,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.slug == product_slug).first()
    if not product:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Product not found"},
        )
    product_res = ProductSchema.model_validate(product, from_attributes=True)

    return {
        "message": "Product retrieved successfully",
        "data": product_res.to_dict_with_absolute_url(request),
    }

    base_url = str(request.base_url).rstrip("/")
    full_primary = (
        f"{base_url}{product.primary_image}" if product.primary_image else None
    )
    image_urls = []
    if product.images:
        for img in product.images.split(","):
            image_urls.append(f"{base_url}{img}")

    return {
        "message": "Product retrieved successfully",
        "data": {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "description": product.description,
            "price": product.price,
            "cost_price": product.cost_price,
            "discount_price": product.discount_price,
            "primary_image": full_primary,
            "images": image_urls,
            "sku": product.sku,
            "quantity": product.quantity,
            "min_stock_level": product.min_stock_level,
            "category": product.category,
            "subcategory": product.subcategory,
            "brand": product.brand,
            "tags": product.tags,
            "weight": product.weight,
            "unit": product.unit,
            "dimensions": product.dimensions,
        },
    }
