from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.auth import RefreshRequest, TokenResponse, UserLogin, UserRegister, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserRegister, service: AuthService = Depends(get_auth_service)):
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, service: AuthService = Depends(get_auth_service)):
    return await service.login(data.email, data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, service: AuthService = Depends(get_auth_service)):
    return await service.refresh(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(authorization: str = Header(...), service: AuthService = Depends(get_auth_service)):
    token = authorization.replace("Bearer ", "")
    payload = await service.verify_token(token)
    return await service.get_user(payload["sub"])


@router.post("/verify")
async def verify(authorization: str = Header(...), service: AuthService = Depends(get_auth_service)):
    token = authorization.replace("Bearer ", "")
    payload = await service.verify_token(token)
    return {"valid": True, "user_id": payload["sub"], "role": payload.get("role")}
