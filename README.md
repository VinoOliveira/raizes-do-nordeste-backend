# Raízes do Nordeste — Back-end

API REST para a rede de franquias "Raízes do Nordeste" — Projeto Multidisciplinar (Trilha Back-End).

## Stack

- Python 3.12+
- FastAPI
- SQLAlchemy + Alembic
- SQLite (dev) / PostgreSQL (produção)
- JWT + bcrypt

## Estrutura

```
src/
├── domain/
├── application/services/
├── infrastructure/
└── api/
```

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```
