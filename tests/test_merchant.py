from httpx import AsyncClient

import pytest

from digimon.models.merchant_model import DBMerchant
from digimon.models.users import DBUser, Token


@pytest.mark.asyncio
async def test_no_permission_create_merchants(
    client: AsyncClient, user1: DBUser
):
    payload = {"name": "merchants"}
    response = await client.post("/merchants", json=payload)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_merchants(client: AsyncClient, token_user1: Token):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {"name": "merchants",}
    response = await client.post("/merchants", json=payload, headers=headers)

    data = response.json()

    assert response.status_code == 200
    assert data["name"] == payload["name"]


@pytest.mark.asyncio
async def test_merchants(client: AsyncClient, merchant_user1: DBMerchant):
    response = await client.get("/merchants")

    data = response.json()
    assert response.status_code == 200
    assert len(data["merchants"]) > 0
    check_merchant = None

    for merchant in data["merchants"]:
        if merchant["name"] == merchant_user1.name:
            check_merchant = merchant
            break

    assert check_merchant["name"] == merchant_user1.name