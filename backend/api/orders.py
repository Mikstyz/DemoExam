from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from api.deps import get_session, get_current_user, require_roles, role_name
from model import Order, OrderItem, Product, Size, StockItem, User
from schemas import OrderCreate, OrderRead, OrderSummary, OrderItemRead, OrderDateUpdate
from services.discount_service import DiscountService

router = APIRouter(prefix="/api/orders", tags=["Заказы"])
MANAGER_ROLES = ("manager", "менеджер", "admin", "administrator", "администратор")
ADMIN_ROLES = ("admin", "administrator", "администратор")


def full_name(user: User) -> str:
    return " ".join(x for x in (user.last_name, user.first_name, user.middle_name) if x)


def order_payload(session: Session, order: Order) -> OrderRead:
    user = session.get(User, order.user_id)
    items_out = []
    total = Decimal("0.00")
    items = list(
        session.exec(
            select(OrderItem)
            .where(OrderItem.order_id == order.order_id)
            .order_by(OrderItem.order_item_id)
        ).all()
    )
    for item in items:
        product = session.get(Product, item.product_id)
        size = session.get(Size, item.size_id)
        line = (item.price * item.quantity).quantize(Decimal("0.01"))
        total += line
        items_out.append(
            OrderItemRead(
                order_item_id=item.order_item_id,
                product_id=item.product_id,
                product_name=product.product_name if product else "",
                manufacturer=product.manufacturer if product else "",
                size_id=item.size_id,
                size_value=size.size_value if size else "",
                quantity=item.quantity,
                price=item.price,
                line_total=line,
            )
        )
    return OrderRead(
        order_id=order.order_id,
        order_date=order.order_date,
        user_id=order.user_id,
        customer_full_name=full_name(user) if user else "",
        total=total,
        items=items_out,
    )


def summary(session: Session, order: Order):
    user = session.get(User, order.user_id)
    items = list(
        session.exec(
            select(OrderItem).where(OrderItem.order_id == order.order_id)
        ).all()
    )
    total = sum((i.price * i.quantity for i in items), Decimal("0.00"))
    return OrderSummary(
        order_id=order.order_id,
        order_date=order.order_date,
        user_id=order.user_id,
        customer_full_name=full_name(user) if user else "",
        total=total,
    )


def create_order(session: Session, customer_id: int, items_data):
    if not items_data:
        raise HTTPException(
            status_code=422, detail="Заказ должен содержать хотя бы одну позицию"
        )
    merged = {}
    for item in items_data:
        key = (item.product_id, item.size_id)
        merged[key] = merged.get(key, 0) + item.quantity
    try:
        order = Order(user_id=customer_id, order_date=datetime.now())
        session.add(order)
        session.flush()
        for (product_id, size_id), quantity in merged.items():
            stock = session.exec(
                select(StockItem)
                .where(StockItem.product_id == product_id, StockItem.size_id == size_id)
                .with_for_update()
            ).first()
            if stock is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Не найден остаток для товара {product_id}, размер {size_id}",
                )
            if stock.quantity_available < quantity:
                raise HTTPException(
                    status_code=409,
                    detail=f"Недостаточно остатка для товара {product_id}, размера {size_id}: доступно {stock.quantity_available}",
                )
            product = session.get(Product, product_id)
            if product is None:
                raise HTTPException(
                    status_code=404, detail=f"Товар {product_id} не найден"
                )
            if session.get(Size, size_id) is None:
                raise HTTPException(
                    status_code=404, detail=f"Размер {size_id} не найден"
                )
            stock.quantity_available -= quantity
            order_price, _discount_percent = DiscountService.discounted_price(
                session, product
            )
            session.add(
                OrderItem(
                    order_id=order.order_id,
                    product_id=product_id,
                    size_id=size_id,
                    quantity=quantity,
                    price=order_price,
                )
            )
        session.commit()
        session.refresh(order)
        return order
    except Exception:
        session.rollback()
        raise


@router.get(
    "",
    response_model=list[OrderSummary],
    summary="Список заказов (менеджер/администратор)",
)
def list_orders(
    session: Session = Depends(get_session),
    _user: User = Depends(require_roles(*MANAGER_ROLES)),
):
    orders = session.exec(
        select(Order).order_by(Order.order_date.desc(), Order.order_id.desc())
    ).all()
    return [summary(session, o) for o in orders]


@router.get("/my", response_model=list[OrderSummary], summary="Мои заказы")
def my_orders(
    session: Session = Depends(get_session), user: User = Depends(get_current_user)
):
    orders = session.exec(
        select(Order)
        .where(Order.user_id == user.user_id)
        .order_by(Order.order_date.desc())
    ).all()
    return [summary(session, o) for o in orders]


