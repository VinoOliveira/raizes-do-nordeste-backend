import uuid
from datetime import datetime, timezone
from decimal import Decimal

from src.domain.enums import StatusPagamento


class PagamentoGatewayMock:
    # ",99" ou forma RECUSAR_MOCK => recusado (permite testar os dois cenários)
    def solicitar_pagamento(self, pedido_id: int, valor: Decimal, forma_pagamento: str) -> dict:
        recusar = forma_pagamento.upper() == "RECUSAR_MOCK" or (valor % 1 == Decimal("0.99"))

        if recusar:
            return {
                "status": StatusPagamento.RECUSADO,
                "payload": {
                    "motivo": "SALDO_MOCK_INSUFICIENTE",
                    "processedAt": datetime.now(timezone.utc).isoformat(),
                },
            }

        return {
            "status": StatusPagamento.APROVADO,
            "payload": {
                "autorizacao": f"MOCK-AUTH-{uuid.uuid4().hex[:8].upper()}",
                "processedAt": datetime.now(timezone.utc).isoformat(),
            },
        }


pagamento_gateway_mock = PagamentoGatewayMock()
