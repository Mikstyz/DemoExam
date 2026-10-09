from typing import Any

from sqlmodel import Session, col, select

from model.user import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def get_by_login(self, login: str) -> User | None:
        statement = select(User).where(
            col(User.login) == login
        )
        return self.session.exec(statement).first()

    def get_all(self) -> list[User]:
        statement = select(User).order_by(col(User.user_id))
        return list(self.session.exec(statement).all())

    def update(
        self,
        user_id: int,
        data: dict[str, Any],
    ) -> User | None:
        user = self.get_by_id(user_id)

        if user is None:
            return None

        allowed_fields = {
            "last_name",
            "first_name",
            "middle_name",
            "login",
            "role_id",
        }

        for field, value in data.items():
            if field in allowed_fields:
                setattr(user, field, value)

        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)

        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)

        if user is None:
            return False

        self.session.delete(user)
        self.session.flush()

        return True
