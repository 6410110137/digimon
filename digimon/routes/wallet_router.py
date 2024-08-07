from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from ..models.wallet_model import CreatedWallet, DBWallet, UpdatedWallet, Wallet
from contextlib import contextmanager
from typing import Optional, Annotated
from .. import models
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter(prefix="/wallets", tags=["wallet"])


@router.post("/{merchant_id}")
async def create_wallet(wallet: CreatedWallet, merchant_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]):
    db_wallet = DBWallet(**wallet.dict(), merchant_id=merchant_id)
    session.add(db_wallet)
    await session.commit()
    await session.refresh(db_wallet)
    return Wallet.from_orm(db_wallet)

@router.get("/{wallet_id}")
async def get_wallet(wallet_id: int,session: Annotated[AsyncSession, Depends(models.get_session)]):
    db_wallet = await session.get(DBWallet, wallet_id)
    if not db_wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return Wallet.from_orm(db_wallet)

@router.put("/{wallet_id}")
async def update_wallet(wallet_id: int, wallet: UpdatedWallet,session: Annotated[AsyncSession, Depends(models.get_session)]):
    db_wallet = await session.get(DBWallet, wallet_id)
    for key, value in wallet.dict(exclude_unset=True).items():
        setattr(db_wallet, key, value)
    session.add(db_wallet)
    await session.commit()
    await session.refresh(db_wallet)
    return Wallet.from_orm(db_wallet)

@router.delete("/{wallet_id}")
async def delete_wallet(wallet_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]):
    db_wallet = await session.get(DBWallet, wallet_id)
    await session.delete(db_wallet)
    await session.commit()
    return {"message": "Wallet deleted successfully"}