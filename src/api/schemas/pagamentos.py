from pydantic import BaseModel


class PagamentoCreateRequest(BaseModel):
    pedidoId: int
    formaPagamento: str = "MOCK"


class PagamentoResponse(BaseModel):
    pagamentoId: int
    pedidoId: int
    statusPagamento: str
    payload: dict


class FidelidadeSaldoResponse(BaseModel):
    clienteId: int
    pontosFidelidade: int


class FidelidadeResgateRequest(BaseModel):
    pontos: int


class FidelidadeResgateResponse(BaseModel):
    clienteId: int
    pontosResgatados: int
    saldoRestante: int
