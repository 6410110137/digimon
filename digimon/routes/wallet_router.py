from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from models import engine
from models.wallet_model import CreatedWallet, DBWallet, UpdatedWallet, Wallet
from contextlib import contextmanager

router = APIRouter(prefix="/wallets", tags=["wallet"])

@contextmanager
def get_session():
    with Session(engine) as session:
        yield session

def get_db_wallet(session: Session, wallet_id: int):
    db_wallet = session.get(DBWallet, wallet_id)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return db_wallet

@router.post("/{merchant_id}")
async def create_wallet(wallet: CreatedWallet, merchant_id: int):
    with get_session() as session:
        db_wallet = DBWallet(**wallet.dict(), merchant_id=merchant_id)
        session.add(db_wallet)
        session.commit()
        session.refresh(db_wallet)
    return Wallet.from_orm(db_wallet)

@router.get("/{wallet_id}")
async def get_wallet(wallet_id: int):
    with get_session() as session:
        return Wallet.from_orm(get_db_wallet(session, wallet_id))

@router.put("/{wallet_id}")
async def update_wallet(wallet_id: int, wallet: UpdatedWallet):
    with get_session() as session:
        db_wallet = get_db_wallet(session, wallet_id)
        for key, value in wallet.dict(exclude_unset=True).items():
            setattr(db_wallet, key, value)
        session.add(db_wallet)
        session.commit()
        session.refresh(db_wallet)
    return Wallet.from_orm(db_wallet)

@router.delete("/{wallet_id}")
async def delete_wallet(wallet_id: int):
    with get_session() as session:
        db_wallet = get_db_wallet(session, wallet_id)
        session.delete(db_wallet)
        session.commit()
    return {"message": "Wallet deleted successfully"}