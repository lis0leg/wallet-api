import asyncio

import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.db.models import Wallet


@pytest.mark.asyncio
async def test_get_wallet(client, db_session):
    wallet = Wallet()

    db_session.add(wallet)
    await db_session.commit()

    response = await client.get(
        f"/api/v1/wallets/{wallet.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(wallet.id)
    assert Decimal(data["balance"]) == Decimal("0.00")


@pytest.mark.asyncio
async def test_get_nonexistent_wallet(client):
    wallet_id = uuid.uuid4()

    response = await client.get(
        f"/api/v1/wallets/{wallet_id}"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_deposit(client, db_session):
    wallet = Wallet()

    db_session.add(wallet)
    await db_session.commit()

    response = await client.post(
        f"/api/v1/wallets/{wallet.id}/operation",
        json={
            "operation_type": "DEPOSIT",
            "amount": 1000,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["balance"]) == Decimal("1000.00")


@pytest.mark.asyncio
async def test_withdraw(client, db_session):
    wallet = Wallet(balance=Decimal("1000.00"))

    db_session.add(wallet)
    await db_session.commit()

    response = await client.post(
        f"/api/v1/wallets/{wallet.id}/operation",
        json={
            "operation_type": "WITHDRAW",
            "amount": 300,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["balance"]) == Decimal("700.00")


@pytest.mark.asyncio
async def test_withdraw_insufficient_funds(client, db_session):
    wallet = Wallet(balance=Decimal("500.00"))

    db_session.add(wallet)
    await db_session.commit()

    response = await client.post(
        f"/api/v1/wallets/{wallet.id}/operation",
        json={
            "operation_type": "WITHDRAW",
            "amount": 1000,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Insufficient funds"


@pytest.mark.asyncio
async def test_concurrent_withdrawals(client, db_session):
    wallet = Wallet(balance=Decimal("1000.00"))

    db_session.add(wallet)
    await db_session.commit()

    async def withdraw():
        return await client.post(
            f"/api/v1/wallets/{wallet.id}/operation",
            json={
                "operation_type": "WITHDRAW",
                "amount": 700,
            },
        )

    response_1, response_2 = await asyncio.gather(
        withdraw(),
        withdraw(),
    )

    statuses = sorted([
        response_1.status_code,
        response_2.status_code,
    ])

    assert statuses == [200, 409]

    balance_response = await client.get(
        f"/api/v1/wallets/{wallet.id}"
    )

    assert balance_response.status_code == 200

    balance = Decimal(
        balance_response.json()["balance"]
    )

    assert balance == Decimal("300.00")
