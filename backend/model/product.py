from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import CheckConstraint, Numeric
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .stock_item import StockItem
    from .order_item import OrderItem
    from .subcategory import Subcategory
    from .category import Category


class Product(SQLModel, table=True):
    __tablename__ = "products"
    __table_args__ = (CheckConstraint("price > 0", name="ck_product_price_positive"),)

    product_id: int | None = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="categories.category_id", index=True)
    subcategory_id: int | None = Field(
        default=None, foreign_key="subcategories.subcategory_id", index=True
    )
    image_path: str | None = Field(default=None, max_length=500)
    product_name: str = Field(max_length=200, index=True)
    manufacturer: str = Field(max_length=150)
    description: str | None = Field(default=None, max_length=2000)
    composition: str | None = Field(default=None, max_length=1000)
    price: Decimal = Field(sa_type=Numeric(10, 2), gt=0)

    category_ref: "Category" = Relationship(back_populates="products")
    subcategory_ref: "Subcategory" = Relationship(back_populates="products")
    stock_items: list["StockItem"] = Relationship(back_populates="product")
    order_items: list["OrderItem"] = Relationship(back_populates="product")
