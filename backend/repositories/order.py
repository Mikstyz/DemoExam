from datetime import datetime

from sqlmodel import Session, select

from model import Order


class OrderRepository:
    """CRUD-операции и выборки таблицы orders."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, order_id: int) -> Order | None:
        return self.session.get(Order, order_id)

    def get_by_user_id(self, user_id: int) -> list[Order]:
        statement = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.order_date.desc(), Order.order_id.desc())
        )
        return list(self.session.exec(statement).all())

    def get_all(self) -> list[Order]:
        statement = select(Order).order_by(
            Order.order_date.desc(), Order.order_id.desc()
        )
        return list(self.session.exec(statement).all())

    def get_by_date_range(
        self,
        start: datetime,
        end: datetime,
    ) -> list[Order]:
        statement = (
            select(Order)
            .where(Order.order_date >= start, Order.order_date <= end)
            .order_by(Order.order_date.desc())
        )
        return list(self.session.exec(statement).all())

    def create(self, order: Order) -> Order:
        self.session.add(order)
        self.session.flush()
        self.session.refresh(order)
        return order

    def update(self, order: Order) -> Order:
        self.session.add(order)
        self.session.flush()
        self.session.refresh(order)
        return order

    def delete(self, order: Order) -> None:
        self.session.delete(order)
        self.session.flush()
