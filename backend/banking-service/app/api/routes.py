from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.banking import (
    AccountResponse,
    AgencyResponse,
    BeneficiaryCreate,
    BeneficiaryResponse,
    MessageCreate,
    MessageResponse,
    ProductResponse,
    TransactionResponse,
    TransferCreate,
    TransferResponse,
)
from app.services.banking_service import BankingService

router = APIRouter(prefix="/banking", tags=["Banking"])


def get_service(db: AsyncSession = Depends(get_db)) -> BankingService:
    return BankingService(db)


def get_user_id(x_user_id: str = Header(...)) -> str:
    return x_user_id


@router.get("/accounts", response_model=list[AccountResponse])
async def list_accounts(user_id: str = Depends(get_user_id), service: BankingService = Depends(get_service)):
    return await service.list_accounts(user_id)


@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(account_id: str, user_id: str = Depends(get_user_id), service: BankingService = Depends(get_service)):
    return await service.get_account(user_id, account_id)


@router.get("/accounts/{account_id}/transactions", response_model=list[TransactionResponse])
async def list_transactions(account_id: str, user_id: str = Depends(get_user_id), service: BankingService = Depends(get_service)):
    return await service.list_transactions(user_id, account_id)


@router.post("/transfers", response_model=TransferResponse, status_code=201)
async def create_transfer(data: TransferCreate, user_id: str = Depends(get_user_id), service: BankingService = Depends(get_service)):
    return await service.create_transfer(user_id, data)


@router.get("/transfers", response_model=list[TransferResponse])
async def list_transfers(user_id: str = Depends(get_user_id), service: BankingService = Depends(get_service)):
    return await service.list_transfers(user_id)


@router.get("/beneficiaries", response_model=list[BeneficiaryResponse])
async def list_beneficiaries(user_id: str = Depends(get_user_id), service: BankingService = Depends(get_service)):
    return await service.list_beneficiaries(user_id)


@router.post("/beneficiaries", response_model=BeneficiaryResponse, status_code=201)
async def create_beneficiary(data: BeneficiaryCreate, user_id: str = Depends(get_user_id), service: BankingService = Depends(get_service)):
    return await service.create_beneficiary(user_id, data)


@router.get("/products", response_model=list[ProductResponse])
async def list_products(service: BankingService = Depends(get_service)):
    return await service.list_products()


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, service: BankingService = Depends(get_service)):
    return await service.get_product(product_id)


@router.get("/agencies", response_model=list[AgencyResponse])
async def list_agencies(service: BankingService = Depends(get_service)):
    return await service.list_agencies()


@router.get("/messages", response_model=list[MessageResponse])
async def list_messages(user_id: str = Depends(get_user_id), service: BankingService = Depends(get_service)):
    return await service.list_messages(user_id)


@router.post("/messages", response_model=MessageResponse, status_code=201)
async def create_message(data: MessageCreate, user_id: str = Depends(get_user_id), service: BankingService = Depends(get_service)):
    return await service.create_message(user_id, data)
