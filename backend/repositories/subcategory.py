from sqlmodel import Session, select

from model import Subcategory


class SubcategoryRepository:
    """CRUD-операции с таблицей subcategories."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, subcategory_id: int) -> Subcategory | None:
        return self.session.get(Subcategory, subcategory_id)

    def get_by_category_and_name(
        self,
        category_id: int,
        name: str,
    ) -> Subcategory | None:
        statement = select(Subcategory).where(
            Subcategory.category_id == category_id,
            Subcategory.name == name,
        )
        return self.session.exec(statement).first()

    def get_by_category_id(self, category_id: int) -> list[Subcategory]:
        statement = (
            select(Subcategory)
            .where(Subcategory.category_id == category_id)
            .order_by(Subcategory.name)
        )
        return list(self.session.exec(statement).all())

    def get_all(self) -> list[Subcategory]:
        statement = select(Subcategory).order_by(
            Subcategory.category_id, Subcategory.name
        )
        return list(self.session.exec(statement).all())

    def create(self, subcategory: Subcategory) -> Subcategory:
        self.session.add(subcategory)
        self.session.flush()
        self.session.refresh(subcategory)
        return subcategory

    def update(self, subcategory: Subcategory) -> Subcategory:
        self.session.add(subcategory)
        self.session.flush()
        self.session.refresh(subcategory)
        return subcategory

    def delete(self, subcategory: Subcategory) -> None:
        self.session.delete(subcategory)
        self.session.flush()
