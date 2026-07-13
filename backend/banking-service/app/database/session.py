import random
import uuid
from collections.abc import AsyncGenerator
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.banking import (
    Account,
    Agency,
    Base,
    Beneficiary,
    Message,
    Product,
    Transaction,
    Transfer,
)

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_demo_data() -> None:
    async with async_session() as db:
        existing = await db.execute(select(Product).limit(1))
        if existing.scalar_one_or_none():
            return

        products = [
            Product(name="Compte Courant", category="account", description="Compte courant en dinars tunisiens",
                    features={"currency": "TND", "type": "checking"}),
            Product(name="Compte Épargne", category="account", description="Compte épargne avec intérêts",
                    features={"currency": "TND", "type": "savings"}),
            Product(name="Carte Visa Classic", category="card", description="Carte bancaire internationale",
                    features={"network": "Visa", "type": "debit"}),
            Product(name="Crédit à la Consommation", category="loan", description="Financement personnel",
                    features={"type": "consumer", "max_duration_months": 84}),
            Product(name="Crédit Immobilier", category="loan", description="Financement achat immobilier",
                    features={"type": "mortgage", "max_duration_months": 300}),
        ]
        agencies = [
            Agency(name="Agence Siège", address="31 Avenue de la Liberté", city="Tunis", phone="+216 71 181 000",
                   latitude=Decimal("36.8065"), longitude=Decimal("10.1815")),
            Agency(name="Agence Lac", address="Les Berges du Lac", city="Tunis", phone="+216 71 960 100",
                   latitude=Decimal("36.8380"), longitude=Decimal("10.2410")),
            Agency(name="Agence Sfax", address="Avenue Habib Bourguiba", city="Sfax", phone="+216 74 225 500",
                   latitude=Decimal("34.7406"), longitude=Decimal("10.7603")),
        ]
        db.add_all(products + agencies)
        await db.commit()


def generate_account_number() -> str:
    return f"TN59{''.join(str(random.randint(0, 9)) for _ in range(16))}"
