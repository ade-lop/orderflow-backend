"""api/routes/order_items.py"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.order_item import OrderItemCreate, OrderItemRead

router = APIRouter(
    prefix="/orders",
    tags=["items"],
)


@router.post(
    "/{order_id}/items",
    response_model=OrderItemRead,
    status_code=status.HTTP_201_CREATED,
)
def create_order_item(
    order_id: int,
    order_item_in: OrderItemCreate,
    db: Annotated[Session, Depends(get_db)],
) -> OrderItem:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    order_item = OrderItem(
        order_id=order_id,
        product_name=order_item_in.product_name,
        quantity=order_item_in.quantity,
        unit_price=order_item_in.unit_price,
    )

    db.add(order_item)
    db.commit()
    db.refresh(order_item)

    return order_item


@router.get(
    "/{order_id}/items",
    response_model=list[OrderItemRead],
    status_code=status.HTTP_200_OK,
)
def get_order_items_list(
    order_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[OrderItem]:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order.items
