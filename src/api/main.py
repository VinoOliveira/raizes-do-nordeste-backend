from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.infrastructure.db.session import Base, engine
from src.infrastructure.db import models  # noqa: F401
from src.api.error_handlers import register_exception_handlers
from src.api.v1 import auth, usuarios, unidades, produtos, estoque, pedidos, pagamentos, fidelidade, auditoria

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(unidades.router)
app.include_router(produtos.router)
app.include_router(estoque.router)
app.include_router(pedidos.router)
app.include_router(pagamentos.router)
app.include_router(fidelidade.router)
app.include_router(auditoria.router)


@app.get("/")
def root():
    return {"status": "ok", "app": settings.APP_NAME}
