from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .subcategory import Subcategory
    from .product import Product


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    category_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, index=True)

    subcategories: list["Subcategory"] = Relationship(back_populates="category")
    products: list["Product"] = Relationship(back_populates="category_ref")
