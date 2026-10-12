from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .product import Product
    from .size import Size


class StockItem(SQLModel, table=True):
    __tablename__ = "stock_items"
    __table_args__ = (
        UniqueConstraint("product_id", "size_id", name="uq_stock_product_size"),
        CheckConstraint(
            "quantity_available >= 0",
            name="ck_stock_quantity_nonnegative",
        ),
    )

    stock_item_id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.product_id", index=True)
    size_id: int = Field(foreign_key="sizes.size_id", index=True)
    quantity_available: int = Field(default=0, ge=0)

    product: "Product" = Relationship(back_populates="stock_items")
    size: "Size" = Relationship(back_populates="stock_items")
