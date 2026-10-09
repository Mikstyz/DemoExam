from sqlmodel import Session, col, select

from model.stock_item import StockItem


class StockItemRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, stock_item: StockItem) -> StockItem:
        self.session.add(stock_item)
        self.session.flush()
        self.session.refresh(stock_item)
        return stock_item

    def get_by_id(self, stock_item_id: int) -> StockItem | None:
        return self.session.get(StockItem, stock_item_id)

    def get_by_product_and_size(
        self,
        product_id: int,
        size_id: int,
    ) -> StockItem | None:
        statement = select(StockItem).where(
            col(StockItem.product_id) == product_id,
            col(StockItem.size_id) == size_id,
        )
        return self.session.exec(statement).first()

    def get_by_product(self, product_id: int) -> list[StockItem]:
        statement = (
            select(StockItem)
            .where(col(StockItem.product_id) == product_id)
            .order_by(col(StockItem.size_id))
        )
        return list(self.session.exec(statement).all())

    def get_all(self) -> list[StockItem]:
        statement = select(StockItem).order_by(
            col(StockItem.stock_item_id)
        )
        return list(self.session.exec(statement).all())

    def update_quantity(
        self,
        stock_item_id: int,
        quantity: int,
    ) -> StockItem | None:
        if quantity < 0:
            raise ValueError("Количество товара не может быть отрицательным")

        stock_item = self.get_by_id(stock_item_id)

        if stock_item is None:
            return None

        stock_item.quantity_available = quantity
        self.session.add(stock_item)
        self.session.flush()
        self.session.refresh(stock_item)

        return stock_item

    def change_quantity(
        self,
        stock_item_id: int,
        amount: int,
    ) -> StockItem | None:
        stock_item = self.get_by_id(stock_item_id)

        if stock_item is None:
            return None

        new_quantity = stock_item.quantity_available + amount

        if new_quantity < 0:
            raise ValueError(
                "Недостаточно товара на складе"
            )

        stock_item.quantity_available = new_quantity
        self.session.add(stock_item)
        self.session.flush()
        self.session.refresh(stock_item)

        return stock_item

    def delete(self, stock_item_id: int) -> bool:
        stock_item = self.get_by_id(stock_item_id)

        if stock_item is None:
            return False

        self.session.delete(stock_item)
        self.session.flush()

        return True
