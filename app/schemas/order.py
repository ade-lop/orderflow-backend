"""
schemas/order.py
"""
import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

OrderTitle = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=255,
    ),
]

OrderStatus = Literal["processing", "completed", "new", "canceled"]


class OrderCreate(BaseModel):
    title: OrderTitle


class OrderRead(BaseModel):
    id: int
    title: str
    status: OrderStatus
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


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
