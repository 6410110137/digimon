from typing import AsyncIterator
from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine


from .item_models import *
from .users import *
from .exchange_model import *
from .transaction_model import *
from .wallet_model import *
from .merchant_model import *

connect_args = {}

engine = None

def init_db(settings):
    global engine

    engine = create_async_engine(
        settings.SQLDB_URL,
        future=True,
        connect_args=connect_args,
    )

async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def recreate_table():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]: 
    async_session = sessionmaker(
        engine, 
        class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

async def close_session():
    global engine
    if engine is None:
        raise Exception("DatabaseSessionManager is not initialized")
    await engine.dispose()