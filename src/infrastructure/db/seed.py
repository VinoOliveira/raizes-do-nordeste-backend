from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.db.session import Base, engine, SessionLocal
from src.infrastructure.db import models
from src.infrastructure.db.models import Usuario, Cliente, Unidade, Produto, EstoqueUnidade
from src.infrastructure.security.hashing import hash_senha
from src.domain.enums import Perfil

SENHA_PADRAO = "Senha@123"

UNIDADES = [
    ("Raízes do Nordeste - Boa Viagem", "Av. Boa Viagem, 1000", "Recife/PE"),
    ("Raízes do Nordeste - Pelourinho", "Largo do Pelourinho, 25", "Salvador/BA"),
]

PRODUTOS = [
    ("Tapioca de queijo coalho", "Lanche", "12.50"),
    ("Cuscuz com carne de sol", "Prato", "18.00"),
    ("Baião de dois", "Prato", "24.90"),
    ("Suco de caju", "Bebida", "8.00"),
    ("Bolo de rolo", "Sobremesa", "9.50"),
]

USUARIOS = [
    ("Gerente Raízes", "gerente@raizes.com", Perfil.GERENTE),
    ("Atendente Balcão", "atendente@raizes.com", Perfil.ATENDENTE),
    ("Cozinha Central", "cozinha@raizes.com", Perfil.COZINHA),
    ("Maria Cliente", "cliente@raizes.com", Perfil.CLIENTE),
]

ESTOQUE_INICIAL = 50


def popular(db: Session) -> None:
    if db.execute(select(Unidade)).first():
        return

    unidades = [Unidade(nome=n, endereco=e, cidade_uf=c) for n, e, c in UNIDADES]
    produtos = [Produto(nome=n, categoria=c, preco=Decimal(p)) for n, c, p in PRODUTOS]
    db.add_all(unidades + produtos)
    db.flush()

    for unidade in unidades:
        for produto in produtos:
            db.add(EstoqueUnidade(
                unidade_id=unidade.id, produto_id=produto.id,
                quantidade=ESTOQUE_INICIAL, estoque_minimo=5,
            ))

    senha_hash = hash_senha(SENHA_PADRAO)
    for nome, email, perfil in USUARIOS:
        usuario = Usuario(
            nome=nome, email=email, senha_hash=senha_hash, perfil=perfil,
            consentimento_lgpd=perfil == Perfil.CLIENTE,
        )
        db.add(usuario)
        db.flush()
        if perfil == Perfil.CLIENTE:
            db.add(Cliente(usuario_id=usuario.id, telefone="81999990000", pontos_fidelidade=0))

    db.commit()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        popular(db)
    print("Seed aplicado.")
