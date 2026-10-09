from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User
    from .order_item import OrderItem


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    order_id: int | None = Field(
        default=None,
        primary_key=True,
    )
    order_date: datetime = Field(
        default_factory=datetime.now,
        index=True,
    )
    user_id: int = Field(
        foreign_key="users.user_id",
        index=True,
    )

    user: "User" = Relationship(
        back_populates="orders",
    )
    order_items: list["OrderItem"] = Relationship(
        back_populates="order",
    )
