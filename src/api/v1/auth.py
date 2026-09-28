from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.infrastructure.db.session import get_db
from src.application.services import auth_service
from src.api.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    usuario = auth_service.autenticar(db, payload.email, payload.senha)
    return auth_service.gerar_token_response(usuario)
