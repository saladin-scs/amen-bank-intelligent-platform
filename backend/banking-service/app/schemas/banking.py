from decimal import Decimal

from pydantic import BaseModel, Field


class AccountResponse(BaseModel):
    id: str
    account_number: str
    account_type: str
    currency: str
    balance: Decimal
    status: str

    model_config = {"from_attributes": True}


class TransactionResponse(BaseModel):
    id: str
    account_id: str
    type: str
    amount: Decimal
    description: str | None
    reference: str | None
    created_at: str

    model_config = {"from_attributes": True}


class TransferCreate(BaseModel):
    from_account_id: str
    to_account_number: str
    amount: Decimal = Field(gt=0)
    description: str | None = None
    beneficiary_id: str | None = None


class TransferResponse(BaseModel):
    id: str
    from_account_id: str
    to_account_number: str
    amount: Decimal
    status: str
    description: str | None
    created_at: str

    model_config = {"from_attributes": True}


class BeneficiaryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    account_number: str = Field(min_length=10, max_length=20)
    bank_name: str | None = None


class BeneficiaryResponse(BaseModel):
    id: str
    name: str
    account_number: str
    bank_name: str | None

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id: str
    name: str
    category: str
    description: str | None
    features: dict | None

    model_config = {"from_attributes": True}


class AgencyResponse(BaseModel):
    id: str
    name: str
    address: str | None
    city: str | None
    phone: str | None

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=255)
    body: str = Field(min_length=5)


class MessageResponse(BaseModel):
    id: str
    subject: str
    body: str
    status: str
    created_at: str

    model_config = {"from_attributes": True}
