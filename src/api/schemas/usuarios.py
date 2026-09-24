from pydantic import BaseModel, EmailStr, Field


class UsuarioCreateRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=6, max_length=128)
    telefone: str | None = None
    consentimentoLGPD: bool = False


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    perfil: str
    consentimentoLGPD: bool
