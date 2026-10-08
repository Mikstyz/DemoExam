from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import CheckConstraint, UniqueConstraint

import model

class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: int | None = Field(
        default=None,
        primary_key=True,
    )

    last_name: str = Field(
        nullable=False,
        max_length=100,
    )

    first_name: str = Field(
        nullable=False,
        max_length=100,
    )

    middle_name: str | None = Field(
        default=None,
        max_length=100,
    )

    login: str = Field(
        nullable=False,
        unique=True,
        max_length=100,
    )

    role_id: int = Field(
        foreign_key="roles.role_id",
        nullable=False,
    )

    role: model.role.Role = Relationship(
        back_populates="users",
    )

    orders: list["model.order.Order"] = Relationship(
        back_populates="user",
    )
