from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_session
from app.db.models import Wallet
from app.schemas.wallet import WalletOperation, WalletResponse


router = APIRouter(
    prefix="/api/v1/wallets",
    tags=["Wallets"],
)

@router.get(
    "/{wallet_id}",
    response_model=WalletResponse,
)
async def get_wallet(
    wallet_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    query = select(Wallet).where(Wallet.id == wallet_id)

    result = await session.execute(query)

    wallet = result.scalar_one_or_none()

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    return WalletResponse(
        id=str(wallet.id),
        balance=wallet.balance,
    )

@router.post(
    "/{wallet_id}/operation",
    response_model=WalletResponse,
)
async def wallet_operation(
    wallet_id: UUID,
    operation: WalletOperation,
    session: AsyncSession = Depends(get_session),
):
    async with session.begin():

        query = (
            select(Wallet)
            .where(Wallet.id == wallet_id)
            .with_for_update()
        )

        result = await session.execute(query)

        wallet = result.scalar_one_or_none()

        if wallet is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found",
            )

        if operation.operation_type == "DEPOSIT":
            wallet.balance += operation.amount

        elif operation.operation_type == "WITHDRAW":
            if wallet.balance < operation.amount:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Insufficient funds",
                )

            wallet.balance -= operation.amount

    return WalletResponse(
        id=str(wallet.id),
        balance=wallet.balance,
    )