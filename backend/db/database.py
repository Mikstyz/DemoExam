from sqlmodel import SQLModel, Session, create_engine
from config.setting import load_config
from model import (
    Role,
    User,
    Category,
    Subcategory,
    Product,
    Size,
    StockItem,
    Order,
    OrderItem,
)


def connection(db_url: str):
    return create_engine(db_url, echo=False, pool_pre_ping=True)


engine = connection(load_config().db_conn)


def create_tables(database_engine=engine) -> None:
    SQLModel.metadata.create_all(database_engine)


def get_session(database_engine=engine):
    with Session(database_engine) as session:
        yield session
