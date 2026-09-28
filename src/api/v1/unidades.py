from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.infrastructure.db.session import get_db
from src.infrastructure.db.models import Unidade
from src.api.schemas.catalogo import UnidadeResponse

router = APIRouter(prefix="/unidades", tags=["unidades"])


@router.get("", response_model=list[UnidadeResponse])
def listar(db: Session = Depends(get_db)):
    unidades = db.execute(select(Unidade).where(Unidade.ativo == True)).scalars().all()
    return [
        UnidadeResponse(id=u.id, nome=u.nome, endereco=u.endereco, cidadeUf=u.cidade_uf, ativo=u.ativo)
        for u in unidades
    ]
