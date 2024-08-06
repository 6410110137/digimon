from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from models.merchant_model import CreatedMerchant, DBMerchant, Merchant, MerchantList, UpdatedMerchant
from models import engine
from contextlib import contextmanager

router = APIRouter(prefix="/merchants", tags=["merchant"])

@contextmanager
def get_session():
    with Session(engine) as session:
        yield session

def get_db_merchant(session: Session, merchant_id: int):
    db_merchant = session.get(DBMerchant, merchant_id)
    if db_merchant is None:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return db_merchant

@router.post("")
async def create_merchant(merchant: CreatedMerchant):
    with get_session() as session:
        db_merchant = DBMerchant(**merchant.dict())
        session.add(db_merchant)
        session.commit()
        session.refresh(db_merchant)
    return Merchant.from_orm(db_merchant)

@router.get("")
async def get_merchants(page: int = 1, page_size: int = 10):
    with get_session() as session:
        db_merchants = session.exec(select(DBMerchant).offset((page - 1) * page_size).limit(page_size)).all()
    return MerchantList(merchants=db_merchants, page=page, page_size=page_size, size_per_page=len(db_merchants))

@router.get("/{merchant_id}")
async def get_merchant(merchant_id: int):
    with get_session() as session:
        return Merchant.from_orm(get_db_merchant(session, merchant_id))

@router.put("/{merchant_id}")
async def update_merchant(merchant_id: int, merchant: UpdatedMerchant):
    with get_session() as session:
        db_merchant = get_db_merchant(session, merchant_id)
        for key, value in merchant.dict(exclude_unset=True).items():
            setattr(db_merchant, key, value)
        session.add(db_merchant)
        session.commit()
        session.refresh(db_merchant)
    return Merchant.from_orm(db_merchant)

@router.delete("/{merchant_id}")
async def delete_merchant(merchant_id: int):
    with get_session() as session:
        db_merchant = get_db_merchant(session, merchant_id)
        session.delete(db_merchant)
        session.commit()
    return {"message": "Merchant deleted successfully"}