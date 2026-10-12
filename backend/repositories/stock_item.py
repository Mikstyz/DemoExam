from sqlmodel import Session, select

from model import StockItem


class StockItemRepository:
    """CRUD-операции с таблицей stock_items."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, stock_item_id: int) -> StockItem | None:
        return self.session.get(StockItem, stock_item_id)

    def get_by_product_and_size(
        self,
        product_id: int,
        size_id: int,
    ) -> StockItem | None:
        statement = select(StockItem).where(
            StockItem.product_id == product_id,
            StockItem.size_id == size_id,
        )
        return self.session.exec(statement).first()

    def get_by_product_id(self, product_id: int) -> list[StockItem]:
        statement = (
            select(StockItem)
            .where(StockItem.product_id == product_id)
            .order_by(StockItem.size_id)
        )
        return list(self.session.exec(statement).all())

    def get_by_size_id(self, size_id: int) -> list[StockItem]:
        statement = (
            select(StockItem)
            .where(StockItem.size_id == size_id)
            .order_by(StockItem.product_id)
        )
        return list(self.session.exec(statement).all())

    def get_all(self) -> list[StockItem]:
        statement = select(StockItem).order_by(StockItem.product_id, StockItem.size_id)
        return list(self.session.exec(statement).all())

    def create(self, stock_item: StockItem) -> StockItem:
        self.session.add(stock_item)
        self.session.flush()
        self.session.refresh(stock_item)
        return stock_item

    def update(self, stock_item: StockItem) -> StockItem:
        self.session.add(stock_item)
        self.session.flush()
        self.session.refresh(stock_item)
        return stock_item

    def delete(self, stock_item: StockItem) -> None:
        self.session.delete(stock_item)
        self.session.flush()
