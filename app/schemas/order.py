"""
schemas/order.py
"""
import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from app.schemas.order_item import OrderItemCreate, OrderItemRead

OrderTitle = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=255,
    ),
]

OrderStatus = Literal["processing", "completed", "new", "canceled"]

Items = Annotated[
    list[OrderItemCreate],
    Field(min_length=1),
]


class OrderCreate(BaseModel):
    title: OrderTitle


class OrderCreateWithItems(BaseModel):
    title: OrderTitle
    items: Items


class OrderRead(BaseModel):
    id: int
    title: str
    status: OrderStatus
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class OrderWithItemsRead(OrderRead):
    items: list[OrderItemRead]


class OrderUpdate(BaseModel):
    title: Annotated[
        str | None,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=255,
        ),
    ] = None
    status: OrderStatus | None = None

    @field_validator("title", "status", mode="before")
    @classmethod
    def reject_null(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Field cannot be null")

        return value
