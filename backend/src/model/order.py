from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import CheckConstraint, UniqueConstraint

import model

class Order(SQLModel, table=True):
    __tablename__ = "orders"

    order_id: int | None = Field(
        default=None,
        primary_key=True,
    )

    order_date: datetime = Field(
        nullable=False,
    )

    user_id: int = Field(
        foreign_key="users.user_id",
        nullable=False,
    )

    user: model.user.User = Relationship(
        back_populates="orders",
    )

    order_items: list["model.order_item.OrderItem"] = Relationship(
        back_populates="order",
    )
