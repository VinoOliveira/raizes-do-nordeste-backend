import json
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.infrastructure.db.session import get_db
from src.infrastructure.db.models import Usuario, Pagamento
from src.application.services import pagamento_service
from src.api.schemas.pagamentos import PagamentoCreateRequest, PagamentoResponse
from src.api.deps import get_current_user
from src.domain.entities import RecursoNaoEncontradoError

router = APIRouter(prefix="/pagamentos", tags=["pagamentos"])


def _to_response(p: Pagamento) -> PagamentoResponse:
    return PagamentoResponse(
        pagamentoId=p.id, pedidoId=p.pedido_id,
        statusPagamento=p.status_pagamento.value, payload=json.loads(p.payload_mock),
    )


@router.post("", response_model=PagamentoResponse, status_code=status.HTTP_201_CREATED)
def solicitar(payload: PagamentoCreateRequest, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    pagamento = pagamento_service.solicitar_pagamento(db, usuario.id, payload.pedidoId, payload.formaPagamento)
    return _to_response(pagamento)


@router.get("/{pagamento_id}", response_model=PagamentoResponse)
def obter(pagamento_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    pagamento = db.get(Pagamento, pagamento_id)
    if not pagamento:
        raise RecursoNaoEncontradoError(f"Pagamento {pagamento_id} não encontrado.")
    return _to_response(pagamento)
