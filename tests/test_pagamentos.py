def test_pagamento_aprovado_atualiza_status_do_pedido(client, auth_cliente, criar_pedido):
    pedido_id = criar_pedido().json()["pedidoId"]
    r = client.post("/pagamentos", headers=auth_cliente, json={"pedidoId": pedido_id, "formaPagamento": "MOCK"})
    assert r.status_code == 201
    assert r.json()["statusPagamento"] == "APROVADO"
    assert r.json()["payload"]["autorizacao"].startswith("MOCK-AUTH-")

    pedido = client.get(f"/pedidos/{pedido_id}", headers=auth_cliente).json()
    assert pedido["status"] == "EM_PREPARO"


def test_pagamento_recusado_mantem_pedido_aguardando(client, auth_cliente, criar_pedido):
    pedido_id = criar_pedido().json()["pedidoId"]
    r = client.post("/pagamentos", headers=auth_cliente, json={"pedidoId": pedido_id, "formaPagamento": "RECUSAR_MOCK"})
    assert r.status_code == 201
    assert r.json()["statusPagamento"] == "RECUSADO"
    assert r.json()["payload"]["motivo"] == "SALDO_MOCK_INSUFICIENTE"

    pedido = client.get(f"/pedidos/{pedido_id}", headers=auth_cliente).json()
    assert pedido["status"] == "AGUARDANDO_PAGAMENTO"


def test_pagamento_duplicado_retorna_409(client, auth_cliente, criar_pedido):
    pedido_id = criar_pedido().json()["pedidoId"]
    client.post("/pagamentos", headers=auth_cliente, json={"pedidoId": pedido_id, "formaPagamento": "MOCK"})
    r = client.post("/pagamentos", headers=auth_cliente, json={"pedidoId": pedido_id, "formaPagamento": "MOCK"})
    assert r.status_code == 409


def test_pagamento_de_pedido_inexistente_retorna_404(client, auth_cliente):
    r = client.post("/pagamentos", headers=auth_cliente, json={"pedidoId": 999, "formaPagamento": "MOCK"})
    assert r.status_code == 404


def test_pagamento_aprovado_credita_pontos_de_fidelidade(client, auth_cliente, criar_pedido, cliente_id):
    pedido_id = criar_pedido(itens=[{"produtoId": 3, "quantidade": 2}]).json()["pedidoId"]
    client.post("/pagamentos", headers=auth_cliente, json={"pedidoId": pedido_id, "formaPagamento": "MOCK"})
    r = client.get(f"/fidelidade/{cliente_id}/saldo", headers=auth_cliente)
    assert r.json()["pontosFidelidade"] == 4


def test_fluxo_completo_ate_entrega(client, auth_cliente, auth_cozinha, criar_pedido):
    pedido_id = criar_pedido().json()["pedidoId"]
    client.post("/pagamentos", headers=auth_cliente, json={"pedidoId": pedido_id, "formaPagamento": "MOCK"})
    for novo in ("PRONTO", "ENTREGUE"):
        r = client.patch(f"/pedidos/{pedido_id}/status", headers=auth_cozinha, json={"novoStatus": novo})
        assert r.status_code == 200
        assert r.json()["status"] == novo
