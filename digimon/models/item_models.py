from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select, Relationship
from . import users

if TYPE_CHECKING:
    from .merchant_model import DBMerchant
    from .transaction_model import DBTransaction

class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    price: float = 0.12
    tax: float | None = None
    user_id: int | None = 1
    merchant_id: int | None


class CreatedItem(BaseItem):
    pass


class UpdatedItem(BaseItem):
    pass


class Item(BaseItem):
    id: int

class DBItem(Item, SQLModel, table=True):
    __tablename__ = "items"
    id: Optional[int] = Field(default=None, primary_key=True)

    merchant_id: Optional[int] = Field(default=None, foreign_key="merchants.id")
    merchant: Optional["DBMerchant"] = Relationship(back_populates="items")

    transactions: list["DBTransaction"] = Relationship(back_populates="item")

    user_id: int = Field(default=None, foreign_key="users.id")
    user: users.DBUser | None = Relationship()

class ItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[Item]
    page: int
    page_count: int
    size_per_page: int