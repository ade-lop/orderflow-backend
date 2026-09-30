"""/repositories/orders.py"""
from sqlalchemy.orm import Session

from app.models.order import Order


def create_order(
        db: Session,
        title: str,
) -> Order:
    order = Order(title=title)
    db.add(order)
    db.flush()
    return order
