from decimal import Decimal
from src.domain.enums import StatusPedido, TRANSICOES_STATUS_VALIDAS


class RegraNegocioError(Exception):
    pass


class RecursoNaoEncontradoError(Exception):
    pass


def calcular_total_pedido(itens: list[dict]) -> Decimal:
    total = Decimal("0.00")
    for item in itens:
        total += Decimal(item["quantidade"]) * Decimal(item["preco_unitario"])
    return total.quantize(Decimal("0.01"))


def validar_transicao_status(status_atual: StatusPedido, novo_status: StatusPedido) -> None:
    permitidos = TRANSICOES_STATUS_VALIDAS.get(status_atual, set())
    if novo_status not in permitidos:
        raise RegraNegocioError(
            f"Transição de status inválida: {status_atual.value} -> {novo_status.value}"
        )


def validar_estoque_suficiente(saldo_disponivel: int, quantidade_solicitada: int) -> None:
    if quantidade_solicitada > saldo_disponivel:
        raise RegraNegocioError(
            f"Estoque insuficiente. Disponível: {saldo_disponivel}, solicitado: {quantidade_solicitada}."
        )
