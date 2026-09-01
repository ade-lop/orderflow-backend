"""
/models/order_item.py
"""
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.order import Order


class OrderItem(Base):
    __tablename__ = "order_items"

    __table_args__ = (
        CheckConstraint(
            "product_name <> ''",
            name="ck_order_items_product_name_not_empty",
        ),
        CheckConstraint(
            r"product_name = btrim(product_name, E' \t\n\r\f' || chr(11))",
            name="ck_order_items_product_name_trimmed",
        ),
        CheckConstraint(
            "quantity > 0",
            name="ck_order_items_quantity_positive",
        ),
        CheckConstraint(
            "unit_price > 0",
            name="ck_order_items_unit_price_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey(
            "orders.id",
            ondelete="CASCADE"
        ),
        index=True,
    )
    product_name: Mapped[str] = mapped_column(String(400))
    quantity: Mapped[int] = mapped_column()
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    order: Mapped[Order] = relationship(
        back_populates="items",
    )
