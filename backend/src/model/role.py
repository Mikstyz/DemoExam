from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import CheckConstraint, UniqueConstraint

import model

class Role(SQLModel, table=True):
    __tablename__ = "roles"

    role_id: int | None = Field(
        default=None,
        primary_key=True,
    )

    role_name: str = Field(
        nullable=False,
        unique=True,
        max_length=50,
    )

    users: list["model.user.User"] = Relationship(
        back_populates="role",
    )
