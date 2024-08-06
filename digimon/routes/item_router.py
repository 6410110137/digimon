from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from models import engine
from models.item_models import CreatedItem, DBItem, Item, ItemList, UpdatedItem
from contextlib import contextmanager

router = APIRouter(prefix="/items", tags=["item"])

@contextmanager
def get_session():
    with Session(engine) as session:
        yield session

def get_db_item(session: Session, item_id: int):
    db_item = session.get(DBItem, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.post("/{merchant_id}")
async def create_item(item: CreatedItem, merchant_id: int):
    with get_session() as session:
        db_item = DBItem(**item.dict(), merchant_id=merchant_id)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
    return Item.from_orm(db_item)

@router.get("")
async def get_items(page: int = 1, page_size: int = 10):
    with get_session() as session:
        db_items = session.exec(select(DBItem).offset((page - 1) * page_size).limit(page_size)).all()
    return ItemList(items=db_items, page=page, page_size=page_size, size_per_page=len(db_items))

@router.get("/{item_id}")
async def get_item(item_id: int):
    with get_session() as session:
        return Item.from_orm(get_db_item(session, item_id))

@router.put("/{item_id}")
async def update_item(item_id: int, item: UpdatedItem):
    with get_session() as session:
        db_item = get_db_item(session, item_id)
        for key, value in item.dict(exclude_unset=True).items():
            setattr(db_item, key, value)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
    return Item.from_orm(db_item)

@router.delete("/{item_id}")
async def delete_item(item_id: int):
    with get_session() as session:
        db_item = get_db_item(session, item_id)
        session.delete(db_item)
        session.commit()
    return {"message": "Item deleted successfully"}