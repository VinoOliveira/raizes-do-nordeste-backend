# Raízes do Nordeste — Back-end

API REST da rede de franquias "Raízes do Nordeste" (Projeto Multidisciplinar — Trilha Back-End).
Cobre autenticação com perfis, cardápio e estoque por unidade, pedidos multicanal, pagamento simulado (mock), fidelização e auditoria.

**Fluxo crítico entregue:** pedido → pagamento mock → atualização de status.

## Links

- Swagger (local): http://localhost:8000/docs
- Coleção Postman: [`postman/raizes-do-nordeste.postman_collection.json`](postman/raizes-do-nordeste.postman_collection.json)
- DER: [`docs/DER.png`](docs/DER.png) (PDF em [`docs/DER.pdf`](docs/DER.pdf))

## Stack

- Python 3.12
- FastAPI, Pydantic v2
- SQLAlchemy 2 (ORM)
- SQLite por padrão; PostgreSQL configurável via `DATABASE_URL`
- JWT (python-jose) e bcrypt (passlib)
- pytest e Postman (newman) para testes

## Requisitos

- Python 3.12 (usar 3.12, versões mais novas podem não ter pacotes pré-compilados para as dependências fixadas)
- Git

## Instalação

```powershell
git clone [https://github.com/SEU-USUARIO/raizes-do-nordeste-backend.git](https://github.com/VinoOliveira/raizes-do-nordeste-backend)
cd raizes-do-nordeste-backend
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Linux/macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Variáveis de ambiente (`.env`)

| Variável | Descrição | Padrão |
|---|---|---|
| `DATABASE_URL` | URL do banco | `sqlite:///./raizes_do_nordeste.db` |
| `SECRET_KEY` | Chave de assinatura do JWT | trocar em qualquer ambiente real |
| `ALGORITHM` | Algoritmo do JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token | `60` |

Para usar PostgreSQL: `pip install psycopg2-binary` e `DATABASE_URL=postgresql://usuario:senha@localhost:5432/raizes_do_nordeste`.

## Banco de dados e seed

As tabelas são criadas automaticamente quando a API inicia. O seed carrega 2 unidades, 5 produtos com estoque e 4 usuários de teste, e pode ser executado mais de uma vez sem duplicar dados:

```powershell
python -m src.infrastructure.db.seed
```

Usuários de teste (senha de todos: `Senha@123`):

| E-mail | Perfil |
|---|---|
| gerente@raizes.com | GERENTE |
| atendente@raizes.com | ATENDENTE |
| cozinha@raizes.com | COZINHA |
| cliente@raizes.com | CLIENTE |

Para recomeçar do zero, apague o arquivo `raizes_do_nordeste.db` e rode o seed novamente.

## Executando a API

