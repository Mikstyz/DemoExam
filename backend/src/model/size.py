from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import CheckConstraint, UniqueConstraint

import model

class Size(SQLModel, table=True):
    __tablename__ = "sizes"

    size_id: int | None = Field(
        default=None,
        primary_key=True,
    )

    size_value: str = Field(
        nullable=False,
        unique=True,
        max_length=50,
    )

    stock_items: list["model.stock_item.StockItem"] = Relationship(
        back_populates="size",
    )

    order_items: list["model.order_item.OrderItem"] = Relationship(
        back_populates="size",
    )
