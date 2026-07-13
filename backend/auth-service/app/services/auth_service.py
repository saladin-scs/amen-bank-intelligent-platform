import secrets
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from amenbank_shared.security import create_access_token, hash_password, verify_password

from app.core.config import settings
from app.models.user import User
from app.repositories.user_repository import RefreshTokenRepository, UserRepository
from app.schemas.auth import TokenResponse, UserRegister, UserResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.users = UserRepository(db)
        self.tokens = RefreshTokenRepository(db)

    async def register(self, data: UserRegister) -> UserResponse:
        existing = await self.users.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
        )
        created = await self.users.create(user)
        return UserResponse(
            id=str(created.id),
            email=created.email,
            full_name=created.full_name,
            phone=created.phone,
            role=created.role,
            is_active=created.is_active,
        )

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
        return await self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        record = await self.tokens.get_valid(refresh_token)
        if not record:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        user = await self.users.get_by_id(record.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        await self.tokens.revoke(record)
        return await self._issue_tokens(user)

    async def get_user(self, user_id: str) -> UserResponse:
        user = await self.users.get_by_id(uuid.UUID(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
        )

    async def verify_token(self, token: str) -> dict:
        from amenbank_shared.security import decode_token

        payload = decode_token(token, settings.jwt_secret_key, settings.jwt_algorithm)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload

    async def _issue_tokens(self, user: User) -> TokenResponse:
        access = create_access_token(
            {"sub": str(user.id), "email": user.email, "role": user.role},
            settings.jwt_secret_key,
            settings.jwt_algorithm,
            settings.jwt_access_token_expire_minutes,
        )
        refresh = secrets.token_urlsafe(48)
        await self.tokens.create(user.id, refresh, settings.jwt_refresh_token_expire_days)
        return TokenResponse(access_token=access, refresh_token=refresh)
