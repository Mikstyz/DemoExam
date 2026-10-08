from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import CheckConstraint, UniqueConstraint

import model

class StockItem(SQLModel, table=True):
    __tablename__ = "stock_items"

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "size_id",
            name="uq_stock_product_size",
        ),
        CheckConstraint(
            "quantity_available >= 0",
            name="ck_stock_quantity_non_negative",
        ),
    )

    stock_item_id: int | None = Field(
        default=None,
        primary_key=True,
    )

    product_id: int = Field(
        foreign_key="products.product_id",
        nullable=False,
    )

    size_id: int = Field(
        foreign_key="sizes.size_id",
        nullable=False,
    )

    quantity_available: int = Field(
        default=0,
        nullable=False,
        ge=0,
    )

    product: model.product.Product = Relationship(
        back_populates="stock_items",
    )

    size: model.size.Size = Relationship(
        back_populates="stock_items",
    )
