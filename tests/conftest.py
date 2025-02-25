import sys
import os

from sqlmodel import select

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport


from pydantic_settings import SettingsConfigDict



from digimon import models, config, main, security
import pytest
import pytest_asyncio

import pathlib
import datetime

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

SettingsTesting = config.Settings
SettingsTesting.model_config = SettingsConfigDict(
    env_file=".testing.env", validate_assignment=True, extra="allow"
)


@pytest.fixture(name="app", scope="session")
def app_fixture():
    settings = SettingsTesting()
    path = pathlib.Path("test-data")
    if not path.exists():
        path.mkdir()

    app = main.create_app(settings)

    asyncio.run(models.create_all())

    yield app


@pytest.fixture(name="client", scope="session")
def client_fixture(app: FastAPI) -> AsyncClient:

    # client = TestClient(app)
    # yield client
    # app.dependency_overrides.clear()
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost")


@pytest_asyncio.fixture(name="session", scope="session")
async def get_session() -> models.AsyncIterator[models.AsyncSession]:
    settings = SettingsTesting()
    models.init_db(settings)

    async_session = models.sessionmaker(
        models.engine, class_=models.AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(name="user1")
async def example_user1(session: models.AsyncSession) -> models.DBUser:
    password = "123456"
    username = "user1"

    query = await session.exec(
        select(models.DBUser).where(models.DBUser.username == username).limit(1)
    )
    user = query.one_or_none()
    if user:
        return user

    user = models.DBUser(
        username=username,
        password = password,
        email="test@test.com",
        first_name="Firstname",
        last_name="lastname",
        last_login_date=datetime.datetime.now(tz=datetime.timezone.utc),
        
        role="merchants"
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture(name="token_user1")
async def oauth_token_user1(user1: models.DBUser) -> models.Token:
    settings = SettingsTesting()
    access_token_expires = datetime.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    user = user1
    return models.Token(
        user_id=user.id, 
        access_token=security.create_access_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        ),
        refresh_token=security.create_refresh_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        ),
        token_type="Bearer",
        scope="",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expires_at=datetime.datetime.now() + access_token_expires,
        issued_at=user1.last_login_date,   
    )


@pytest_asyncio.fixture(name="merchant_user1")
async def example_merchant_user1(
    session: models.AsyncSession, user1: models.DBUser
) -> models.DBMerchant:
    name = "merchant1"

    query = await session.exec(
        select(models.DBMerchant)
        .where(models.DBMerchant.name == name)
        .limit(1)
    )
    merchant = query.one_or_none()
    if merchant:
        return merchant

    merchant = models.DBMerchant(
        name=name, user=user1, decription="Merchant Description"
    )

    session.add(merchant)
    await session.commit()
    await session.refresh(merchant)
    return merchant