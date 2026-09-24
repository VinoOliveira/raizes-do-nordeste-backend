from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    String, Integer, Numeric, Boolean, DateTime, ForeignKey, Enum as SAEnum, Text, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.session import Base
from src.domain.enums import (
    Perfil, CanalPedido, StatusPedido, FormaPagamento, StatusPagamento,
    TipoMovimentoEstoque, TipoTransacaoFidelidade,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[Perfil] = mapped_column(SAEnum(Perfil, values_callable=lambda e: [i.value for i in e]), nullable=False)
    consentimento_lgpd: Mapped[bool] = mapped_column(Boolean, default=False)
    consentimento_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    cliente: Mapped["Cliente | None"] = relationship(back_populates="usuario", uselist=False)


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), unique=True, nullable=False)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pontos_fidelidade: Mapped[int] = mapped_column(Integer, default=0)

    usuario: Mapped["Usuario"] = relationship(back_populates="cliente")
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="cliente")


class Unidade(Base):
    __tablename__ = "unidades"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    endereco: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cidade_uf: Mapped[str | None] = mapped_column(String(80), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    categoria: Mapped[str | None] = mapped_column(String(80), nullable=True)
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)


class EstoqueUnidade(Base):
    __tablename__ = "estoque_unidade"
    __table_args__ = (UniqueConstraint("unidade_id", "produto_id", name="uq_estoque_unidade_produto"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"), nullable=False)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, default=0)
    estoque_minimo: Mapped[int] = mapped_column(Integer, default=0)

    unidade: Mapped["Unidade"] = relationship()
    produto: Mapped["Produto"] = relationship()
    movimentos: Mapped[list["MovimentoEstoque"]] = relationship(back_populates="estoque")


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"), nullable=False)
    canal_pedido: Mapped[CanalPedido] = mapped_column(
        SAEnum(CanalPedido, values_callable=lambda e: [i.value for i in e]), nullable=False
    )
    status: Mapped[StatusPedido] = mapped_column(
        SAEnum(StatusPedido, values_callable=lambda e: [i.value for i in e]),
        default=StatusPedido.AGUARDANDO_PAGAMENTO,
    )
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    cliente: Mapped["Cliente"] = relationship(back_populates="pedidos")
    unidade: Mapped["Unidade"] = relationship()
    itens: Mapped[list["ItemPedido"]] = relationship(back_populates="pedido", cascade="all, delete-orphan")
    pagamento: Mapped["Pagamento | None"] = relationship(back_populates="pedido", uselist=False)


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), nullable=False)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    pedido: Mapped["Pedido"] = relationship(back_populates="itens")
    produto: Mapped["Produto"] = relationship()


class Pagamento(Base):
    __tablename__ = "pagamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), unique=True, nullable=False)
    forma_pagamento: Mapped[FormaPagamento] = mapped_column(
        SAEnum(FormaPagamento, values_callable=lambda e: [i.value for i in e]), nullable=False
    )
    status_pagamento: Mapped[StatusPagamento] = mapped_column(
        SAEnum(StatusPagamento, values_callable=lambda e: [i.value for i in e]),
        default=StatusPagamento.PENDENTE,
    )
    payload_mock: Mapped[str | None] = mapped_column(Text, nullable=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    pedido: Mapped["Pedido"] = relationship(back_populates="pagamento")


class MovimentoEstoque(Base):
    __tablename__ = "movimentos_estoque"

    id: Mapped[int] = mapped_column(primary_key=True)
    estoque_id: Mapped[int] = mapped_column(ForeignKey("estoque_unidade.id"), nullable=False)
    tipo: Mapped[TipoMovimentoEstoque] = mapped_column(
        SAEnum(TipoMovimentoEstoque, values_callable=lambda e: [i.value for i in e]), nullable=False
    )
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    origem: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    estoque: Mapped["EstoqueUnidade"] = relationship(back_populates="movimentos")


class TransacaoFidelidade(Base):
    __tablename__ = "transacoes_fidelidade"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    pedido_id: Mapped[int | None] = mapped_column(ForeignKey("pedidos.id"), nullable=True)
    pontos: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo: Mapped[TipoTransacaoFidelidade] = mapped_column(
        SAEnum(TipoTransacaoFidelidade, values_callable=lambda e: [i.value for i in e]), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    acao: Mapped[str] = mapped_column(String(80), nullable=False)
    entidade: Mapped[str] = mapped_column(String(80), nullable=False)
    entidade_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=_now)
