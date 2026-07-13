import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import generate_account_number
from app.models.banking import Account, Agency, Beneficiary, Message, Product, Transaction, Transfer
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


class BankingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_accounts(self, user_id: str) -> list[AccountResponse]:
        uid = uuid.UUID(user_id)
        result = await self.db.execute(select(Account).where(Account.user_id == uid))
        accounts = result.scalars().all()
        if not accounts:
            account = Account(
                user_id=uid,
                account_number=generate_account_number(),
                account_type="checking",
                balance=Decimal("5000.000"),
            )
            self.db.add(account)
            savings = Account(
                user_id=uid,
                account_number=generate_account_number(),
                account_type="savings",
                balance=Decimal("15000.000"),
            )
            self.db.add(savings)
            await self.db.commit()
            result = await self.db.execute(select(Account).where(Account.user_id == uid))
            accounts = result.scalars().all()
        return [self._account(a) for a in accounts]

    async def get_account(self, user_id: str, account_id: str) -> AccountResponse:
        account = await self._get_user_account(user_id, account_id)
        return self._account(account)

    async def list_transactions(self, user_id: str, account_id: str) -> list[TransactionResponse]:
        account = await self._get_user_account(user_id, account_id)
        result = await self.db.execute(
            select(Transaction).where(Transaction.account_id == account.id).order_by(Transaction.created_at.desc())
        )
        txs = result.scalars().all()
        if not txs:
            demo = [
                Transaction(account_id=account.id, type="credit", amount=Decimal("2500.000"),
                            description="Salaire", reference="SAL-001"),
                Transaction(account_id=account.id, type="debit", amount=Decimal("150.500"),
                            description="Paiement carte", reference="CRD-042"),
            ]
            self.db.add_all(demo)
            await self.db.commit()
            result = await self.db.execute(
                select(Transaction).where(Transaction.account_id == account.id).order_by(Transaction.created_at.desc())
            )
            txs = result.scalars().all()
        return [self._transaction(t) for t in txs]

    async def create_transfer(self, user_id: str, data: TransferCreate) -> TransferResponse:
        account = await self._get_user_account(user_id, data.from_account_id)
        if account.balance < data.amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
        account.balance -= data.amount
        transfer = Transfer(
            user_id=uuid.UUID(user_id),
            from_account_id=account.id,
            to_account_number=data.to_account_number,
            amount=data.amount,
            description=data.description,
            beneficiary_id=uuid.UUID(data.beneficiary_id) if data.beneficiary_id else None,
        )
        debit = Transaction(
            account_id=account.id, type="debit", amount=data.amount,
            description=f"Virement vers {data.to_account_number}", reference=f"TRF-{uuid.uuid4().hex[:8]}",
        )
        self.db.add_all([transfer, debit])
        await self.db.commit()
        await self.db.refresh(transfer)
        return self._transfer(transfer)

    async def list_transfers(self, user_id: str) -> list[TransferResponse]:
        result = await self.db.execute(
            select(Transfer).where(Transfer.user_id == uuid.UUID(user_id)).order_by(Transfer.created_at.desc())
        )
        return [self._transfer(t) for t in result.scalars().all()]

    async def list_beneficiaries(self, user_id: str) -> list[BeneficiaryResponse]:
        result = await self.db.execute(select(Beneficiary).where(Beneficiary.user_id == uuid.UUID(user_id)))
        return [self._beneficiary(b) for b in result.scalars().all()]

    async def create_beneficiary(self, user_id: str, data: BeneficiaryCreate) -> BeneficiaryResponse:
        b = Beneficiary(user_id=uuid.UUID(user_id), name=data.name, account_number=data.account_number,
                        bank_name=data.bank_name)
        self.db.add(b)
        await self.db.commit()
        await self.db.refresh(b)
        return self._beneficiary(b)

    async def list_products(self) -> list[ProductResponse]:
        result = await self.db.execute(select(Product).where(Product.is_active.is_(True)))
        return [self._product(p) for p in result.scalars().all()]

    async def get_product(self, product_id: str) -> ProductResponse:
        result = await self.db.execute(select(Product).where(Product.id == uuid.UUID(product_id)))
        p = result.scalar_one_or_none()
        if not p:
            raise HTTPException(status_code=404, detail="Product not found")
        return self._product(p)

    async def list_agencies(self) -> list[AgencyResponse]:
        result = await self.db.execute(select(Agency))
        return [self._agency(a) for a in result.scalars().all()]

    async def list_messages(self, user_id: str) -> list[MessageResponse]:
        result = await self.db.execute(
            select(Message).where(Message.user_id == uuid.UUID(user_id)).order_by(Message.created_at.desc())
        )
        return [self._message(m) for m in result.scalars().all()]

    async def create_message(self, user_id: str, data: MessageCreate) -> MessageResponse:
        m = Message(user_id=uuid.UUID(user_id), subject=data.subject, body=data.body)
        self.db.add(m)
        await self.db.commit()
        await self.db.refresh(m)
        return self._message(m)

    async def _get_user_account(self, user_id: str, account_id: str) -> Account:
        result = await self.db.execute(
            select(Account).where(Account.id == uuid.UUID(account_id), Account.user_id == uuid.UUID(user_id))
        )
        account = result.scalar_one_or_none()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account

    @staticmethod
    def _account(a: Account) -> AccountResponse:
        return AccountResponse(id=str(a.id), account_number=a.account_number, account_type=a.account_type,
                               currency=a.currency, balance=a.balance, status=a.status)

    @staticmethod
    def _transaction(t: Transaction) -> TransactionResponse:
        return TransactionResponse(id=str(t.id), account_id=str(t.account_id), type=t.type, amount=t.amount,
                                   description=t.description, reference=t.reference,
                                   created_at=t.created_at.isoformat())

    @staticmethod
    def _transfer(t: Transfer) -> TransferResponse:
        return TransferResponse(id=str(t.id), from_account_id=str(t.from_account_id),
                                to_account_number=t.to_account_number, amount=t.amount, status=t.status,
                                description=t.description, created_at=t.created_at.isoformat())

    @staticmethod
    def _beneficiary(b: Beneficiary) -> BeneficiaryResponse:
        return BeneficiaryResponse(id=str(b.id), name=b.name, account_number=b.account_number, bank_name=b.bank_name)

    @staticmethod
    def _product(p: Product) -> ProductResponse:
        return ProductResponse(id=str(p.id), name=p.name, category=p.category, description=p.description,
                               features=p.features)

    @staticmethod
    def _agency(a: Agency) -> AgencyResponse:
        return AgencyResponse(id=str(a.id), name=a.name, address=a.address, city=a.city, phone=a.phone)

    @staticmethod
    def _message(m: Message) -> MessageResponse:
        return MessageResponse(id=str(m.id), subject=m.subject, body=m.body, status=m.status,
                               created_at=m.created_at.isoformat())
