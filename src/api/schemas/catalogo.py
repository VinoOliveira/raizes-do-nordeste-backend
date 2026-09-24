from decimal import Decimal
from pydantic import BaseModel, Field


class UnidadeResponse(BaseModel):
    id: int
    nome: str
    endereco: str | None = None
    cidadeUf: str | None = None
    ativo: bool


class ProdutoCreateRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    categoria: str | None = None
    preco: Decimal = Field(gt=0)


class ProdutoResponse(BaseModel):
    id: int
    nome: str
    categoria: str | None = None
    preco: Decimal
    ativo: bool
