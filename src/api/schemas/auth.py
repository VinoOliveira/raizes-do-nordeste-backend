from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class UserOut(BaseModel):
    id: int
    nome: str
    perfil: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    accessToken: str
    tokenType: str = "Bearer"
    expiresIn: int
    user: UserOut
