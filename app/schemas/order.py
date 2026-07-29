import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, field_validator


class OrderCreate(BaseModel):
    title: str


class OrderRead(BaseModel):
    id: int
    title: str
    status: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


OrderStatus = Literal["processing", "completed", "new", "canceled"]


class OrderUpdate(BaseModel):
    title: str | None = None
    status: OrderStatus | None = None

    @field_validator("title", "status", mode="before")
    @classmethod
    def reject_null(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Field cannot be null")

        return value
