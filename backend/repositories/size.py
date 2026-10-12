from sqlmodel import Session, select

from model import Size


class SizeRepository:
    """CRUD-операции с таблицей sizes."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, size_id: int) -> Size | None:
        return self.session.get(Size, size_id)

    def get_by_value(self, size_value: str) -> Size | None:
        statement = select(Size).where(Size.size_value == size_value)
        return self.session.exec(statement).first()

    def get_by_value_normalized(self, size_value: str) -> Size | None:
        """Find a size ignoring case and surrounding/repeated whitespace."""
        normalized = " ".join(size_value.split()).casefold()
        for size in self.get_all():
            if " ".join(size.size_value.split()).casefold() == normalized:
                return size
        return None

    def get_all(self) -> list[Size]:
        statement = select(Size).order_by(Size.size_value)
        return list(self.session.exec(statement).all())

    def create(self, size: Size) -> Size:
        self.session.add(size)
        self.session.flush()
        self.session.refresh(size)
        return size

    def update(self, size: Size) -> Size:
        self.session.add(size)
        self.session.flush()
        self.session.refresh(size)
        return size

    def delete(self, size: Size) -> None:
        self.session.delete(size)
        self.session.flush()
