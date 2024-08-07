from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from models.merchant_model import CreatedMerchant, DBMerchant, Merchant, MerchantList, UpdatedMerchant
from models import engine
from contextlib import contextmanager
from typing import Optional, Annotated
from .. import models
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter(prefix="/merchants", tags=["merchant"])

@contextmanager
async def get_db_merchant(session: AsyncSession, merchant_id: int):
    db_merchant = await session.get(DBMerchant, merchant_id)
    if db_merchant is None:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return db_merchant

@router.post("")
async def create_merchant(merchant: CreatedMerchant, session: Annotated[AsyncSession, Depends(models.get_session)]):
    db_merchant = DBMerchant(**merchant.dict())
    session.add(db_merchant)
    await session.commit()
    await session.refresh(db_merchant)
    return Merchant.from_orm(db_merchant)

@router.get("")
async def get_merchants( session: Annotated[AsyncSession, Depends(models.get_session)], page: int = 1, page_size: int = 10,):
    result = await session.exec(select(DBMerchant).offset((page - 1) * page_size).limit(page_size))
    db_merchants = result.all()
    return MerchantList(merchants=db_merchants, page=page, page_size=page_size, size_per_page=len(db_merchants))

@router.get("/{merchant_id}")
async def get_merchant(merchant_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]):
    return Merchant.from_orm(get_db_merchant(session, merchant_id))

@router.put("/{merchant_id}")
async def update_merchant(merchant_id: int, merchant: UpdatedMerchant,session: Annotated[AsyncSession, Depends(models.get_session)]):
    db_merchant = get_db_merchant(session, merchant_id)
    for key, value in merchant.dict(exclude_unset=True).items():
        setattr(db_merchant, key, value)
    session.add(db_merchant)
    await session.commit()
    await session.refresh(db_merchant)
    return Merchant.from_orm(db_merchant)

@router.delete("/{merchant_id}")
async def delete_merchant(merchant_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]):
    db_merchant = get_db_merchant(session, merchant_id)
    await session.delete(db_merchant)
    await session.commit()
    return {"message": "Merchant deleted successfully"}