from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.infrastructure.db.session import get_db
from src.infrastructure.db.models import Produto
from src.api.schemas.catalogo import ProdutoCreateRequest, ProdutoResponse
from src.api.deps import require_perfis
from src.domain.entities import RecursoNaoEncontradoError

router = APIRouter(prefix="/produtos", tags=["produtos"])


def _to_response(p: Produto) -> ProdutoResponse:
    return ProdutoResponse(id=p.id, nome=p.nome, categoria=p.categoria, preco=p.preco, ativo=p.ativo)


@router.get("", response_model=list[ProdutoResponse])
def listar(db: Session = Depends(get_db)):
    produtos = db.execute(select(Produto).where(Produto.ativo == True)).scalars().all()
    return [_to_response(p) for p in produtos]


@router.post("", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_perfis("GERENTE"))])
def criar(payload: ProdutoCreateRequest, db: Session = Depends(get_db)):
    produto = Produto(nome=payload.nome, categoria=payload.categoria, preco=payload.preco)
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return _to_response(produto)


@router.get("/{produto_id}", response_model=ProdutoResponse)
def obter(produto_id: int, db: Session = Depends(get_db)):
    produto = db.get(Produto, produto_id)
    if not produto:
        raise RecursoNaoEncontradoError(f"Produto {produto_id} não encontrado.")
    return _to_response(produto)


@router.put("/{produto_id}", response_model=ProdutoResponse, dependencies=[Depends(require_perfis("GERENTE"))])
def atualizar(produto_id: int, payload: ProdutoCreateRequest, db: Session = Depends(get_db)):
    produto = db.get(Produto, produto_id)
    if not produto:
        raise RecursoNaoEncontradoError(f"Produto {produto_id} não encontrado.")
    produto.nome = payload.nome
    produto.categoria = payload.categoria
    produto.preco = payload.preco
    db.commit()
    db.refresh(produto)
    return _to_response(produto)


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_perfis("GERENTE"))])
def remover(produto_id: int, db: Session = Depends(get_db)):
    produto = db.get(Produto, produto_id)
    if not produto:
        raise RecursoNaoEncontradoError(f"Produto {produto_id} não encontrado.")
    produto.ativo = False
    db.commit()
