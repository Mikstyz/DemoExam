from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from config.setting import load_config

from db.database import create_tables
from api import auth, products, orders, categories


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Чудо Обувь REST API",
    description=(
        "REST API каталога обуви, авторизации и управления заказами. "
        "Доступ к PostgreSQL осуществляется через SQLModel ORM."
    ),
    version="1.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(categories.router)

_storage_dir = Path(load_config().storage_dir)
if not _storage_dir.is_absolute():
    _storage_dir = Path(__file__).resolve().parent / _storage_dir
_storage_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=_storage_dir), name="media")


@app.get("/health", tags=["Система"])
def health():
    return {"status": "ok", "service": "chudo-obuv-api"}
