from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import CheckConstraint, UniqueConstraint

import model

class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_order_item_quantity_positive",
        ),
        CheckConstraint(
            "price >= 0",
            name="ck_order_item_price_non_negative",
        ),
    )

    order_item_id: int | None = Field(
        default=None,
        primary_key=True,
    )

    order_id: int = Field(
        foreign_key="orders.order_id",
        nullable=False,
    )

    product_id: int = Field(
        foreign_key="products.product_id",
        nullable=False,
    )

    size_id: int = Field(
        foreign_key="sizes.size_id",
        nullable=False,
    )

    quantity: int = Field(
        nullable=False,
        gt=0,
    )

    price: float = Field(
        nullable=False,
        ge=0,
    )

    order: model.order.Order = Relationship(
        back_populates="order_items",
    )

    product: model.product.Product = Relationship(
        back_populates="order_items",
    )

    size: model.size.Size = Relationship(
        back_populates="order_items",
    )
