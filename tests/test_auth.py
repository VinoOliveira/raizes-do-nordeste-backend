def test_login_valido_retorna_token(client):
    r = client.post("/auth/login", json={"email": "cliente@raizes.com", "senha": "Senha@123"})
    assert r.status_code == 200
    corpo = r.json()
    assert corpo["accessToken"]
    assert corpo["tokenType"] == "Bearer"
    assert corpo["user"]["perfil"] == "CLIENTE"


def test_login_senha_errada_retorna_401(client):
    r = client.post("/auth/login", json={"email": "cliente@raizes.com", "senha": "errada"})
    assert r.status_code == 401
    assert r.json()["error"] == "CREDENCIAIS_INVALIDAS"


def test_acesso_sem_token_retorna_401(client):
    r = client.get("/pedidos")
    assert r.status_code == 401
    assert r.json()["error"] == "NAO_AUTENTICADO"


def test_token_invalido_retorna_401(client):
    r = client.get("/pedidos", headers={"Authorization": "Bearer token-falso"})
    assert r.status_code == 401


def test_cadastro_novo_usuario(client):
    r = client.post("/usuarios", json={
        "nome": "Novo Cliente", "email": "novo@teste.com", "senha": "Senha@123", "consentimentoLGPD": True,
    })
    assert r.status_code == 201
    corpo = r.json()
    assert corpo["perfil"] == "CLIENTE"
    assert "senha" not in corpo
    assert "senhaHash" not in corpo


def test_cadastro_email_duplicado_retorna_409(client):
    r = client.post("/usuarios", json={
        "nome": "Outra Maria", "email": "cliente@raizes.com", "senha": "Senha@123",
    })
    assert r.status_code == 409
    assert r.json()["error"] == "EMAIL_JA_CADASTRADO"


def test_cadastro_email_invalido_retorna_422(client):
    r = client.post("/usuarios", json={"nome": "Fulano", "email": "nao-e-email", "senha": "Senha@123"})
    assert r.status_code == 422
    assert r.json()["error"] == "VALIDACAO_FALHOU"


def test_usuarios_me_retorna_usuario_logado(client, auth_cliente):
    r = client.get("/usuarios/me", headers=auth_cliente)
    assert r.status_code == 200
    assert r.json()["email"] == "cliente@raizes.com"
