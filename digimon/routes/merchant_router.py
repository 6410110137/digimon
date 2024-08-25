from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from ..models.merchant_model import CreatedMerchant, DBMerchant, Merchant, MerchantList, UpdatedMerchant
from contextlib import contextmanager
from typing import Optional, Annotated
from .. import models
from .. import deps
from ..models import users
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter(prefix="/merchants", tags=["merchant"])

@router.post("")
async def create_merchant(
    merchant: CreatedMerchant, 
    current_user: Annotated[users, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]):
    db_merchant = DBMerchant.parse_obj(merchant)
    db_merchant.user = current_user
    session.add(db_merchant)
    await session.commit()
    await session.refresh(db_merchant)
    return Merchant.model_validate(db_merchant)


@router.get("")
async def get_merchants( session: Annotated[AsyncSession, Depends(models.get_session)], page: int = 1, page_size: int = 10,):
    result = await session.exec(select(DBMerchant).offset((page - 1) * page_size).limit(page_size))
    db_merchants = result.all()
    return MerchantList(merchants=db_merchants, page=page, page_size=page_size, size_per_page=len(db_merchants))

@router.get("/{merchant_id}")
async def get_merchant(merchant_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]):
    db_merchant = await session.get(DBMerchant, merchant_id)
    if not db_merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return Merchant.model_validate(db_merchant)


@router.put("/{merchant_id}")
async def update_merchant(
    merchant_id: int, merchant: UpdatedMerchant,
    # current_user: Annotated[models.users, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]):
    db_merchant = await session.get(DBMerchant, merchant_id)
    for key, value in merchant.dict(exclude_unset=True).items():
        setattr(db_merchant, key, value)
    session.add(db_merchant)
    await session.commit()
    await session.refresh(db_merchant)
    return Merchant.model_validate(db_merchant)


@router.delete("/{merchant_id}")
async def delete_merchant(
    merchant_id: int, 
    # current_user: Annotated[models.users, Depends(deps.get_current_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)]):
    db_merchant = await session.get(DBMerchant, merchant_id)
    await session.delete(db_merchant)
    await session.commit()
    return {"message": "Merchant deleted successfully"}