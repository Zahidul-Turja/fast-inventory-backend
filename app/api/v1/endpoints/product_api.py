import os
from uuid import uuid4

from fastapi import APIRouter, Depends, status, Form, File, UploadFile, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.product_model import Product
from app.utilities.auth import get_current_user
from app.models.user_model import User
from app.schemas.product_schema import ProductSchema
from fastapi_pagination import Page, paginate

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

    product_schema = ProductSchema.model_validate(product, from_attributes=True)

    return {
        "message": "Product created successfully",
        "data": product_schema.to_dict_with_absolute_url(request),
    }


@router.get("/", response_model=Page[ProductSchema])
async def list_products(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    products = db.query(Product).filter(Product.owner_id == user.id).all()
    product_schemas = [
        ProductSchema.model_validate(
            product, from_attributes=True
        ).to_dict_with_absolute_url(request)
        for product in products
    ]
    response = {
        "message": "Products retrieved successfully",
        "data": paginate(product_schemas),
    }
    return JSONResponse(
        content=jsonable_encoder(response), status_code=status.HTTP_200_OK
    )


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


@router.get("/public/list", response_model=Page[ProductSchema])
async def list_public_products(
    request: Request,
    db: Session = Depends(get_db),
):
    products = db.query(Product).filter(Product.is_published == True).all()
    product_schemas = [
        ProductSchema.model_validate(
            product, from_attributes=True
        ).to_dict_with_absolute_url(request)
        for product in products
    ]
    response = {
        "message": "Products retrieved successfully",
        "data": paginate(product_schemas),
    }
    return JSONResponse(
        content=jsonable_encoder(response), status_code=status.HTTP_200_OK
    )


@router.put("/{product_slug}")
async def update_product(
    product_slug: str,
    request: Request,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    cost_price: float = Form(None),
    discount_price: float = Form(None),
    primary_image: UploadFile = File(None),
    images: list[UploadFile] = File([]),
    sku: str = Form(None),
    quantity: int = Form(None),
    min_stock_level: int = Form(None),
    category: str = Form(None),
    subcategory: str = Form(None),
    brand: str = Form(None),
    tags: str = Form(None),
    weight: float = Form(None),
    unit: str = Form(None),
    dimensions: str = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.slug == product_slug).first()
    if not product:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Product not found"},
        )

    if product.owner_id != user.id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "You are not authorized to update this product"},
        )

    # Update fields if provided
    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if price is not None:
        product.price = price
    if cost_price is not None:
        product.cost_price = cost_price
    if discount_price is not None:
        product.discount_price = discount_price
    if sku is not None:
        product.sku = sku
    if quantity is not None:
        product.quantity = quantity
    if min_stock_level is not None:
        product.min_stock_level = min_stock_level
    if category is not None:
        product.category = category
    if subcategory is not None:
        product.subcategory = subcategory
    if brand is not None:
        product.brand = brand
    if tags is not None:
        product.tags = tags
    if weight is not None:
        product.weight = weight
    if unit is not None:
        product.unit = unit
    if dimensions is not None:
        product.dimensions = dimensions

    # Handle images
    if primary_image:
        os.makedirs(PRODUCT_IMAGE_DIR, exist_ok=True)
        ext = primary_image.filename.split(".")[-1]
        filename = f"{uuid4()}.{ext}"
        file_path = os.path.join(PRODUCT_IMAGE_DIR, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await primary_image.read())
        product.primary_image = f"/static/product_images/{filename}"

    if images:
        os.makedirs(PRODUCT_IMAGE_DIR, exist_ok=True)
        new_image_urls = []
        for image in images:
            if image.filename == "":
                continue
            ext = image.filename.split(".")[-1]
            filename = f"{uuid4()}.{ext}"
            file_path = os.path.join(PRODUCT_IMAGE_DIR, filename)
            with open(file_path, "wb") as buffer:
                buffer.write(await image.read())
            new_image_urls.append(f"/static/product_images/{filename}")

        if new_image_urls:
            # Append or replace? Let's append for now, or maybe replace if user sends new ones.
            # Usually PUT replaces. But handling list of files is tricky.
            # Let's assume if images are sent, we append them to existing list?
            # Or maybe we should have a way to delete images.
            # For simplicity, let's just append new ones to the list.
            current_images = product.images.split(",") if product.images else []
            current_images.extend(new_image_urls)
            product.images = ",".join(current_images)

    db.commit()
    db.refresh(product)

    product_schema = ProductSchema.model_validate(product, from_attributes=True)

    return {
        "message": "Product updated successfully",
        "data": product_schema.to_dict_with_absolute_url(request),
    }


@router.delete("/{product_slug}")
async def delete_product(
    product_slug: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.slug == product_slug).first()
    if not product:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Product not found"},
        )

    if product.owner_id != user.id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "You are not authorized to delete this product"},
        )

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}
