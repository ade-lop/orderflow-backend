"""repositories/order_item.py"""
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.order_item import OrderItem


def create_order_item(
        db: Session,
        order_id: int,
        product_name: str,
        quantity: int,
        unit_price: Decimal,
) -> OrderItem:
    order_item = OrderItem(
        order_id=order_id,
        product_name=product_name,
        quantity=quantity,
        unit_price=unit_price,
    )
    db.add(order_item)
    return order_item
