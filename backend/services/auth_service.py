from sqlmodel import Session
from repositories.user import UserRepository
from model import User


class AuthService:
    def __init__(self, session: Session):
        self.users = UserRepository(session)

    def authenticate(self, login: str) -> User | None:
        return self.users.get_by_login(login.strip())
