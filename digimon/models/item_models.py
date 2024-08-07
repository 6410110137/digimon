from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, create_engine, Session, select, Relationship

if TYPE_CHECKING:
    from models.merchant_model import DBMerchant
    from models.transaction_model import DBTransaction

class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    price: float = 0.12
    tax: float | None = None


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

class ItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[Item]
    page: int
    page_size: int
    size_per_page: int