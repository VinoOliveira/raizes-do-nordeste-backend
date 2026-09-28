from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.infrastructure.db.session import get_db
from src.application.services import auth_service
from src.api.schemas.usuarios import UsuarioCreateRequest, UsuarioResponse
from src.api.deps import get_current_user
from src.infrastructure.db.models import Usuario

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def _to_response(usuario: Usuario) -> UsuarioResponse:
    return UsuarioResponse(
        id=usuario.id, nome=usuario.nome, email=usuario.email,
        perfil=usuario.perfil.value, consentimentoLGPD=usuario.consentimento_lgpd,
    )


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def cadastrar(payload: UsuarioCreateRequest, db: Session = Depends(get_db)):
    usuario = auth_service.registrar_usuario(
        db, payload.nome, payload.email, payload.senha, payload.telefone, payload.consentimentoLGPD
    )
    return _to_response(usuario)


@router.get("/me", response_model=UsuarioResponse)
def me(usuario: Usuario = Depends(get_current_user)):
    return _to_response(usuario)
