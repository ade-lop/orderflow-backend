"""
models/order.py
"""
import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.order_item import OrderItem


class Order(Base):
    __tablename__ = "orders"

    __table_args__ = (
        CheckConstraint(
            "title <> ''",
            name="ck_orders_title_not_empty",
        ),
        CheckConstraint(
            r"title = btrim(title, E' \t\n\r\f' || chr(11))",
            name="ck_orders_title_trimmed",
        ),
        CheckConstraint(
            "status IN ('new', 'processing', 'canceled', 'completed')",
            name="ck_orders_status_allowed",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))

    status: Mapped[str] = mapped_column(
        String(30),
        server_default="new"
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    items: Mapped[list[OrderItem]] = relationship(
        back_populates="order",
        passive_deletes=True,
        cascade="all, delete-orphan",
    )
