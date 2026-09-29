from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.infrastructure.db.session import get_db
from src.infrastructure.db.models import LogAuditoria
from src.api.schemas.auditoria import LogAuditoriaResponse, LogAuditoriaListResponse
from src.api.deps import require_perfis

router = APIRouter(prefix="/auditoria", tags=["auditoria"], dependencies=[Depends(require_perfis("GERENTE"))])


@router.get("", response_model=LogAuditoriaListResponse)
def listar(acao: str | None = None, entidade: str | None = None, entidadeId: str | None = None,
           page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100),
           db: Session = Depends(get_db)):
    query = select(LogAuditoria)
    if acao:
        query = query.where(LogAuditoria.acao == acao)
    if entidade:
        query = query.where(LogAuditoria.entidade == entidade)
    if entidadeId:
        query = query.where(LogAuditoria.entidade_id == entidadeId)

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
    registros = db.execute(
        query.order_by(LogAuditoria.id.desc()).offset((page - 1) * limit).limit(limit)
    ).scalars().all()

    return LogAuditoriaListResponse(
        page=page, limit=limit, total=total,
        items=[
            LogAuditoriaResponse(id=r.id, usuarioId=r.usuario_id, acao=r.acao, entidade=r.entidade,
                                 entidadeId=r.entidade_id, timestamp=r.timestamp)
            for r in registros
        ],
    )
