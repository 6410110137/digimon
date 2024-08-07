from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, Relationship, SQLModel

class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    balance: float = 0.0


class CreatedWallet(BaseWallet):
    pass


class UpdatedWallet(BaseWallet):
    pass

class Wallet(BaseWallet):
    id: int

class DBWallet(Wallet, SQLModel, table=True):
    __tablename__ = "wallets"
    id: Optional[int] = Field(default=None, primary_key=True)

    merchant_id: Optional[int] = Field(default=None, foreign_key="merchants.id")
    merchant: Optional["DBMerchant"] = Relationship(back_populates="wallet")

    transactions: list["DBTransaction"] = Relationship(back_populates="wallet")

if TYPE_CHECKING:
    from .merchant_model import DBMerchant
    from .transaction_model import DBTransaction