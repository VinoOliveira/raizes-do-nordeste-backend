from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha_texto_claro: str) -> str:
    return pwd_context.hash(senha_texto_claro)


def verificar_senha(senha_texto_claro: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_texto_claro, senha_hash)
