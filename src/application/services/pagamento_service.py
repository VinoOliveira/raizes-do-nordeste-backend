import json
from sqlalchemy.orm import Session

from src.infrastructure.db.models import Pagamento
from src.infrastructure.payment.gateway_mock import pagamento_gateway_mock
from src.infrastructure.logging.auditoria import registrar_log
from src.application.services.pedido_service import obter_pedido
from src.application.services.fidelidade_service import registrar_ganho_pontos
from src.domain.enums import StatusPedido, StatusPagamento, FormaPagamento
from src.domain.entities import RegraNegocioError


def solicitar_pagamento(db: Session, usuario_id: int, pedido_id: int, forma_pagamento: str) -> Pagamento:
    pedido = obter_pedido(db, pedido_id)

    if pedido.pagamento is not None:
        raise RegraNegocioError(f"Pedido {pedido_id} já possui um pagamento registrado.")

    resultado = pagamento_gateway_mock.solicitar_pagamento(pedido.id, pedido.total, forma_pagamento)

    pagamento = Pagamento(
        pedido_id=pedido.id,
        forma_pagamento=FormaPagamento(forma_pagamento) if forma_pagamento in FormaPagamento._value2member_map_ else FormaPagamento.MOCK,
        status_pagamento=resultado["status"],
        payload_mock=json.dumps(resultado["payload"]),
    )
    db.add(pagamento)

    if resultado["status"] == StatusPagamento.APROVADO:
        pedido.status = StatusPedido.EM_PREPARO
        # 1 ponto a cada R$10
        pontos = int(pedido.total // 10)
        if pontos > 0:
            registrar_ganho_pontos(db, pedido.cliente_id, pedido.id, pontos)

    registrar_log(db, usuario_id, "SOLICITACAO_PAGAMENTO", "Pagamento", pedido.id)
    db.commit()
    db.refresh(pagamento)
    return pagamento
