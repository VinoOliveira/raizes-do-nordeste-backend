from src.infrastructure.db.session import SessionLocal
from src.infrastructure.db.models import LogAuditoria


def test_criar_pedido_valido(criar_pedido):
    r = criar_pedido()
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["status"] == "AGUARDANDO_PAGAMENTO"
    assert corpo["canalPedido"] == "TOTEM"
    assert float(corpo["total"]) == 25.00
    assert corpo["itens"][0]["precoUnitario"] is not None


def test_criar_pedido_sem_canal_retorna_422(client, auth_cliente, payload_pedido):
    del payload_pedido["canalPedido"]
    r = client.post("/pedidos", headers=auth_cliente, json=payload_pedido)
    assert r.status_code == 422
    assert r.json()["details"][0]["field"] == "canalPedido"


def test_criar_pedido_canal_invalido_retorna_422(criar_pedido):
    r = criar_pedido(canalPedido="TELEGRAM")
    assert r.status_code == 422


def test_criar_pedido_quantidade_negativa_retorna_422(criar_pedido):
    r = criar_pedido(itens=[{"produtoId": 1, "quantidade": -1}])
    assert r.status_code == 422


def test_criar_pedido_unidade_inexistente_retorna_404(criar_pedido):
    r = criar_pedido(unidadeId=999)
    assert r.status_code == 404


def test_criar_pedido_produto_inexistente_retorna_404(criar_pedido):
    r = criar_pedido(itens=[{"produtoId": 999, "quantidade": 1}])
    assert r.status_code == 404


def test_criar_pedido_estoque_insuficiente_retorna_409(criar_pedido):
    r = criar_pedido(itens=[{"produtoId": 1, "quantidade": 9999}])
    assert r.status_code == 409
    assert r.json()["error"] == "REGRA_NEGOCIO_VIOLADA"


def test_criar_pedido_debita_estoque(client, auth_gerente, criar_pedido):
    criar_pedido(itens=[{"produtoId": 1, "quantidade": 3}])
    r = client.get("/estoque/unidades/1", headers=auth_gerente)
    saldo = next(i for i in r.json() if i["produtoId"] == 1)
    assert saldo["quantidade"] == 47


def test_filtrar_pedidos_por_canal(client, auth_cliente, criar_pedido):
    criar_pedido(canalPedido="APP")
    criar_pedido(canalPedido="TOTEM")
    r = client.get("/pedidos?canalPedido=TOTEM", headers=auth_cliente)
    assert r.status_code == 200
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["canalPedido"] == "TOTEM"


def test_listagem_paginada(client, auth_cliente, criar_pedido):
    for _ in range(3):
        criar_pedido()
    r = client.get("/pedidos?page=1&limit=2", headers=auth_cliente)
    assert r.json()["total"] == 3
    assert len(r.json()["items"]) == 2


def test_cliente_nao_pode_atualizar_status(client, auth_cliente, criar_pedido):
    pedido_id = criar_pedido().json()["pedidoId"]
    r = client.patch(f"/pedidos/{pedido_id}/status", headers=auth_cliente, json={"novoStatus": "PRONTO"})
    assert r.status_code == 403
    assert r.json()["error"] == "SEM_PERMISSAO"


def test_transicao_de_status_invalida_retorna_409(client, auth_cozinha, criar_pedido):
    pedido_id = criar_pedido().json()["pedidoId"]
    r = client.patch(f"/pedidos/{pedido_id}/status", headers=auth_cozinha, json={"novoStatus": "ENTREGUE"})
    assert r.status_code == 409


def test_pedido_inexistente_retorna_404(client, auth_cliente):
    r = client.get("/pedidos/999", headers=auth_cliente)
    assert r.status_code == 404


def test_criar_pedido_gera_log_de_auditoria(criar_pedido):
    pedido_id = criar_pedido().json()["pedidoId"]
    with SessionLocal() as db:
        log = db.query(LogAuditoria).filter_by(acao="CRIACAO_PEDIDO", entidade_id=str(pedido_id)).first()
    assert log is not None


def test_gerente_consulta_auditoria_do_pedido(client, auth_gerente, auth_cozinha, criar_pedido):
    pedido_id = criar_pedido().json()["pedidoId"]
    client.patch(f"/pedidos/{pedido_id}/status", headers=auth_cozinha, json={"novoStatus": "CANCELADO"})
    r = client.get(f"/auditoria?entidade=Pedido&entidadeId={pedido_id}", headers=auth_gerente)
    assert r.status_code == 200
    acoes = {i["acao"] for i in r.json()["items"]}
    assert acoes == {"CRIACAO_PEDIDO", "ATUALIZACAO_STATUS_PEDIDO"}


def test_cliente_nao_acessa_auditoria(client, auth_cliente):
    assert client.get("/auditoria", headers=auth_cliente).status_code == 403


def test_usuarios_me_retorna_cliente_id(client, auth_cliente, cliente_id):
    assert client.get("/usuarios/me", headers=auth_cliente).json()["clienteId"] == cliente_id
