from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from src.config import settings


class TokenInvalidoError(Exception):
    pass


def criar_access_token(subject: str, perfil: str, extra_expires_minutes: int | None = None) -> str:
    expira_em = datetime.now(timezone.utc) + timedelta(
        minutes=extra_expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "perfil": perfil, "type": "access", "exp": expira_em}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise TokenInvalidoError("Token inválido ou expirado.")
