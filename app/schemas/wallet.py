from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class WalletOperation(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(gt=0)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        if value.as_tuple().exponent < -2:
            raise ValueError("Amount cannot have more than 2 decimal places")

        return value


class WalletResponse(BaseModel):
    id: str
    balance: Decimal