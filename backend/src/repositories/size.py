from sqlmodel import Session, col, select

from model.size import Size


class SizeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, size: Size) -> Size:
        self.session.add(size)
        self.session.flush()
        self.session.refresh(size)
        return size

    def get_by_id(self, size_id: int) -> Size | None:
        return self.session.get(Size, size_id)

    def get_by_value(self, size_value: str) -> Size | None:
        statement = select(Size).where(
            col(Size.size_value) == size_value
        )
        return self.session.exec(statement).first()

    def get_all(self) -> list[Size]:
        statement = select(Size).order_by(col(Size.size_value))
        return list(self.session.exec(statement).all())

    def delete(self, size_id: int) -> bool:
        size = self.get_by_id(size_id)

        if size is None:
            return False

        self.session.delete(size)
        self.session.flush()
        return True
