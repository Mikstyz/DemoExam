from pathlib import Path
import tomllib

from pydantic import BaseModel, Field

BACKEND_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BACKEND_DIR / "config.toml"


class ConfigModel(BaseModel):
    db_conn: str = Field(
        default="postgresql+psycopg://USER:PASSWORD@localhost:5432/chudo_obuv"
    )
    storage_dir: str = Field(default="./data")


def load_config() -> ConfigModel:
    if not CONFIG_PATH.is_file():
        raise FileNotFoundError(
            f"Не найден файл настроек {CONFIG_PATH} к PostgreSQL."
        )

    with CONFIG_PATH.open("rb") as file:
        config = ConfigModel(**tomllib.load(file))

    if any(marker in config.db_conn for marker in ("USER:PASSWORD@", "YOUR_USER", "YOUR_PASSWORD")) or config.db_conn.startswith(
        "postgresql+psycopg://USER:"
    ):
        raise ValueError(
            f"В {CONFIG_PATH} остались шаблонные реквизиты подключения к PostgreSQL"
        )

    return config
