from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from repositories.user import UserRepository
from schemas import LoginRequest, UserRead
from api.deps import get_session, get_current_user
from model import User

router = APIRouter(prefix="/api/auth", tags=["Авторизация"])


def to_user_read(user: User) -> UserRead:
    return UserRead(
        user_id=user.user_id,
        last_name=user.last_name,
        first_name=user.first_name,
        middle_name=user.middle_name,
        login=user.login,
        role=user.role.role_name if user.role else "",
    )


@router.post("/login", response_model=UserRead, summary="Войти по логину без пароля")
def login(data: LoginRequest, session: Session = Depends(get_session)):
    user = UserRepository(session).get_by_login(data.login.strip())
    if user is None:
        raise HTTPException(
            status_code=401, detail="Пользователь с таким логином не найден"
        )
    return to_user_read(user)


@router.get("/me", response_model=UserRead, summary="Текущий пользователь")
def me(user: User = Depends(get_current_user)):
    return to_user_read(user)
