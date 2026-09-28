def test_entrada_de_estoque_aumenta_saldo(client, auth_gerente):
    r = client.post("/estoque/movimentos", headers=auth_gerente, json={
        "unidadeId": 1, "produtoId": 1, "tipo": "ENTRADA", "quantidade": 10, "origem": "REPOSICAO",
    })
    assert r.status_code == 201
    assert r.json()["saldoAtual"] == 60


def test_saida_maior_que_saldo_retorna_409(client, auth_gerente):
    r = client.post("/estoque/movimentos", headers=auth_gerente, json={
        "unidadeId": 1, "produtoId": 1, "tipo": "SAIDA", "quantidade": 500,
    })
    assert r.status_code == 409


def test_movimento_com_tipo_invalido_retorna_422(client, auth_gerente):
    r = client.post("/estoque/movimentos", headers=auth_gerente, json={
        "unidadeId": 1, "produtoId": 1, "tipo": "TROCA", "quantidade": 1,
    })
    assert r.status_code == 422


def test_cliente_nao_acessa_estoque(client, auth_cliente):
    r = client.get("/estoque/unidades/1", headers=auth_cliente)
    assert r.status_code == 403


def test_estoque_de_unidade_inexistente_retorna_404(client, auth_gerente):
    r = client.get("/estoque/unidades/999", headers=auth_gerente)
    assert r.status_code == 404


def test_cardapio_lista_produtos_sem_autenticacao(client):
    r = client.get("/produtos")
    assert r.status_code == 200
    assert len(r.json()) == 5


def test_apenas_gerente_cria_produto(client, auth_cliente, auth_gerente):
    body = {"nome": "Cartola", "categoria": "Sobremesa", "preco": "11.00"}
    assert client.post("/produtos", headers=auth_cliente, json=body).status_code == 403
    assert client.post("/produtos", headers=auth_gerente, json=body).status_code == 201


def test_resgate_de_pontos_com_saldo_insuficiente_retorna_409(client, auth_cliente, cliente_id):
    r = client.post(f"/fidelidade/{cliente_id}/resgatar", headers=auth_cliente, json={"pontos": 10})
    assert r.status_code == 409


def test_resgate_de_pontos(client, auth_cliente, criar_pedido, cliente_id):
    pedido_id = criar_pedido(itens=[{"produtoId": 3, "quantidade": 2}]).json()["pedidoId"]
    client.post("/pagamentos", headers=auth_cliente, json={"pedidoId": pedido_id, "formaPagamento": "MOCK"})
    r = client.post(f"/fidelidade/{cliente_id}/resgatar", headers=auth_cliente, json={"pontos": 3})
    assert r.status_code == 200
    assert r.json()["saldoRestante"] == 1
