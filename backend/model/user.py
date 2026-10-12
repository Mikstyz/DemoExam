from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .role import Role
    from .order import Order


class User(SQLModel, table=True):
    __tablename__ = "users"

    user_id: int | None = Field(default=None, primary_key=True)
    last_name: str = Field(max_length=100)
    first_name: str = Field(max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    login: str = Field(max_length=100, unique=True, index=True)
    role_id: int = Field(foreign_key="roles.role_id", index=True)

    role: "Role" = Relationship(back_populates="users")
    orders: list["Order"] = Relationship(back_populates="user")
