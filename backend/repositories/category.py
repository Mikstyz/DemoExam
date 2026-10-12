from sqlmodel import Session, select

from model import Category


class CategoryRepository:
    """CRUD-операции с таблицей categories."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, category_id: int) -> Category | None:
        return self.session.get(Category, category_id)

    def get_by_name(self, name: str) -> Category | None:
        statement = select(Category).where(Category.name == name)
        return self.session.exec(statement).first()

    def get_all(self) -> list[Category]:
        statement = select(Category).order_by(Category.name)
        return list(self.session.exec(statement).all())

    def create(self, category: Category) -> Category:
        self.session.add(category)
        self.session.flush()
        self.session.refresh(category)
        return category

    def update(self, category: Category) -> Category:
        self.session.add(category)
        self.session.flush()
        self.session.refresh(category)
        return category

    def delete(self, category: Category) -> None:
        self.session.delete(category)
        self.session.flush()
