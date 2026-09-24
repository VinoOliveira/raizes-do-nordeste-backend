from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from src.domain.enums import CanalPedido, StatusPedido


class ItemPedidoRequest(BaseModel):
    produtoId: int
    quantidade: int = Field(gt=0)


class PedidoCreateRequest(BaseModel):
    canalPedido: CanalPedido
    unidadeId: int
    clienteId: int
    itens: list[ItemPedidoRequest] = Field(min_length=1)
    formaPagamento: str = "MOCK"


class ItemPedidoResponse(BaseModel):
    produtoId: int
    quantidade: int
    precoUnitario: Decimal


class PedidoResponse(BaseModel):
    pedidoId: int
    canalPedido: str
    unidadeId: int
    clienteId: int
    status: str
    total: Decimal
    itens: list[ItemPedidoResponse]
    createdAt: datetime


class PedidoListItem(BaseModel):
    pedidoId: int
    canalPedido: str
    status: str
    total: Decimal
    createdAt: datetime


class PedidoListResponse(BaseModel):
    page: int
    limit: int
    total: int
    items: list[PedidoListItem]


class AtualizarStatusRequest(BaseModel):
    novoStatus: StatusPedido