@router.post("", response_model=OrderRead, status_code=201, summary="Создать заказ")
def place_order(
    data: OrderCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    customer_id = user.user_id
    if (
        role_name(user) in {r.casefold() for r in MANAGER_ROLES}
        and data.user_id is not None
    ):
        customer_id = data.user_id
    elif data.user_id is not None and data.user_id != user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Нельзя оформить заказ от имени другого пользователя",
        )
    if session.get(User, customer_id) is None:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    order = create_order(session, customer_id, data.items)
    return order_payload(session, order)


@router.get("/{order_id}", response_model=OrderRead, summary="Состав заказа")
def get_order(
    order_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    if order.user_id != user.user_id and role_name(user) not in {
        r.casefold() for r in MANAGER_ROLES
    }:
        raise HTTPException(
            status_code=403, detail="Можно просматривать только собственные заказы"
        )
    return order_payload(session, order)


@router.delete("/{order_id}", summary="Удалить заказ (менеджер/администратор)")
def delete_order(
    order_id: int,
    session: Session = Depends(get_session),
    _user: User = Depends(require_roles(*MANAGER_ROLES)),
):
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    try:
        items = list(
            session.exec(select(OrderItem).where(OrderItem.order_id == order_id)).all()
        )
        for item in items:
            stock = session.exec(
                select(StockItem)
                .where(
                    StockItem.product_id == item.product_id,
                    StockItem.size_id == item.size_id,
                )
                .with_for_update()
            ).first()
            if stock is None:
                raise HTTPException(
                    status_code=409,
                    detail="Не найден остаток для восстановления товара из заказа",
                )
            stock.quantity_available += item.quantity
            session.delete(item)
        session.delete(order)
        session.commit()
        return {"detail": "Заказ удалён, остатки восстановлены"}
    except Exception:
        session.rollback()
        raise


@router.patch(
    "/{order_id}/date",
    response_model=OrderSummary,
    summary="Изменить дату заказа (только администратор)",
)
def update_order_date(
    order_id: int,
    data: OrderDateUpdate,
    session: Session = Depends(get_session),
    _user: User = Depends(require_roles(*ADMIN_ROLES)),
):
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    order.order_date = data.order_date.replace(tzinfo=None)
    session.add(order)
    session.commit()
    session.refresh(order)
    return summary(session, order)


@router.delete(
    "/{order_id}/items/{order_item_id}",
    summary="Удалить позицию заказа (только администратор)",
)
def delete_order_item(
    order_id: int,
    order_item_id: int,
    session: Session = Depends(get_session),
    _user: User = Depends(require_roles(*ADMIN_ROLES)),
):
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    item = session.get(OrderItem, order_item_id)
    if item is None or item.order_id != order_id:
        raise HTTPException(status_code=404, detail="Позиция заказа не найдена")
    try:
        stock = session.exec(
            select(StockItem)
            .where(
                StockItem.product_id == item.product_id,
                StockItem.size_id == item.size_id,
            )
            .with_for_update()
        ).first()
        if stock is None:
            raise HTTPException(
                status_code=409,
                detail="Не найден остаток для восстановления товара из заказа",
            )
        stock.quantity_available += item.quantity
        session.delete(item)
        session.commit()
        return {"detail": "Позиция удалена, остаток восстановлен"}
    except Exception:
        session.rollback()
        raise


@router.patch(
    "/{order_id}/items/{order_item_id}",
    response_model=OrderRead,
    summary="Изменить количество позиции (только администратор)",
)
def update_order_item_quantity(
    order_id: int,
    order_item_id: int,
    quantity: int = Query(gt=0, le=10000),
    session: Session = Depends(get_session),
    _user: User = Depends(require_roles(*ADMIN_ROLES)),
):
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    item = session.get(OrderItem, order_item_id)
    if item is None or item.order_id != order_id:
        raise HTTPException(status_code=404, detail="Позиция заказа не найдена")
    difference = quantity - item.quantity
    try:
        stock = session.exec(
            select(StockItem)
            .where(
                StockItem.product_id == item.product_id,
                StockItem.size_id == item.size_id,
            )
            .with_for_update()
        ).first()
        if stock is None:
            raise HTTPException(
                status_code=409, detail="Для позиции заказа не найдена запись остатка"
            )
        if difference > 0 and stock.quantity_available < difference:
            raise HTTPException(
                status_code=409,
                detail=f"Недостаточно остатка. Доступно дополнительно: {stock.quantity_available}",
            )
        stock.quantity_available -= difference
        item.quantity = quantity
        session.add(item)
        session.commit()
        session.refresh(order)
        return order_payload(session, order)
    except Exception:
        session.rollback()
        raise
