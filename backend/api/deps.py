from collections.abc import Generator
from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session
from db.database import engine
from repositories.user import UserRepository
from model import User


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def get_current_user(
    x_user_id: int | None = Header(default=None, alias="X-User-ID"),
    session: Session = Depends(get_session),
) -> User:
    """Учебная авторизация по ID пользователя после входа по логину."""
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Сначала войдите по логину и передавайте заголовок X-User-ID",
        )
    user = UserRepository(session).get_by_id(x_user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден"
        )
    return user


def role_name(user: User) -> str:
    return user.role.role_name.strip().casefold() if user.role else ""


def require_roles(*allowed: str):
    normalized = {value.casefold() for value in allowed}

    def checker(user: User = Depends(get_current_user)) -> User:
        if role_name(user) not in normalized:
            raise HTTPException(
                status_code=403, detail="Недостаточно прав для выполнения операции"
            )
        return user

    return checker
