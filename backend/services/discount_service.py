from datetime import date, datetime, time
from decimal import Decimal, ROUND_HALF_UP

from sqlmodel import Session, select

from model import Order, OrderItem, Product


class DiscountService:
    @staticmethod
    def previous_month(today: date | None = None) -> tuple[datetime, datetime]:
        """Return naive bounds for the previous calendar month: [start, end)."""
        today = today or datetime.now().date()
        end_date = today.replace(day=1)
        if end_date.month == 1:
            start_date = end_date.replace(year=end_date.year - 1, month=12)
        else:
            start_date = end_date.replace(month=end_date.month - 1)

        start = datetime.combine(start_date, time.min)
        end = datetime.combine(end_date, time.min)
        return start, end

    @classmethod
    def discounted_price(
        cls, session: Session, product: Product, today: date | None = None
    ) -> tuple[Decimal, int]:
        start, end = cls.previous_month(today)
        ordered = (
            session.exec(
                select(OrderItem.order_item_id)
                .join(Order, Order.order_id == OrderItem.order_id)
                .where(
                    OrderItem.product_id == product.product_id,
                    Order.order_date >= start,
                    Order.order_date < end,
                )
                .limit(1)
            ).first()
            is not None
        )
        discount = 0 if ordered else 25
        price = (product.price * Decimal(100 - discount) / Decimal(100)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return price, discount
