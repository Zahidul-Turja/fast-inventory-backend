import re
import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Float,
    Enum,
    Boolean,
    ForeignKey,
    Text,
    event,
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session

from app.database import Base


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from product name"""
    slug = name.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[-\s]+", "-", slug)
    slug = slug.strip("-")
    return slug


class ProductStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    out_of_stock = "out_of_stock"
    discontinued = "discontinued"


class ProductCategory(enum.Enum):
    electronics = "electronics"
    clothing = "clothing"
    food = "food"
    furniture = "furniture"
    books = "books"
    toys = "toys"
    sports = "sports"
    beauty = "beauty"
    automotive = "automotive"
    home_garden = "home_garden"
    other = "other"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    # Pricing
    price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=True)  # For profit calculations
    discount_price = Column(Float, nullable=True)

    # Inventory
    sku = Column(String, unique=True, index=True, nullable=False)  # Stock Keeping Unit
    quantity = Column(Integer, nullable=False, default=0)
    min_stock_level = Column(Integer, nullable=True, default=10)  # For reorder alerts

    # Classification
    category = Column(Enum(ProductCategory), nullable=False)
    subcategory = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    tags = Column(String, nullable=True)  # Comma-separated tags

    # Media
    primary_image = Column(String, nullable=True)
    images = Column(String, nullable=True)  # JSON string of image URLs

    # Dimensions & Shipping
    weight = Column(Float, nullable=True)
    unit = Column(String, nullable=True, default="kg")
    dimensions = Column(
        String, nullable=True
    )  # JSON: {"length": x, "width": y, "height": z}

    # Status
    status = Column(Enum(ProductStatus), nullable=False, default=ProductStatus.active)
    is_featured = Column(Boolean, nullable=False, default=False)
    is_published = Column(Boolean, nullable=False, default=True)
    deleted = Column(Boolean, nullable=False, default=False)

    # Relationships
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    owner = relationship("User", backref="products", foreign_keys=[owner_id])

    # Timestamps
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def is_low_stock(self) -> bool:
        """Check if product is below minimum stock level"""
        return self.quantity <= self.min_stock_level

    @property
    def profit_margin(self) -> float:
        """Calculate profit margin percentage"""
        if self.cost_price and self.cost_price > 0:
            return ((self.price - self.cost_price) / self.cost_price) * 100
        return 0.0

    @property
    def effective_price(self) -> float:
        """Return discount price if available, otherwise regular price"""
        return self.discount_price if self.discount_price else self.price

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name}, sku={self.sku}, owner_id={self.owner_id})"


@event.listens_for(Product, "before_insert")
def generate_slug_before_insert(mapper, connection, target):
    if not target.slug and target.name:
        base_slug = generate_slug(target.name)
        slug = base_slug

        # Check for existing slugs and append number if needed
        counter = 1
        from sqlalchemy import select

        while True:
            result = connection.execute(
                select(Product.id).where(Product.slug == slug)
            ).first()

            if not result:
                break

            slug = f"{base_slug}-{counter}"
            counter += 1

        target.slug = slug
