from logging import *
import psycopg

#==============================
from config import setting
from db import database

#==============================

CONFIG_DIR = "../config.toml"

def log_init():
    Logger("log")
    basicConfig(level=INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    log_init()

    cfg = setting.load_config(CONFIG_DIR)
    info(f"[cfg]: {cfg}")

    db_engine = database.connection(cfg.db_conn);
    info(f"[db_engine]: {db_engine}")

    database.create_tables(db_engine)


if __name__ == "__main__":
    main()
