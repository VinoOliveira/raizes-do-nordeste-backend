import os

os.environ["DATABASE_URL"] = "sqlite:///./test_raizes.db"

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.infrastructure.db.session import Base, engine, SessionLocal
from src.infrastructure.db.models import Cliente, Usuario
from src.infrastructure.db.seed import popular, SENHA_PADRAO


@pytest.fixture(autouse=True)
def banco_limpo():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        popular(db)
    yield


@pytest.fixture
def client():
    return TestClient(app)


def _login(client, email):
    r = client.post("/auth/login", json={"email": email, "senha": SENHA_PADRAO})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['accessToken']}"}


@pytest.fixture
def auth_cliente(client):
    return _login(client, "cliente@raizes.com")


@pytest.fixture
def auth_gerente(client):
    return _login(client, "gerente@raizes.com")


@pytest.fixture
def auth_cozinha(client):
    return _login(client, "cozinha@raizes.com")


@pytest.fixture
def auth_atendente(client):
    return _login(client, "atendente@raizes.com")


@pytest.fixture
def cliente_id():
    with SessionLocal() as db:
        return db.query(Usuario).filter_by(email="cliente@raizes.com").one().cliente.id


@pytest.fixture
def payload_pedido(cliente_id):
    return {
        "canalPedido": "TOTEM",
        "unidadeId": 1,
        "clienteId": cliente_id,
        "itens": [{"produtoId": 1, "quantidade": 2}],
        "formaPagamento": "MOCK",
    }


@pytest.fixture
def criar_pedido(client, auth_cliente, payload_pedido):
    def _criar(**alteracoes):
        body = {**payload_pedido, **alteracoes}
        return client.post("/pedidos", headers=auth_cliente, json=body)
    return _criar


def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
    if os.path.exists("test_raizes.db"):
        os.remove("test_raizes.db")
