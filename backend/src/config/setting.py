import os
import tomllib
from pydantic import BaseModel, Field

class ConfigModel(BaseModel):
    db_conn: str = Field(default="postgresql://postgres:password@localhost:5432/postgres")
    storage_dir: str = Field(default="./data")


def load_config(filepath: str = "config.toml") -> ConfigModel:
    if not os.path.exists(filepath):
        return ConfigModel()

    with open(filepath, "rb") as f:
        data = tomllib.load(f)

    return ConfigModel(**data)


def save_default_config(filepath: str = "config.toml") -> None:
    if os.path.exists(filepath):
        return

    cfg = ConfigModel()
    toml_content = (
        f'db_conn = "{cfg.db_conn}"\n'
        f'storage_dir = "{cfg.storage_dir}"\n'
    )
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(toml_content)
