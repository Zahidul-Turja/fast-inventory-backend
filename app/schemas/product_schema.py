from pydantic import BaseModel, field_validator
import json
from app.models.product_model import Product


class ProductSchema(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    price: float
    cost_price: float | None
    discount_price: float | None
    primary_image: str | None
    images: list[str] | None
    sku: str
    quantity: int
    min_stock_level: int
    category: str
    subcategory: str | None
    brand: str | None
    tags: str | None
    weight: float | None
    unit: str | None
    dimensions: str | None

    class Config:
        from_attributes = True

    @field_validator("images", mode="before")
    def parse_images(cls, v):
        if not v:
            return None
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [i.strip() for i in v.split(",") if i.strip()]
        return v

    def to_dict_with_absolute_url(self, request):
        data = self.model_dump()
        base_url = str(request.base_url).rstrip("/")

        if self.primary_image and not self.primary_image.startswith("http"):
            data["primary_image"] = f"{base_url}{self.primary_image}"

        if self.images:
            data["images"] = [
                f"{base_url}{img}" if not img.startswith("http") else img
                for img in self.images
            ]

        return data
