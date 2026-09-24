from sqlalchemy.orm import Session
from src.infrastructure.db.models import LogAuditoria


def registrar_log(db: Session, usuario_id, acao: str, entidade: str, entidade_id) -> None:
    log = LogAuditoria(
        usuario_id=usuario_id,
        acao=acao,
        entidade=entidade,
        entidade_id=str(entidade_id) if entidade_id is not None else None,
    )
    db.add(log)
