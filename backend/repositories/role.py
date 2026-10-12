from sqlmodel import Session, select

from model import Role


class RoleRepository:
    """CRUD-операции с таблицей roles."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, role_id: int) -> Role | None:
        return self.session.get(Role, role_id)

    def get_by_name(self, role_name: str) -> Role | None:
        statement = select(Role).where(Role.role_name == role_name)
        return self.session.exec(statement).first()

    def get_all(self) -> list[Role]:
        statement = select(Role).order_by(Role.role_name)
        return list(self.session.exec(statement).all())

    def create(self, role: Role) -> Role:
        self.session.add(role)
        self.session.flush()
        self.session.refresh(role)
        return role

    def update(self, role: Role) -> Role:
        self.session.add(role)
        self.session.flush()
        self.session.refresh(role)
        return role

    def delete(self, role: Role) -> None:
        self.session.delete(role)
        self.session.flush()
