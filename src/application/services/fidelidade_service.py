from sqlalchemy.orm import Session

from src.infrastructure.db.models import Cliente, TransacaoFidelidade
from src.domain.enums import TipoTransacaoFidelidade
from src.domain.entities import RegraNegocioError, RecursoNaoEncontradoError


def consultar_saldo(db: Session, cliente_id: int) -> Cliente:
    cliente = db.get(Cliente, cliente_id)
    if not cliente:
        raise RecursoNaoEncontradoError(f"Cliente {cliente_id} não encontrado.")
    return cliente


def registrar_ganho_pontos(db: Session, cliente_id: int, pedido_id: int | None, pontos: int) -> None:
    cliente = db.get(Cliente, cliente_id)
    if not cliente:
        return
    cliente.pontos_fidelidade += pontos
    db.add(TransacaoFidelidade(
        cliente_id=cliente_id, pedido_id=pedido_id, pontos=pontos, tipo=TipoTransacaoFidelidade.GANHO
    ))


def resgatar_pontos(db: Session, cliente_id: int, pontos: int) -> Cliente:
    cliente = consultar_saldo(db, cliente_id)
    if pontos <= 0:
        raise RegraNegocioError("A quantidade de pontos a resgatar deve ser maior que zero.")
    if pontos > cliente.pontos_fidelidade:
        raise RegraNegocioError(
            f"Saldo de pontos insuficiente. Disponível: {cliente.pontos_fidelidade}, solicitado: {pontos}."
        )
    cliente.pontos_fidelidade -= pontos
    db.add(TransacaoFidelidade(
        cliente_id=cliente_id, pedido_id=None, pontos=pontos, tipo=TipoTransacaoFidelidade.RESGATE
    ))
    db.commit()
    db.refresh(cliente)
    return cliente
