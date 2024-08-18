from fastapi import APIRouter, Depends, HTTPException

from digimon.models.exchange_model import EXCHANGE_RATES, BaseExchange, Currency

from sqlmodel.ext.asyncio.session import AsyncSession
from digimon.models.wallet_model import DBWallet

from .. import models

router = APIRouter(prefix="/exchange", tags=["exchange"])

@router.post("/{exchange}")
async def exchange_money(
    wallet_id: int,
    request:BaseExchange,
    session: AsyncSession = Depends(models.get_session)):

    wallet = await session.get(DBWallet, wallet_id)
    if not wallet:
        raise HTTPException(
            status_code=404,
            detail="Not found this wallet",
        )
    if request.from_currency == request.to_currency:
        raise HTTPException(
            status_code=400,
            detail="from_currency and to_currency are the same",
        )
    if request.from_currency == Currency.THB:
        thb_amount = request.amount
        rate = EXCHANGE_RATES[request.to_currency]
        to_amount = thb_amount / rate
    else:
        rate = EXCHANGE_RATES[request.from_currency]
        thb_amount = request.amount * rate

        if request.to_currency == Currency.THB:
            to_amount = thb_amount
        else:
            to_rate = EXCHANGE_RATES[request.to_currency]
            to_amount = thb_amount / to_rate

    rate = EXCHANGE_RATES[request.to_currency]
    to_amount = request.amount / rate

    if wallet.balance < thb_amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    wallet.balance -= thb_amount

    session.add(wallet)
    await session.commit()
    await session.refresh(wallet)

    return {
        "from_currency": request.from_currency,
        "to_currency": request.to_currency,
        "original_amount": request.amount,
        "exchanged_amount": to_amount,
        "thb_equivalent": thb_amount,
        "wallet_balance": wallet.balance
    }