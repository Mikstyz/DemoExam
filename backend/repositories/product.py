from decimal import Decimal

from sqlmodel import Session, select

from model import Product, Category


class ProductRepository:
    """CRUD-операции и фильтрация таблицы products."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, product_id: int) -> Product | None:
        return self.session.get(Product, product_id)

    def get_by_name(self, product_name: str) -> Product | None:
        statement = select(Product).where(Product.product_name == product_name)
        return self.session.exec(statement).first()

    def get_all(self) -> list[Product]:
        statement = select(Product).order_by(Product.product_name)
        return list(self.session.exec(statement).all())

    def get_by_category(self, category_id: int) -> list[Product]:
        statement = (
            select(Product)
            .where(Product.category_id == category_id)
            .order_by(Product.product_name)
        )
        return list(self.session.exec(statement).all())

    def search_by_name(self, query: str) -> list[Product]:
        statement = (
            select(Product)
            .where(Product.product_name.ilike(f"%{query}%"))
            .order_by(Product.product_name)
        )
        return list(self.session.exec(statement).all())

    def get_by_price_range(
        self,
        min_price: Decimal,
        max_price: Decimal,
    ) -> list[Product]:
        statement = (
            select(Product)
            .where(Product.price >= min_price, Product.price <= max_price)
            .order_by(Product.price, Product.product_name)
        )
        return list(self.session.exec(statement).all())

    def create(self, product: Product) -> Product:
        self.session.add(product)
        self.session.flush()
        self.session.refresh(product)
        return product

    def update(self, product: Product) -> Product:
        self.session.add(product)
        self.session.flush()
        self.session.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.session.delete(product)
        self.session.flush()
