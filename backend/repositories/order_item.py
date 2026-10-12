from sqlmodel import Session, select

from model import OrderItem


class OrderItemRepository:
    """CRUD-операции с таблицей order_items."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, order_item_id: int) -> OrderItem | None:
        return self.session.get(OrderItem, order_item_id)

    def get_by_order_id(self, order_id: int) -> list[OrderItem]:
        statement = (
            select(OrderItem)
            .where(OrderItem.order_id == order_id)
            .order_by(OrderItem.order_item_id)
        )
        return list(self.session.exec(statement).all())

    def get_by_product_id(self, product_id: int) -> list[OrderItem]:
        statement = (
            select(OrderItem)
            .where(OrderItem.product_id == product_id)
            .order_by(OrderItem.order_id)
        )
        return list(self.session.exec(statement).all())

    def get_all(self) -> list[OrderItem]:
        statement = select(OrderItem).order_by(OrderItem.order_item_id)
        return list(self.session.exec(statement).all())

    def create(self, order_item: OrderItem) -> OrderItem:
        self.session.add(order_item)
        self.session.flush()
        self.session.refresh(order_item)
        return order_item

    def update(self, order_item: OrderItem) -> OrderItem:
        self.session.add(order_item)
        self.session.flush()
        self.session.refresh(order_item)
        return order_item

    def delete(self, order_item: OrderItem) -> None:
        self.session.delete(order_item)
        self.session.flush()
