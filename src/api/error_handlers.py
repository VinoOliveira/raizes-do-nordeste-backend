from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.domain.entities import RegraNegocioError, RecursoNaoEncontradoError
from src.application.services.auth_service import CredenciaisInvalidasError, EmailJaCadastradoError
from src.infrastructure.security.jwt import TokenInvalidoError
from src.api.schemas.common import ErrorResponse, ErrorDetail


def _body(error: str, message: str, path: str, details=None) -> dict:
    return ErrorResponse(error=error, message=message, path=path, details=details or []).model_dump()


def register_exception_handlers(app):
    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        details = [ErrorDetail(field=".".join(str(x) for x in e["loc"][1:]), issue=e["msg"]) for e in exc.errors()]
        return JSONResponse(status_code=422, content=_body("VALIDACAO_FALHOU", "Dados inválidos na requisição.", str(request.url.path), details))

    @app.exception_handler(RecursoNaoEncontradoError)
    async def not_found_handler(request: Request, exc: RecursoNaoEncontradoError):
        return JSONResponse(status_code=404, content=_body("RECURSO_NAO_ENCONTRADO", str(exc), str(request.url.path)))

    @app.exception_handler(RegraNegocioError)
    async def business_rule_handler(request: Request, exc: RegraNegocioError):
        return JSONResponse(status_code=409, content=_body("REGRA_NEGOCIO_VIOLADA", str(exc), str(request.url.path)))

    @app.exception_handler(CredenciaisInvalidasError)
    async def credentials_handler(request: Request, exc: CredenciaisInvalidasError):
        return JSONResponse(status_code=401, content=_body("CREDENCIAIS_INVALIDAS", str(exc), str(request.url.path)))

    @app.exception_handler(EmailJaCadastradoError)
    async def email_handler(request: Request, exc: EmailJaCadastradoError):
        return JSONResponse(status_code=409, content=_body("EMAIL_JA_CADASTRADO", str(exc), str(request.url.path)))

    @app.exception_handler(TokenInvalidoError)
    async def token_handler(request: Request, exc: TokenInvalidoError):
        return JSONResponse(status_code=401, content=_body("TOKEN_INVALIDO", str(exc), str(request.url.path)))

    @app.exception_handler(HTTPException)
    async def http_exc_handler(request: Request, exc: HTTPException):
        error_map = {401: "NAO_AUTENTICADO", 403: "SEM_PERMISSAO", 404: "RECURSO_NAO_ENCONTRADO"}
        return JSONResponse(status_code=exc.status_code, content=_body(error_map.get(exc.status_code, "ERRO"), str(exc.detail), str(request.url.path)))
