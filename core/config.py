from typing import Any

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ==============================
    # JWT / 토큰
    # ==============================
    SECRET_KEY: str = Field("please_change_me_32+chars")
    ALGORITHM: str = Field("HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7)

    # ==============================
    # Database
    # ==============================
    POSTGRES_USER: str = Field("postgres")
    POSTGRES_PASSWORD: str = Field("postgres")
    POSTGRES_DB: str = Field("postgres")
    POSTGRES_HOST: str = Field("db")
    POSTGRES_PORT: int = Field(5432)
    DATABASE_URL: str | None = None  # env에 직접 DATABASE_URL 설정 가능

    # ==============================
    # Google Sheets
    # ==============================
    GOOGLE_CREDENTIALS_FILE: str = Field("google-credentials.json")
    GOOGLE_SPREADSHEET_ID: str = Field("")
    GOOGLE_SHEET_NAME: str = Field("quiz")

    # ==============================
    # Gemini
    # ==============================
    GEMINI_API_KEY: str = Field("")

    # ==============================
    # OpenWeather
    # ==============================
    OPENWEATHER_API_KEY: str = Field("")

    # ==============================
    # Mail (FastAPI-Mail)
    # ==============================
    MAIL_USERNAME: str = Field("example@example.com")
    MAIL_PASSWORD: str = Field("examplepassword")
    MAIL_FROM: str | None = None  # 기본값은 MAIL_USERNAME로 아래 init에서 설정
    MAIL_PORT: int = Field(587)
    MAIL_SERVER: str = Field("smtp.gmail.com")
    MAIL_STARTTLS: bool = Field(True)
    MAIL_SSL_TLS: bool = Field(False)
    USE_CREDENTIALS: bool = Field(True)
    VALIDATE_CERTS: bool = Field(True)

    # ==============================
    # 앱 환경 설정
    # ==============================
    PYTHONUNBUFFERED: int = Field(1)

    # 구글 로그인
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # ==============================
    # Pydantic Settings Config
    # ==============================
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **values: Any) -> None:
        super().__init__(**values)
        # DATABASE_URL 없으면 기본 구성으로 생성
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
                f"{self.POSTGRES_DB}"
            )
        # MAIL_FROM 없으면 MAIL_USERNAME 사용
        if self.MAIL_FROM is None:
            self.MAIL_FROM = self.MAIL_USERNAME


# 전역 인스턴스
settings = Settings()