```powershell
uvicorn src.api.main:app --reload
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI (JSON): http://localhost:8000/openapi.json

No Swagger, use o botão **Authorize** com o token retornado por `POST /auth/login`.

## Testes

### Automatizados (pytest)

```powershell
pytest
```

Usam um banco SQLite temporário (`test_raizes.db`, removido ao final), independente do banco de desenvolvimento.

### Coleção Postman

1. Aplicar o seed e iniciar a API (seções acima).
2. No Postman: **Import** → `postman/raizes-do-nordeste.postman_collection.json`.
3. Executar a coleção inteira, na ordem, com o **Collection Runner**. Os tokens e IDs são guardados em variáveis de coleção pelos próprios testes.

Pela linha de comando:

```powershell
npx newman run postman/raizes-do-nordeste.postman_collection.json
```

A coleção pode ser executada várias vezes seguidas sem resetar o banco.

| ID | Cenário | Esperado |
|---|---|---|
| T01 | Login válido | 200 + accessToken |
| T02 | Cardápio da unidade | 200 + lista de produtos |
| T03 | Criar pedido válido | 201 + AGUARDANDO_PAGAMENTO |
| T04 | Pagamento mock aprovado | 201 + APROVADO; pedido vai para EM_PREPARO |
| T05 | Cozinha atualiza status | 200 + PRONTO |
| T06 | Filtrar pedidos por canal | 200 + apenas o canal filtrado |
| T07 | Acesso sem token | 401 |
| T08 | Cliente tenta alterar status | 403 |
| T09 | Pedido sem `canalPedido` | 422 |
| T10 | Produto inexistente | 404 |
| T11 | Estoque insuficiente | 409 |
| T12 | Pagamento mock recusado | 201 + RECUSADO; pedido continua AGUARDANDO_PAGAMENTO |
| T13 | Cadastro de cliente | 201, sem senha na resposta |
| T14 | Log de auditoria do pedido | 200 + CRIACAO_PEDIDO e ATUALIZACAO_STATUS_PEDIDO |
| T15 | Quantidade negativa | 422 |
| T16 | Login com senha errada | 401 |

## Endpoints

| Recurso | Rota | Acesso |
|---|---|---|
| Auth | `POST /auth/login` | público |
| Usuários | `POST /usuarios` | público |
| | `GET /usuarios/me` | autenticado |
| Unidades | `GET /unidades` | público |
| Produtos | `GET /produtos?unidadeId=` | público |
| | `POST /produtos`, `PUT /produtos/{id}`, `DELETE /produtos/{id}` | GERENTE |
| | `GET /produtos/{id}` | público |
| Estoque | `GET /estoque/unidades/{id}`, `POST /estoque/movimentos` | ATENDENTE, GERENTE |
| Pedidos | `POST /pedidos` | CLIENTE, ATENDENTE |
| | `GET /pedidos?canalPedido=&status=&page=&limit=`, `GET /pedidos/{id}` | autenticado |
| | `PATCH /pedidos/{id}/status` | COZINHA, ATENDENTE, GERENTE |
| Pagamentos | `POST /pagamentos`, `GET /pagamentos/{id}` | autenticado |
| Fidelidade | `GET /fidelidade/{clienteId}/saldo`, `POST /fidelidade/{clienteId}/resgatar` | autenticado |
| Auditoria | `GET /auditoria?acao=&entidade=&entidadeId=` | GERENTE |

Todos os erros seguem o mesmo formato:

```json
{
  "error": "ESTOQUE_INSUFICIENTE",
  "message": "Mensagem legível",
  "details": [{"field": "campo", "issue": "problema"}],
  "timestamp": "2026-01-01T12:00:00+00:00",
  "path": "/pedidos",
  "requestId": null
}
```

Códigos usados: 200, 201, 204, 401 (não autenticado), 403 (sem permissão), 404 (não encontrado), 409 (regra de negócio) e 422 (validação).

## Regras de negócio

- `canalPedido` é obrigatório na criação do pedido (`APP`, `TOTEM`, `BALCAO`, `PICKUP`, `WEB`) e pode ser usado como filtro na listagem.
- O preço dos itens vem do cadastro do produto; o cliente informa apenas produto e quantidade.
- Estoque é por unidade e debitado na criação do pedido; sem saldo suficiente a API responde 409.
- Fluxo de status: `AGUARDANDO_PAGAMENTO → EM_PREPARO → PRONTO → ENTREGUE`, com `CANCELADO` permitido antes da entrega. Transições fora desse fluxo respondem 409.
- Pagamento mock: valor terminado em `,99` ou `formaPagamento = "RECUSAR_MOCK"` resulta em pagamento recusado; qualquer outro caso é aprovado. Aprovado leva o pedido para `EM_PREPARO`; recusado mantém `AGUARDANDO_PAGAMENTO`.
- Fidelidade: 1 ponto a cada R$ 10 em pedidos com pagamento aprovado; resgate exige saldo suficiente.
- Ações sensíveis (cadastro, criação de pedido, mudança de status, pagamento) geram registro em `logs_auditoria`, consultável por GERENTE.

## Segurança e LGPD

- Senhas armazenadas com hash bcrypt; nunca retornadas nas respostas.
- Autenticação por JWT e autorização por perfil em cada endpoint.
- Consentimento LGPD registrado no cadastro (`consentimentoLGPD` e data do aceite).
- Dados retornados limitados ao necessário para cada recurso.

## Estrutura

```
src/
├── domain/            enums e regras de negócio puras
├── application/       services (casos de uso)
├── infrastructure/    banco (models, sessão, seed), segurança, pagamento mock, auditoria
└── api/               routers, schemas, dependências de autenticação e tratamento de erros
tests/                 testes pytest
postman/               coleção Postman
docs/                  DER
```

## Modelo de dados

![DER](docs/DER.png)
