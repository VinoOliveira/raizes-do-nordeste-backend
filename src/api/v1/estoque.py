from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.infrastructure.db.session import get_db
from src.application.services import estoque_service
from src.api.schemas.estoque import SaldoEstoqueResponse, MovimentoEstoqueRequest, MovimentoEstoqueResponse
from src.api.deps import require_perfis

router = APIRouter(prefix="/estoque", tags=["estoque"])


@router.get("/unidades/{unidade_id}", response_model=list[SaldoEstoqueResponse],
            dependencies=[Depends(require_perfis("ATENDENTE", "GERENTE"))])
def saldo_por_unidade(unidade_id: int, db: Session = Depends(get_db)):
    return estoque_service.consultar_saldo_unidade(db, unidade_id)


@router.post("/movimentos", response_model=MovimentoEstoqueResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_perfis("ATENDENTE", "GERENTE"))])
def registrar_movimento(payload: MovimentoEstoqueRequest, db: Session = Depends(get_db)):
    movimento = estoque_service.registrar_movimento(
        db, payload.unidadeId, payload.produtoId, payload.tipo, payload.quantidade, payload.origem
    )
    return MovimentoEstoqueResponse(
        id=movimento.id, unidadeId=payload.unidadeId, produtoId=payload.produtoId,
        tipo=movimento.tipo.value, quantidade=movimento.quantidade,
        saldoAtual=movimento.estoque.quantidade,
    )
