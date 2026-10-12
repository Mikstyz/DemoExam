from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


class Role(SQLModel, table=True):
    __tablename__ = "roles"

    role_id: int | None = Field(default=None, primary_key=True)
    role_name: str = Field(max_length=50, unique=True, index=True)

    users: list["User"] = Relationship(back_populates="role")
