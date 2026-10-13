from decimal import Decimal
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from config.setting import load_config
from sqlmodel import Session, select
from api.deps import get_session, require_roles, EDITOR_ROLES
from model import Product, StockItem, Size, OrderItem, Category, Subcategory
from repositories.product import ProductRepository
from repositories.stock_item import StockItemRepository
from repositories.size import SizeRepository
from services.discount_service import DiscountService
from schemas import (
    ProductRead,
    ProductDetail,
    SizeAvailability,
    ProductCreate,
    ProductUpdate,
    StockUpdate,
    StockBySizeValue,
)

router = APIRouter(prefix="/api/products", tags=["Товары"])
def make_product(session: Session, product: Product, detail: bool = False):
    category = session.get(Category, product.category_id)
    subcategory = (
        session.get(Subcategory, product.subcategory_id)
        if product.subcategory_id
        else None
    )
    stocks = session.exec(
        select(StockItem, Size)
        .join(Size, Size.size_id == StockItem.size_id)
        .where(StockItem.product_id == product.product_id)
        .order_by(Size.size_value)
    ).all()
    total = sum(stock.quantity_available for stock, _size in stocks)
    discounted_price, discount = DiscountService.discounted_price(session, product)
    result = dict(
        product_id=product.product_id,
        category_id=product.category_id,
        category=category.name if category else "",
        subcategory_id=product.subcategory_id,
        subcategory=subcategory.name if subcategory else None,
        image_path=product.image_path,
        product_name=product.product_name,
        manufacturer=product.manufacturer,
        description=product.description,
        composition=product.composition,
        price=product.price,
        discounted_price=discounted_price,
        discount_percent=discount,
        total_quantity=total,
        low_stock=total <= 3,
    )
    if detail:
        result["sizes"] = [
            SizeAvailability(
                size_id=size.size_id,
                size_value=size.size_value,
                quantity_available=stock.quantity_available,
            )
            for stock, size in stocks
        ]
        result["size_range"] = [size.size_value for _stock, size in stocks]
        return ProductDetail(**result)
    return ProductRead(**result)


def validate_category_pair(
    session: Session, category_id: int, subcategory_id: int | None
) -> None:
    if session.get(Category, category_id) is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    if subcategory_id is not None:
        subcategory = session.get(Subcategory, subcategory_id)
        if subcategory is None:
            raise HTTPException(status_code=404, detail="Подкатегория не найдена")
        if subcategory.category_id != category_id:
            raise HTTPException(
                status_code=422,
                detail="Подкатегория не относится к выбранной категории",
            )


@router.get("", response_model=list[ProductRead], summary="Список товаров")
def list_products(
    category_id: int | None = Query(default=None, gt=0),
    subcategory_id: int | None = Query(default=None, gt=0),
    search: str | None = Query(default=None, max_length=200),
    sort: str | None = Query(default=None, pattern="^(price_asc|price_desc)$"),
    session: Session = Depends(get_session),
):
    statement = select(Product)
    if category_id is not None:
        statement = statement.where(Product.category_id == category_id)
    if subcategory_id is not None:
        statement = statement.where(Product.subcategory_id == subcategory_id)
    if search and search.strip():
        term = f"%{search.strip()}%"
        statement = statement.where(
            (Product.product_name.ilike(term)) | (Product.description.ilike(term))
        )
    products = [
        make_product(session, product) for product in session.exec(statement).all()
    ]
    if sort == "price_asc":
        products.sort(
            key=lambda item: (item.discounted_price, item.product_name.casefold())
        )
    elif sort == "price_desc":
        products.sort(
            key=lambda item: (-item.discounted_price, item.product_name.casefold())
        )
    else:
        products.sort(key=lambda item: item.product_name.casefold())
    return products


@router.get(
    "/{product_id}",
    response_model=ProductDetail,
    summary="Подробная информация о товаре",
)
def product_detail(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return make_product(session, product, detail=True)


@router.post(
    "", response_model=ProductDetail, status_code=201, summary="Добавить товар"
)
def create_product(
    data: ProductCreate,
    session: Session = Depends(get_session),
    _user=Depends(require_roles(*EDITOR_ROLES)),
):
    validate_category_pair(session, data.category_id, data.subcategory_id)
    product = Product(**data.model_dump())
    try:
        ProductRepository(session).create(product)
        session.commit()
        session.refresh(product)
        return make_product(session, product, detail=True)
    except Exception:
        session.rollback()
        raise


@router.patch("/{product_id}", response_model=ProductDetail, summary="Изменить товар")
def update_product(
    product_id: int,
    data: ProductUpdate,
    session: Session = Depends(get_session),
    _user=Depends(require_roles(*EDITOR_ROLES)),
):
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    changes = data.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="Не переданы поля для изменения")
    category_id = changes.get("category_id", product.category_id)
    subcategory_id = changes.get("subcategory_id", product.subcategory_id)
    validate_category_pair(session, category_id, subcategory_id)
    for field, value in changes.items():
        setattr(product, field, value)
    try:
        session.add(product)
        session.commit()
        session.refresh(product)
        return make_product(session, product, detail=True)
    except Exception:
        session.rollback()
        raise


