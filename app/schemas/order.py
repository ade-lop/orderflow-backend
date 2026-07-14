import datetime

from pydantic import BaseModel, ConfigDict


class OrderCreate(BaseModel):
    title: str


class OrderRead(BaseModel):
    id: int
    title: str
    status: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
