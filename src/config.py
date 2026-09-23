from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "sqlite:///./raizes_do_nordeste.db"

    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_5f8a2c9e1b4d7f0a3c6e9b2d5f8a1c4e"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    APP_NAME: str = "Raízes do Nordeste — API"
    ENV: str = "development"


settings = Settings()
