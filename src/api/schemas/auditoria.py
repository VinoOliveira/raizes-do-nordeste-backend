from datetime import datetime
from pydantic import BaseModel


class LogAuditoriaResponse(BaseModel):
    id: int
    usuarioId: int | None
    acao: str
    entidade: str
    entidadeId: str | None
    timestamp: datetime


class LogAuditoriaListResponse(BaseModel):
    page: int
    limit: int
    total: int
    items: list[LogAuditoriaResponse]
