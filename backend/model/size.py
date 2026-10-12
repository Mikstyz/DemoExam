from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .stock_item import StockItem
    from .order_item import OrderItem


class Size(SQLModel, table=True):
    __tablename__ = "sizes"

    size_id: int | None = Field(default=None, primary_key=True)
    size_value: str = Field(max_length=50, unique=True, index=True)

    stock_items: list["StockItem"] = Relationship(back_populates="size")
    order_items: list["OrderItem"] = Relationship(back_populates="size")