@router.delete("/{product_id}", summary="Удалить товар")
def delete_product(
    product_id: int,
    session: Session = Depends(get_session),
    _user=Depends(require_roles(*EDITOR_ROLES)),
):
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    if (
        session.exec(
            select(OrderItem.order_item_id)
            .where(OrderItem.product_id == product_id)
            .limit(1)
        ).first()
        is not None
    ):
        raise HTTPException(
            status_code=409,
            detail="Нельзя удалить товар из истории заказов. Измените карточку вместо удаления.",
        )
    try:
        for stock in session.exec(
            select(StockItem).where(StockItem.product_id == product_id)
        ).all():
            session.delete(stock)
        session.delete(product)
        session.commit()
        return {"detail": "Товар удалён"}
    except Exception:
        session.rollback()
        raise


@router.put(
    "/{product_id}/stock/by-value",
    summary="Создать или изменить остаток по значению размера",
)
def set_stock_by_size_value(
    product_id: int,
    data: StockBySizeValue,
    session: Session = Depends(get_session),
    _user=Depends(require_roles(*EDITOR_ROLES)),
):
    if session.get(Product, product_id) is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    value = " ".join(data.size_value.split())
    size_repository = SizeRepository(session)
    size = size_repository.get_by_value_normalized(value)
    try:
        if size is None:
            size = size_repository.create(Size(size_value=value))
        stock_repository = StockItemRepository(session)
        stock = stock_repository.get_by_product_and_size(product_id, size.size_id)
        if stock is None:
            stock = stock_repository.create(
                StockItem(
                    product_id=product_id,
                    size_id=size.size_id,
                    quantity_available=data.quantity_available,
                )
            )
        else:
            stock.quantity_available = data.quantity_available
            stock_repository.update(stock)
        session.commit()
        session.refresh(stock)
        return {
            "stock_item_id": stock.stock_item_id,
            "product_id": product_id,
            "size_id": size.size_id,
            "size_value": size.size_value,
            "quantity_available": stock.quantity_available,
        }
    except Exception:
        session.rollback()
        raise


@router.put("/{product_id}/stock/{size_id}", summary="Изменить остаток по размеру")
def set_stock(
    product_id: int,
    size_id: int,
    data: StockUpdate,
    session: Session = Depends(get_session),
    _user=Depends(require_roles(*EDITOR_ROLES)),
):
    if session.get(Product, product_id) is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    if session.get(Size, size_id) is None:
        raise HTTPException(status_code=404, detail="Размер не найден")
    repository = StockItemRepository(session)
    stock = repository.get_by_product_and_size(product_id, size_id)
    try:
        if stock is None:
            stock = StockItem(
                product_id=product_id,
                size_id=size_id,
                quantity_available=data.quantity_available,
            )
            repository.create(stock)
        else:
            stock.quantity_available = data.quantity_available
            repository.update(stock)
        session.commit()
        session.refresh(stock)
        return {
            "stock_item_id": stock.stock_item_id,
            "product_id": stock.product_id,
            "size_id": stock.size_id,
            "quantity_available": stock.quantity_available,
        }
    except Exception:
        session.rollback()
        raise


ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_IMAGE_SIZE = 10 * 1024 * 1024


def _storage_products_dir() -> Path:
    storage = Path(load_config().storage_dir)
    if not storage.is_absolute():
        storage = Path(__file__).resolve().parents[1] / storage
    target = storage / "products"
    target.mkdir(parents=True, exist_ok=True)
    return target


@router.post("/{product_id}/image", summary="Загрузить изображение товара")
async def upload_product_image(
    product_id: int,
    image: UploadFile = File(...),
    session: Session = Depends(get_session),
    _user=Depends(require_roles(*EDITOR_ROLES)),
):
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    extension = ALLOWED_IMAGE_TYPES.get(image.content_type or "")
    if extension is None:
        raise HTTPException(
            status_code=415, detail="Поддерживаются изображения JPG, PNG, WEBP и GIF"
        )
    content = await image.read(MAX_IMAGE_SIZE + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Файл изображения пуст")
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413, detail="Размер изображения не должен превышать 10 МБ"
        )
    signatures = {
        ".jpg": (b"\xff\xd8\xff",),
        ".png": (b"\x89PNG\r\n\x1a\n",),
        ".webp": (b"RIFF",),
        ".gif": (b"GIF87a", b"GIF89a"),
    }
    if not any(content.startswith(signature) for signature in signatures[extension]):
        raise HTTPException(
            status_code=415,
            detail="Содержимое файла не соответствует формату изображения",
        )
    if extension == ".webp" and content[8:12] != b"WEBP":
        raise HTTPException(status_code=415, detail="Некорректный WEBP-файл")

    filename = f"{product_id}_{uuid4().hex}{extension}"
    target = _storage_products_dir() / filename
    target.write_bytes(content)
    old_path = product.image_path
    product.image_path = f"/media/products/{filename}"
    try:
        session.add(product)
        session.commit()
        session.refresh(product)
    except Exception:
        session.rollback()
        target.unlink(missing_ok=True)
        raise

    if old_path and old_path.startswith("/media/products/"):
        old_file = _storage_products_dir() / Path(old_path).name
        if old_file != target:
            old_file.unlink(missing_ok=True)
    return {"product_id": product_id, "image_path": product.image_path}
