from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Numeric
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .order import Order
    from .product import Product
    from .size import Size


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_order_item_quantity_positive",
        ),
        CheckConstraint(
            "price >= 0",
            name="ck_order_item_price_nonnegative",
        ),
    )

    order_item_id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.order_id", index=True)
    product_id: int = Field(foreign_key="products.product_id", index=True)
    size_id: int = Field(foreign_key="sizes.size_id", index=True)
    quantity: int = Field(gt=0)
    price: Decimal = Field(sa_type=Numeric(10, 2), ge=0)

    order: "Order" = Relationship(back_populates="order_items")
    product: "Product" = Relationship(back_populates="order_items")
    size: "Size" = Relationship(back_populates="order_items")
