from decimal import Decimal

from sqlmodel import Session, col, select

from model.order_item import OrderItem


class OrderItemRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, order_item: OrderItem) -> OrderItem:
        self.session.add(order_item)
        self.session.flush()
        self.session.refresh(order_item)
        return order_item

    def get_by_id(self, order_item_id: int) -> OrderItem | None:
        return self.session.get(OrderItem, order_item_id)

    def get_by_order(self, order_id: int) -> list[OrderItem]:
        statement = (
            select(OrderItem)
            .where(col(OrderItem.order_id) == order_id)
            .order_by(col(OrderItem.order_item_id))
        )
        return list(self.session.exec(statement).all())

    def get_by_product(self, product_id: int) -> list[OrderItem]:
        statement = (
            select(OrderItem)
            .where(col(OrderItem.product_id) == product_id)
            .order_by(col(OrderItem.order_item_id))
        )
        return list(self.session.exec(statement).all())

    def update_quantity(
        self,
        order_item_id: int,
        quantity: int,
    ) -> OrderItem | None:
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")

        order_item = self.get_by_id(order_item_id)

        if order_item is None:
            return None

        order_item.quantity = quantity
        self.session.add(order_item)
        self.session.flush()
        self.session.refresh(order_item)

        return order_item

    def update_price(
        self,
        order_item_id: int,
        price: Decimal,
    ) -> OrderItem | None:
        if price < 0:
            raise ValueError("Цена не может быть отрицательной")

        order_item = self.get_by_id(order_item_id)

        if order_item is None:
            return None

        order_item.price = price
        self.session.add(order_item)
        self.session.flush()
        self.session.refresh(order_item)

        return order_item

    def delete(self, order_item_id: int) -> bool:
        order_item = self.get_by_id(order_item_id)

        if order_item is None:
            return False

        self.session.delete(order_item)
        self.session.flush()

        return True
