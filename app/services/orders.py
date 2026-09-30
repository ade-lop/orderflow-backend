"""/services/orders.py"""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.order import Order
from app.repositories.order_item import create_order_item
from app.repositories.orders import create_order
from app.schemas.order import OrderCreateWithItems


class OrderCreationError(Exception):
    pass

def create_order_with_items(
        db: Session,
        order_in: OrderCreateWithItems,
) -> Order:
    try:
        order = create_order(db, order_in.title)
        for item in order_in.items:
            create_order_item(
                db=db,
                order_id=order.id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
        db.commit()
        return order
    except IntegrityError as exc:
        db.rollback()
        raise OrderCreationError() from exc
