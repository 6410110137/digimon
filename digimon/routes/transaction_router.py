from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from models import engine
from models.item_models import DBItem
from models.transaction_model import CreatedTransaction, DBTransaction, Transaction, TransactionList
from models.wallet_model import DBWallet
from contextlib import contextmanager
from typing import Optional, Annotated
from .. import models
from sqlmodel.ext.asyncio.session import AsyncSession


router = APIRouter(prefix="/transactions", tags=["transaction"])

@contextmanager

async def get_db_transaction(session: Session, transaction_id: int):
    db_transaction =await session.get(DBTransaction, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@router.post("/{wallet_id}/{item_id}")
async def create_transaction(session: Annotated[AsyncSession, Depends(models.get_session)],transaction: CreatedTransaction, wallet_id: int, item_id: int):
        db_wallet = await session.get(DBWallet, wallet_id)
        db_item = await session.get(DBItem, item_id)
        if not db_wallet or not db_item:
            raise HTTPException(status_code=404, detail="Wallet or Item not found")

        balance = db_item.price * transaction.quantity
        if db_wallet.balance < balance:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        db_wallet.balance -= balance
        db_transaction = DBTransaction(**transaction.dict(), wallet_id=wallet_id, item_id=item_id, balance=balance)
        
        session.add(db_transaction)
        await session.commit()
        await session.refresh(db_transaction)
        return Transaction.from_orm(db_transaction)

@router.get("/{transaction_id}")
async def get_transaction(transaction_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]):
    return Transaction.from_orm(get_db_transaction(session, transaction_id))

@router.get("/wallet/{wallet_id}")
async def get_transactions(wallet_id: int , session: Annotated[AsyncSession, Depends(models.get_session)]):
    result = await session.exec(select(DBTransaction).where(DBTransaction.wallet_id == wallet_id))
    db_transactions = result.all()
    return TransactionList(transactions=db_transactions, page=1, page_size=len(db_transactions), size_per_page=len(db_transactions))

@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]):
    db_transaction = get_db_transaction(session, transaction_id)
    await session.delete(db_transaction)
    await session.commit()
    return {"message": "Transaction deleted successfully"}