from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.infrastructure.db.session import get_db
from src.infrastructure.db.models import Usuario
from src.infrastructure.security.jwt import decodificar_token, TokenInvalidoError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado.")
    try:
        payload = decodificar_token(token)
    except TokenInvalidoError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")
    usuario = db.get(Usuario, int(payload["sub"]))
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado.")
    return usuario


def require_perfis(*perfis: str):
    def checker(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.perfil.value not in perfis:
            raise HTTPException(status_code=403, detail="Sem permissão para este recurso.")
        return usuario
    return checker
