from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderRead

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.post(
    "",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    order_in: OrderCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Order:
    order = Order(title=order_in.title)

    db.add(order)
    db.commit()
    db.refresh(order)

    return order


@router.get(
    "",
    response_model=list[OrderRead],
)
def get_orders_list(
    db: Annotated[Session, Depends(get_db)],
) -> list[Order]:
    statement = select(Order)
    result = db.execute(statement)
    orders = result.scalars().all()

    return orders


@router.get(
    "/{order_id}",
    response_model=OrderRead,
)
def get_order(
    order_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Order:
    order = db.get(Order, order_id)

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order
