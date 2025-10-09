from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ==============================
    # 기본 설정
    # ==============================
    APP_NAME: str
    APP_ENV: str
    TZ: str

    # ==============================
    # 보안 / 토큰
    # ==============================
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # ==============================
    # Database
    # ==============================
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    # ==============================
    # Uvicorn
    # ==============================
    UVICORN_HOST: str
    UVICORN_PORT: int
    UVICORN_RELOAD: bool

    # ==============================
    # CORS
    # ==============================
    CORS_ALLOW_ORIGINS: list[str] = ["*"]

    # ==============================
    # Logging
    # ==============================
    LOG_LEVEL: str

    # ==============================
    # 메일 설정
    # ==============================
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool

    # ==============================
    # 외부 API
    # ==============================
    OPENWEATHER_API_KEY: str
    GEMINI_API_KEY: str

    # ==============================
    # 구글 로그인
    # ==============================
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    FRONTEND_URL_LOCAL: str | None = None

    # ==============================
    # AWS S3
    # ==============================
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str | None = None
    AWS_S3_BUCKET: str | None = None

    # ==============================
    # pgAdmin (옵션)
    # ==============================
    PGADMIN_DEFAULT_EMAIL: str | None = None
    PGADMIN_DEFAULT_PASSWORD: str | None = None

    # ==============================
    # Config 설정
    # ==============================
    class Config:
        env_file = (".env.local", ".env")  
        env_file_encoding = "utf-8"


# ==============================
# Settings 인스턴스 생성
# ==============================
settings = Settings()
