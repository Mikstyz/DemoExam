from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api import auth, categories, orders, products
from config.setting import load_config
from db.database import create_tables

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"
PUBLIC_IMAGES_DIR = FRONTEND_DIR / "public" / "images"


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Чудо Обувь",
    description="Каталог обуви, оформление заказов и управление остатками.",
    version="2.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Сначала API-маршруты, затем статические файлы, чтобы фронтенд не перехватывал API.
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(categories.router)

_storage_dir = Path(load_config().storage_dir)
if not _storage_dir.is_absolute():
    _storage_dir = BACKEND_DIR / _storage_dir
_storage_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=_storage_dir), name="media")

if PUBLIC_IMAGES_DIR.is_dir():
    app.mount("/images", StaticFiles(directory=PUBLIC_IMAGES_DIR), name="images")


@app.get("/health", tags=["Система"])
def health():
    return {"status": "ok", "service": "chudo-obuv"}


@app.get("/", include_in_schema=False)
def frontend():
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.is_file():
        return {"detail": "Фронтенд не найден. Проверьте папку frontend."}
    return FileResponse(index_file)


@app.get("/{asset_path:path}", include_in_schema=False)
def frontend_assets(asset_path: str):
    """Отдаёт только реальные файлы фронтенда, не подменяя API-ошибки index.html."""
    requested = (FRONTEND_DIR / asset_path).resolve()
    if not requested.is_relative_to(FRONTEND_DIR.resolve()) or not requested.is_file():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(requested)
