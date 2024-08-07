from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import Optional, Annotated
from .. import models

from sqlmodel.ext.asyncio.session import AsyncSession
from models import engine
from models.item_models import CreatedItem, DBItem, Item, ItemList, UpdatedItem
from contextlib import contextmanager

router = APIRouter(prefix="/items", tags=["item"])

@router.post("/{merchant_id}")
async def create_item(
    item: models.CreatedItem,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Item | None:
    data = item.dict()
    dbitem = models.DBItem(**data)
    session.add(dbitem)
    await session.commit()
    await session.refresh(dbitem)

    return models.Item.from_orm(dbitem)

@router.get("")
async def get_items(
    session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.ItemList:
    result = await session.exec(select(models.DBItem))
    items = result.all()
    return models.ItemList.from_orm(
        dict(items=items, page_size=0, page=0, size_per_page=0)
    )


@router.get("/{item_id}")
async def get_item(
    item_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.Item:
    db_item = await session.get(DBItem, item_id)
    if db_item:
        return models.Item.from_orm(db_item)

    raise HTTPException(status_code=404, detail="Item not found")


@router.put("/{item_id}")
async def update_item(
    item_id: int,
    item: models.UpdatedItem,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.Item:
    print("update_item", item)
    data = item.dict()
    db_item = await session.get(DBItem, item_id)
    db_item.sqlmodel_update(data)
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)

    return models.Item.from_orm(db_item)

@router.delete("/{item_id}")
async def delete_item(
    item_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]
) -> dict:
    db_item = await session.get(DBItem, item_id)
    await session.delete(db_item)
    await session.commit()

    return dict(message="delete success")