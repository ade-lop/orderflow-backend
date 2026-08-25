"""/schemas/order_item.py"""
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

ProductName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=400,
    )
]

Quantity = Annotated[
    int,
    Field(gt=0),
]

UnitPrice = Annotated[
    Decimal,
    Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
]


class OrderItemCreate(BaseModel):
    product_name: ProductName
    quantity: Quantity
    unit_price: UnitPrice


class OrderItemRead(BaseModel):
    id: int
    order_id: int
    product_name: ProductName
    quantity: Quantity
    unit_price: UnitPrice

    model_config = ConfigDict(
        from_attributes=True,
    )
