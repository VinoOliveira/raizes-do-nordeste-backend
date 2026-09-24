from pydantic import BaseModel, Field


class SaldoEstoqueResponse(BaseModel):
    produtoId: int
    produtoNome: str
    quantidade: int
    estoqueMinimo: int


class MovimentoEstoqueRequest(BaseModel):
    unidadeId: int
    produtoId: int
    tipo: str = Field(pattern="^(ENTRADA|SAIDA)$")
    quantidade: int = Field(gt=0)
    origem: str | None = None


class MovimentoEstoqueResponse(BaseModel):
    id: int
    unidadeId: int
    produtoId: int
    tipo: str
    quantidade: int
    saldoAtual: int
