from fastapi import APIRouter, Depends, Query, status as http_status
from sqlalchemy.orm import Session

from src.infrastructure.db.session import get_db
from src.application.services import pedido_service
from src.api.schemas.pedidos import (
    PedidoCreateRequest, PedidoResponse, ItemPedidoResponse,
    PedidoListResponse, PedidoListItem, AtualizarStatusRequest,
)
from src.api.deps import get_current_user, require_perfis
from src.infrastructure.db.models import Usuario, Pedido

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


def _to_response(pedido: Pedido) -> PedidoResponse:
    return PedidoResponse(
        pedidoId=pedido.id,
        canalPedido=pedido.canal_pedido.value,
        unidadeId=pedido.unidade_id,
        clienteId=pedido.cliente_id,
        status=pedido.status.value,
        total=pedido.total,
        itens=[ItemPedidoResponse(produtoId=i.produto_id, quantidade=i.quantidade, precoUnitario=i.preco_unitario) for i in pedido.itens],
        createdAt=pedido.created_at,
    )


@router.post("", response_model=PedidoResponse, status_code=http_status.HTTP_201_CREATED,
             dependencies=[Depends(require_perfis("CLIENTE", "ATENDENTE"))])
def criar(payload: PedidoCreateRequest, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    pedido = pedido_service.criar_pedido(
        db, usuario.id, payload.canalPedido, payload.unidadeId, payload.clienteId,
        [{"produtoId": i.produtoId, "quantidade": i.quantidade} for i in payload.itens],
    )
    return _to_response(pedido)


@router.get("", response_model=PedidoListResponse)
def listar(canalPedido: str | None = None, status: str | None = None,
           page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100),
           db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    itens, total = pedido_service.listar_pedidos(db, canalPedido, status, page, limit)
    return PedidoListResponse(
        page=page, limit=limit, total=total,
        items=[PedidoListItem(pedidoId=p.id, canalPedido=p.canal_pedido.value, status=p.status.value, total=p.total, createdAt=p.created_at) for p in itens],
    )


@router.get("/{pedido_id}", response_model=PedidoResponse)
def obter(pedido_id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return _to_response(pedido_service.obter_pedido(db, pedido_id))


@router.patch("/{pedido_id}/status", response_model=PedidoResponse,
              dependencies=[Depends(require_perfis("COZINHA", "ATENDENTE", "GERENTE"))])
def atualizar_status(pedido_id: int, payload: AtualizarStatusRequest, db: Session = Depends(get_db),
                      usuario: Usuario = Depends(get_current_user)):
    pedido = pedido_service.atualizar_status(db, usuario.id, pedido_id, payload.novoStatus)
    return _to_response(pedido)
