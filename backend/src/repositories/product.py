from typing import Any

from sqlmodel import Session, col, select

from model.product import Product


class ProductRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, product: Product) -> Product:
        self.session.add(product)
        self.session.flush()
        self.session.refresh(product)
        return product

    def get_by_id(self, product_id: int) -> Product | None:
        return self.session.get(Product, product_id)

    def get_all(self) -> list[Product]:
        statement = select(Product).order_by(col(Product.product_name))
        return list(self.session.exec(statement).all())

    def get_by_name(self, name: str) -> list[Product]:
        statement = (
            select(Product)
            .where(col(Product.product_name).ilike(f"%{name}%"))
            .order_by(col(Product.product_name))
        )
        return list(self.session.exec(statement).all())

    def get_by_category(self, category: str) -> list[Product]:
        statement = (
            select(Product)
            .where(Product.category == category)
            .order_by(col(Product.product_name))
        )
        return list(self.session.exec(statement).all())

    def update(
        self,
        product_id: int,
        data: dict[str, Any],
    ) -> Product | None:
        product = self.get_by_id(product_id)

        if product is None:
            return None

        allowed_fields = {
            "category",
            "subcategory",
            "image_path",
            "product_name",
            "manufacturer",
            "description",
            "composition",
            "price",
        }

        for field, value in data.items():
            if field in allowed_fields:
                setattr(product, field, value)

        self.session.add(product)
        self.session.flush()
        self.session.refresh(product)
        return product

    def delete(self, product_id: int) -> bool:
        product = self.get_by_id(product_id)

        if product is None:
            return False

        self.session.delete(product)
        self.session.flush()
        return True
