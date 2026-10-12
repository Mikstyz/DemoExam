from sqlmodel import Session, select

from model import User


class UserRepository:
    """CRUD-операции с таблицей users."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def get_by_login(self, login: str) -> User | None:
        statement = select(User).where(User.login == login)
        return self.session.exec(statement).first()

    def get_by_role_id(self, role_id: int) -> list[User]:
        statement = (
            select(User)
            .where(User.role_id == role_id)
            .order_by(User.last_name, User.first_name)
        )
        return list(self.session.exec(statement).all())

    def get_all(self) -> list[User]:
        statement = select(User).order_by(User.last_name, User.first_name)
        return list(self.session.exec(statement).all())

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.session.delete(user)
        self.session.flush()
