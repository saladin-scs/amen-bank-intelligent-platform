import hashlib
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RefreshToken, User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: uuid.UUID, token: str, expires_days: int) -> RefreshToken:
        record = RefreshToken(
            user_id=user_id,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            expires_at=datetime.now(UTC) + timedelta(days=expires_days),
        )
        self.db.add(record)
        await self.db.commit()
        return record

    async def get_valid(self, token: str) -> RefreshToken | None:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked.is_(False),
                RefreshToken.expires_at > datetime.now(UTC),
            )
        )
        return result.scalar_one_or_none()

    async def revoke(self, record: RefreshToken) -> None:
        record.revoked = True
        await self.db.commit()
