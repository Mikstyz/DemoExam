from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import CheckConstraint, UniqueConstraint

import model

class Product(SQLModel, table=True):
    __tablename__ = "products"

    product_id: int | None = Field(
        default=None,
        primary_key=True,
    )

    category: str = Field(
        nullable=False,
        max_length=100,
    )

    subcategory: str | None = Field(
        default=None,
        max_length=100,
    )

    image_path: str | None = Field(
        default=None,
        max_length=500,
    )

    product_name: str = Field(
        nullable=False,
        max_length=255,
    )

    manufacturer: str = Field(
        nullable=False,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
    )

    composition: str | None = Field(
        default=None,
    )

    price: float = Field(
        nullable=False,
        ge=0,
    )

    stock_items: list["model.stock_item.StockItem"] = Relationship(
        back_populates="product",
    )

    order_items: list["model.order_item.OrderItem"] = Relationship(
        back_populates="product",
    )
