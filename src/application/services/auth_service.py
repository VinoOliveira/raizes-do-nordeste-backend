from sqlalchemy.orm import Session
from sqlalchemy import select

from src.infrastructure.db.models import Usuario, Cliente
from src.infrastructure.security.hashing import hash_senha, verificar_senha
from src.infrastructure.security.jwt import criar_access_token
from src.infrastructure.logging.auditoria import registrar_log
from src.domain.enums import Perfil
from src.config import settings
from datetime import datetime, timezone


class CredenciaisInvalidasError(Exception):
    pass


class EmailJaCadastradoError(Exception):
    pass


def registrar_usuario(db: Session, nome: str, email: str, senha: str,
                       telefone: str | None, consentimento_lgpd: bool) -> Usuario:
    existente = db.execute(select(Usuario).where(Usuario.email == email)).scalar_one_or_none()
    if existente:
        raise EmailJaCadastradoError(f"O e-mail '{email}' já está cadastrado.")

    usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=hash_senha(senha),
        perfil=Perfil.CLIENTE,
        consentimento_lgpd=consentimento_lgpd,
        consentimento_em=datetime.now(timezone.utc) if consentimento_lgpd else None,
    )
    db.add(usuario)
    db.flush()

    cliente = Cliente(usuario_id=usuario.id, telefone=telefone, pontos_fidelidade=0)
    db.add(cliente)

    registrar_log(db, usuario.id, "CADASTRO_USUARIO", "Usuario", usuario.id)
    db.commit()
    db.refresh(usuario)
    return usuario


def autenticar(db: Session, email: str, senha: str) -> Usuario:
    usuario = db.execute(select(Usuario).where(Usuario.email == email)).scalar_one_or_none()
    if not usuario or not verificar_senha(senha, usuario.senha_hash):
        raise CredenciaisInvalidasError("E-mail ou senha inválidos.")
    if not usuario.ativo:
        raise CredenciaisInvalidasError("Usuário inativo.")
    return usuario


def gerar_token_response(usuario: Usuario) -> dict:
    token = criar_access_token(subject=str(usuario.id), perfil=usuario.perfil.value)
    return {
        "accessToken": token,
        "tokenType": "Bearer",
        "expiresIn": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {"id": usuario.id, "nome": usuario.nome, "perfil": usuario.perfil.value},
    }
