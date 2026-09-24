from sqlalchemy.orm import Session
from sqlalchemy import select, func

from src.infrastructure.db.models import Pedido, ItemPedido, Produto, Unidade, Cliente
from src.infrastructure.logging.auditoria import registrar_log
from src.application.services.estoque_service import reservar_itens_pedido
from src.domain.enums import StatusPedido, CanalPedido
from src.domain.entities import (
    RecursoNaoEncontradoError, calcular_total_pedido, validar_transicao_status,
)


def criar_pedido(db: Session, usuario_id: int, canal_pedido: CanalPedido, unidade_id: int,
                  cliente_id: int, itens_request: list[dict]) -> Pedido:
    unidade = db.get(Unidade, unidade_id)
    if not unidade or not unidade.ativo:
        raise RecursoNaoEncontradoError(f"Unidade {unidade_id} não encontrada ou inativa.")

    cliente = db.get(Cliente, cliente_id)
    if not cliente:
        raise RecursoNaoEncontradoError(f"Cliente {cliente_id} não encontrado.")

    itens_processados = []
    for item in itens_request:
        produto = db.get(Produto, item["produtoId"])
        if not produto or not produto.ativo:
            raise RecursoNaoEncontradoError(f"Produto {item['produtoId']} não encontrado ou inativo.")
        itens_processados.append({
            "produtoId": produto.id,
            "quantidade": item["quantidade"],
            "preco_unitario": produto.preco,
        })

    reservar_itens_pedido(db, unidade_id, [
        {"produtoId": i["produtoId"], "quantidade": i["quantidade"]} for i in itens_processados
    ])

    total = calcular_total_pedido([
        {"quantidade": i["quantidade"], "preco_unitario": i["preco_unitario"]} for i in itens_processados
    ])

    pedido = Pedido(
        cliente_id=cliente_id,
        unidade_id=unidade_id,
        canal_pedido=canal_pedido,
        status=StatusPedido.AGUARDANDO_PAGAMENTO,
        total=total,
    )
    db.add(pedido)
    db.flush()

    for i in itens_processados:
        db.add(ItemPedido(
            pedido_id=pedido.id,
            produto_id=i["produtoId"],
            quantidade=i["quantidade"],
            preco_unitario=i["preco_unitario"],
        ))

    registrar_log(db, usuario_id, "CRIACAO_PEDIDO", "Pedido", pedido.id)
    db.commit()
    db.refresh(pedido)
    return pedido


def listar_pedidos(db: Session, canal_pedido: str | None, status: str | None,
                    page: int, limit: int) -> tuple[list[Pedido], int]:
    query = select(Pedido)
    if canal_pedido:
        query = query.where(Pedido.canal_pedido == CanalPedido(canal_pedido))
    if status:
        query = query.where(Pedido.status == StatusPedido(status))

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()

    query = query.order_by(Pedido.created_at.desc()).offset((page - 1) * limit).limit(limit)
    itens = db.execute(query).scalars().all()
    return list(itens), total


def obter_pedido(db: Session, pedido_id: int) -> Pedido:
    pedido = db.get(Pedido, pedido_id)
    if not pedido:
        raise RecursoNaoEncontradoError(f"Pedido {pedido_id} não encontrado.")
    return pedido


def atualizar_status(db: Session, usuario_id: int, pedido_id: int, novo_status: StatusPedido) -> Pedido:
    pedido = obter_pedido(db, pedido_id)
    validar_transicao_status(pedido.status, novo_status)
    pedido.status = novo_status
    registrar_log(db, usuario_id, "ATUALIZACAO_STATUS_PEDIDO", "Pedido", pedido.id)
    db.commit()
    db.refresh(pedido)
    return pedido
