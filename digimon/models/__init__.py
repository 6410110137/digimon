from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession


connect_args = {}

engine = create_engine(
    "postgresql+pg8000://postgres:241241@localhost/digimondb",
    connect_args=connect_args,
)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


def init_db():
    SQLModel.metadata.create_all(engine)

async def get_session() -> AsyncSession:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session