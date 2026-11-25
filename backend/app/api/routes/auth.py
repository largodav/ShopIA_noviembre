import hmac

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core.auth import create_access_token, verify_access_token
from app.core.config import settings

router = APIRouter()
_optional_bearer = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(payload: LoginRequest) -> dict:
    """Autenticación sencilla de usuario único con token de larga duración."""
    if not settings.auth_enabled:
        token, exp = create_access_token(settings.auth_username)
        return {
            "access_token": token,
            "token_type": "bearer",
            "username": settings.auth_username,
            "expires_at": exp,
        }

    user_ok = hmac.compare_digest(payload.username.strip(), settings.auth_username)
    pass_ok = hmac.compare_digest(payload.password, settings.auth_password)
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
        )

    token, exp = create_access_token(settings.auth_username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": settings.auth_username,
        "expires_at": exp,
    }


@router.get("/status")
async def auth_status(
    credentials: HTTPAuthorizationCredentials | None = Depends(_optional_bearer),
) -> dict:
    if not settings.auth_enabled:
        return {
            "auth_enabled": False,
            "authenticated": True,
            "username": settings.auth_username,
        }
    payload = verify_access_token(credentials.credentials) if credentials else None
    return {
        "auth_enabled": True,
        "authenticated": payload is not None,
        "username": payload["sub"] if payload else None,
    }
