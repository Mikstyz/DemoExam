from datetime import datetime

from sqlmodel import Session, col, select

from model.order import Order


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, order: Order) -> Order:
        self.session.add(order)
        self.session.flush()
        self.session.refresh(order)
        return order

    def get_by_id(self, order_id: int) -> Order | None:
        return self.session.get(Order, order_id)

    def get_all(self) -> list[Order]:
        statement = select(Order).order_by(
            col(Order.order_date).desc()
        )
        return list(self.session.exec(statement).all())

    def get_by_user(self, user_id: int) -> list[Order]:
        statement = (
            select(Order)
            .where(col(Order.user_id) == user_id)
            .order_by(col(Order.order_date).desc())
        )
        return list(self.session.exec(statement).all())

    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Order]:
        statement = (
            select(Order)
            .where(
                col(Order.order_date) >= start_date,
                col(Order.order_date) <= end_date,
            )
            .order_by(col(Order.order_date).desc())
        )
        return list(self.session.exec(statement).all())

    def delete(self, order_id: int) -> bool:
        order = self.get_by_id(order_id)

        if order is None:
            return False

        self.session.delete(order)
        self.session.flush()
        return True
