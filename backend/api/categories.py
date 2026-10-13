from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from api.deps import get_session, require_roles, EDITOR_ROLES
from model import Category, Subcategory, Product
from schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryRead,
    SubcategoryCreate,
    SubcategoryUpdate,
    SubcategoryRead,
)

router = APIRouter(prefix="/api", tags=["Категории"])
@router.get(
    "/categories", response_model=list[CategoryRead], summary="Список категорий"
)
def list_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category).order_by(Category.name)).all()


@router.post(
    "/categories",
    response_model=CategoryRead,
    status_code=201,
    summary="Создать категорию",
)
def create_category(
    data: CategoryCreate,
    session: Session = Depends(get_session),
    _user=Depends(require_roles(*EDITOR_ROLES)),
):
    name = " ".join(data.name.split())
    if not name:
        raise HTTPException(
            status_code=422, detail="Название категории не может быть пустым"
        )
    if session.exec(select(Category).where(Category.name.ilike(name))).first():
        raise HTTPException(status_code=409, detail="Такая категория уже существует")
    category = Category(name=name)
    session.add(category)
    try:
        session.commit()
        session.refresh(category)
        return category
    except Exception:
        session.rollback()
        raise


@router.patch(
    "/categories/{category_id}",
    response_model=CategoryRead,
    summary="Переименовать категорию",
)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    session: Session = Depends(get_session),
    _user=Depends(require_roles(*EDITOR_ROLES)),
):
    category = session.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    name = " ".join(data.name.split())
    if not name:
        raise HTTPException(
            status_code=422, detail="Название категории не может быть пустым"
        )
    duplicate = session.exec(
        select(Category).where(
            Category.name.ilike(name), Category.category_id != category_id
        )
    ).first()
    if duplicate:
        raise HTTPException(
            status_code=409, detail="Категория с таким названием уже существует"
        )
    category.name = name
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.delete("/categories/{category_id}", summary="Удалить категорию")
def delete_category(
    category_id: int,
    session: Session = Depends(get_session),
    _user=Depends(require_roles(*EDITOR_ROLES)),
):
    category = session.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    if (
        session.exec(
            select(Subcategory.subcategory_id)
            .where(Subcategory.category_id == category_id)
            .limit(1)
        ).first()
        or session.exec(
            select(Product.product_id)
            .where(Product.category_id == category_id)
            .limit(1)
        ).first()
    ):
        raise HTTPException(
            status_code=409,
            detail="Сначала перенесите или удалите товары и подкатегории этой категории",
        )
    session.delete(category)
    session.commit()
    return {"detail": "Категория удалена"}


@router.get(
    "/subcategories",
    response_model=list[SubcategoryRead],
    summary="Список подкатегорий",
)
def list_subcategories(
    category_id: int | None = None, session: Session = Depends(get_session)
):
    statement = select(Subcategory)
    if category_id is not None:
        statement = statement.where(Subcategory.category_id == category_id)
    return session.exec(statement.order_by(Subcategory.name)).all()


@router.post(
    "/subcategories",
    response_model=SubcategoryRead,
    status_code=201,
    summary="Создать подкатегорию",
)
def create_subcategory(
    data: SubcategoryCreate,
    session: Session = Depends(get_session),
    _user=Depends(require_roles(*EDITOR_ROLES)),
):
    if session.get(Category, data.category_id) is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    name = " ".join(data.name.split())
    if not name:
        raise HTTPException(
            status_code=422, detail="Название подкатегории не может быть пустым"
        )
    duplicate = session.exec(
        select(Subcategory).where(
            Subcategory.category_id == data.category_id, Subcategory.name.ilike(name)
        )
    ).first()
    if duplicate:
        raise HTTPException(
            status_code=409, detail="Такая подкатегория уже существует в этой категории"
        )
    subcategory = Subcategory(name=name, category_id=data.category_id)
    session.add(subcategory)
    session.commit()
    session.refresh(subcategory)
    return subcategory


@router.patch(
    "/subcategories/{subcategory_id}",
    response_model=SubcategoryRead,
    summary="Изменить подкатегорию",
)
def update_subcategory(
    subcategory_id: int,
    data: SubcategoryUpdate,
    session: Session = Depends(get_session),
    _user=Depends(require_roles(*EDITOR_ROLES)),
):
    subcategory = session.get(Subcategory, subcategory_id)
    if subcategory is None:
        raise HTTPException(status_code=404, detail="Подкатегория не найдена")
    changes = data.model_dump(exclude_unset=True)
    category_id = changes.get("category_id", subcategory.category_id)
    name = " ".join(changes.get("name", subcategory.name).split())
    if session.get(Category, category_id) is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    duplicate = session.exec(
        select(Subcategory).where(
            Subcategory.category_id == category_id,
            Subcategory.name.ilike(name),
            Subcategory.subcategory_id != subcategory_id,
        )
    ).first()
    if duplicate:
        raise HTTPException(
            status_code=409, detail="Такая подкатегория уже существует в этой категории"
        )
    name = name.strip()
    if not name:
        raise HTTPException(
            status_code=422, detail="Название подкатегории не может быть пустым"
        )
    subcategory.category_id = category_id
    subcategory.name = name
    session.add(subcategory)
    session.commit()
    session.refresh(subcategory)
    return subcategory


@router.delete("/subcategories/{subcategory_id}", summary="Удалить подкатегорию")
def delete_subcategory(
    subcategory_id: int,
    session: Session = Depends(get_session),
    _user=Depends(require_roles(*EDITOR_ROLES)),
):
    subcategory = session.get(Subcategory, subcategory_id)
    if subcategory is None:
        raise HTTPException(status_code=404, detail="Подкатегория не найдена")
    if session.exec(
        select(Product.product_id)
        .where(Product.subcategory_id == subcategory_id)
        .limit(1)
    ).first():
        raise HTTPException(
            status_code=409, detail="Сначала назначьте товарам другую подкатегорию"
        )
    session.delete(subcategory)
    session.commit()
    return {"detail": "Подкатегория удалена"}
