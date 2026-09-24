from sqlalchemy.orm import Session
from sqlalchemy import select

from src.infrastructure.db.models import EstoqueUnidade, MovimentoEstoque, Produto, Unidade
from src.domain.enums import TipoMovimentoEstoque
from src.domain.entities import RecursoNaoEncontradoError, validar_estoque_suficiente


def obter_ou_criar_estoque(db: Session, unidade_id: int, produto_id: int) -> EstoqueUnidade:
    estoque = db.execute(
        select(EstoqueUnidade).where(
            EstoqueUnidade.unidade_id == unidade_id, EstoqueUnidade.produto_id == produto_id
        )
    ).scalar_one_or_none()
    if estoque is None:
        unidade = db.get(Unidade, unidade_id)
        produto = db.get(Produto, produto_id)
        if not unidade or not produto:
            raise RecursoNaoEncontradoError("Unidade ou produto inexistente.")
        estoque = EstoqueUnidade(unidade_id=unidade_id, produto_id=produto_id, quantidade=0, estoque_minimo=0)
        db.add(estoque)
        db.flush()
    return estoque


def consultar_saldo_unidade(db: Session, unidade_id: int) -> list[dict]:
    unidade = db.get(Unidade, unidade_id)
    if not unidade:
        raise RecursoNaoEncontradoError(f"Unidade {unidade_id} não encontrada.")

    registros = db.execute(select(EstoqueUnidade).where(EstoqueUnidade.unidade_id == unidade_id)).scalars().all()
    return [
        {
            "produtoId": r.produto_id,
            "produtoNome": r.produto.nome,
            "quantidade": r.quantidade,
            "estoqueMinimo": r.estoque_minimo,
        }
        for r in registros
    ]


def registrar_movimento(db: Session, unidade_id: int, produto_id: int, tipo: str,
                         quantidade: int, origem: str | None) -> MovimentoEstoque:
    estoque = obter_ou_criar_estoque(db, unidade_id, produto_id)
    tipo_enum = TipoMovimentoEstoque(tipo)

    if tipo_enum == TipoMovimentoEstoque.SAIDA:
        validar_estoque_suficiente(estoque.quantidade, quantidade)
        estoque.quantidade -= quantidade
    else:
        estoque.quantidade += quantidade

    movimento = MovimentoEstoque(
        estoque_id=estoque.id, tipo=tipo_enum, quantidade=quantidade, origem=origem
    )
    db.add(movimento)
    db.commit()
    db.refresh(movimento)
    return movimento


def reservar_itens_pedido(db: Session, unidade_id: int, itens: list[dict]) -> None:
    for item in itens:
        estoque = obter_ou_criar_estoque(db, unidade_id, item["produtoId"])
        validar_estoque_suficiente(estoque.quantidade, item["quantidade"])
        estoque.quantidade -= item["quantidade"]
        db.add(MovimentoEstoque(
            estoque_id=estoque.id,
            tipo=TipoMovimentoEstoque.SAIDA,
            quantidade=item["quantidade"],
            origem="PEDIDO",
        ))
