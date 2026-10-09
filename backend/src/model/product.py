from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Numeric
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .stock_item import StockItem
    from .order_item import OrderItem


class Product(SQLModel, table=True):
    __tablename__ = "products"

    product_id: int | None = Field(
        default=None,
        primary_key=True,
    )
    category: str = Field(
        max_length=100,
        index=True,
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
        max_length=200,
        index=True,
    )
    manufacturer: str = Field(max_length=150)
    description: str | None = Field(
        default=None,
        max_length=2000,
    )
    composition: str | None = Field(
        default=None,
        max_length=1000,
    )
    price: Decimal = Field(
        sa_type=Numeric(10, 2),
        gt=0,
    )

    stock_items: list["StockItem"] = Relationship(
        back_populates="product",
    )
    order_items: list["OrderItem"] = Relationship(
        back_populates="product",
    )
