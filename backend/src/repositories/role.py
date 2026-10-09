from sqlmodel import Session, col, select

from model.role import Role


class RoleRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, role: Role) -> Role:
        self.session.add(role)
        self.session.flush()
        self.session.refresh(role)
        return role

    def get_by_id(self, role_id: int) -> Role | None:
        return self.session.get(Role, role_id)

    def get_by_name(self, role_name: str) -> Role | None:
        statement = select(Role).where(
            col(Role.role_name) == role_name
        )
        return self.session.exec(statement).first()

    def get_all(self) -> list[Role]:
        statement = select(Role).order_by(col(Role.role_id))
        return list(self.session.exec(statement).all())

    def delete(self, role_id: int) -> bool:
        role = self.get_by_id(role_id)

        if role is None:
            return False

        self.session.delete(role)
        self.session.flush()

        return True
