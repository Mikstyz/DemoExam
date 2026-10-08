from sqlmodel import SQLModel, create_engine

from model import (
    Role,
    User,
    Product,
    Size,
    StockItem,
    Order,
    OrderItem,
)


def connection(db_url: str):
    return create_engine(
        db_url,
        echo=True,
    )


def create_tables(engine):
    SQLModel.metadata.create_all(engine)


def drop_tables(engine):
    SQLModel.metadata.drop_all(engine)


def recreate_tables(engine):
    drop_tables(engine)
    create_tables(engine)
