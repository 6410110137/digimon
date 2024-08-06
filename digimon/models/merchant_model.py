from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, Relationship, SQLModel

class BaseMerchant(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    tax_id: str

class CreatedMerchant(BaseMerchant):
    pass

class UpdatedMerchant(BaseMerchant):
    pass

class Merchant(BaseMerchant):
    id: int

class DBMerchant(Merchant, SQLModel, table=True):
    __tablename__ = "merchants"
    id: Optional[int] = Field(default=None, primary_key=True)

    items: list["DBItem"] = Relationship(back_populates="merchant", cascade_delete=True)
    wallet: Optional["DBWallet"] = Relationship(
        back_populates="merchant", cascade_delete=True
    )

class MerchantList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    merchants: list[Merchant]
    page: int
    page_size: int
    size_per_page: int

if TYPE_CHECKING:
    from models.item_models import DBItem
    from models.wallet_model import DBWallet