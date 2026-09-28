from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.infrastructure.db.session import get_db
from src.infrastructure.db.models import Usuario
from src.application.services import fidelidade_service
from src.api.schemas.pagamentos import FidelidadeSaldoResponse, FidelidadeResgateRequest, FidelidadeResgateResponse
from src.api.deps import get_current_user

router = APIRouter(prefix="/fidelidade", tags=["fidelidade"])


@router.get("/{cliente_id}/saldo", response_model=FidelidadeSaldoResponse)
def saldo(cliente_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    cliente = fidelidade_service.consultar_saldo(db, cliente_id)
    return FidelidadeSaldoResponse(clienteId=cliente.id, pontosFidelidade=cliente.pontos_fidelidade)


@router.post("/{cliente_id}/resgatar", response_model=FidelidadeResgateResponse)
def resgatar(cliente_id: int, payload: FidelidadeResgateRequest, db: Session = Depends(get_db),
             usuario: Usuario = Depends(get_current_user)):
    cliente = fidelidade_service.resgatar_pontos(db, cliente_id, payload.pontos)
    return FidelidadeResgateResponse(clienteId=cliente.id, pontosResgatados=payload.pontos, saldoRestante=cliente.pontos_fidelidade)
