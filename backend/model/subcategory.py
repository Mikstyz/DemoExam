from typing import TYPE_CHECKING
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .category import Category
    from .product import Product


class Subcategory(SQLModel, table=True):
    __tablename__ = "subcategories"
    __table_args__ = (
        UniqueConstraint("category_id", "name", name="uq_subcategory_category_name"),
    )

    subcategory_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    category_id: int = Field(foreign_key="categories.category_id", index=True)

    category: "Category" = Relationship(back_populates="subcategories")
    products: list["Product"] = Relationship(back_populates="subcategory_ref")
