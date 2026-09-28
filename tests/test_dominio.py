from decimal import Decimal

import pytest

from src.domain.entities import (
    RegraNegocioError, calcular_total_pedido, validar_estoque_suficiente, validar_transicao_status,
)
from src.domain.enums import StatusPedido


def test_calcular_total_pedido():
    itens = [
        {"quantidade": 2, "preco_unitario": Decimal("12.50")},
        {"quantidade": 1, "preco_unitario": Decimal("8.00")},
    ]
    assert calcular_total_pedido(itens) == Decimal("33.00")


@pytest.mark.parametrize("atual,novo", [
    (StatusPedido.AGUARDANDO_PAGAMENTO, StatusPedido.EM_PREPARO),
    (StatusPedido.EM_PREPARO, StatusPedido.PRONTO),
    (StatusPedido.PRONTO, StatusPedido.ENTREGUE),
    (StatusPedido.EM_PREPARO, StatusPedido.CANCELADO),
])
def test_transicoes_validas(atual, novo):
    validar_transicao_status(atual, novo)


@pytest.mark.parametrize("atual,novo", [
    (StatusPedido.ENTREGUE, StatusPedido.PRONTO),
    (StatusPedido.CANCELADO, StatusPedido.EM_PREPARO),
    (StatusPedido.AGUARDANDO_PAGAMENTO, StatusPedido.ENTREGUE),
])
def test_transicoes_invalidas(atual, novo):
    with pytest.raises(RegraNegocioError):
        validar_transicao_status(atual, novo)


def test_estoque_insuficiente():
    with pytest.raises(RegraNegocioError):
        validar_estoque_suficiente(saldo_disponivel=1, quantidade_solicitada=2)
    validar_estoque_suficiente(saldo_disponivel=2, quantidade_solicitada=2)
