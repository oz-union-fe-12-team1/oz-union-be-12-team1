from typing import Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # ==============================
    # CORS
    # ==============================
    CORS_ALLOW_ORIGINS: list[str] = ["*"]

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
    DATABASE_URL: Optional[str] = None

    # ==============================
    # Gemini
    # ==============================
    GEMINI_API_KEY: str = Field("")
    GEMINI_URL: Optional[str] = Field(
        default="https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    )

    # ==============================
    # OpenWeather
    # ==============================
    OPENWEATHER_API_KEY: str = Field("")

    # ==============================
    # Mail
    # ==============================
    MAIL_USERNAME: str = Field("example@example.com")
    MAIL_PASSWORD: str = Field("examplepassword")
    MAIL_FROM: Optional[str] = None
    MAIL_PORT: int = Field(587)
    MAIL_SERVER: str = Field("smtp.gmail.com")
    MAIL_STARTTLS: bool = Field(True)
    MAIL_SSL_TLS: bool = Field(False)
    USE_CREDENTIALS: bool = Field(True)
    VALIDATE_CERTS: bool = Field(True)

    # ==============================
    # AWS S3 (Presigned URL)
    # ==============================
    AWS_ACCESS_KEY_ID: str = Field("")
    AWS_SECRET_ACCESS_KEY: str = Field("")
    AWS_REGION: str = Field("ap-northeast-2")
    AWS_S3_BUCKET: str = Field("nyangbucket")

    # ==============================
    # 앱 환경
    # ==============================
    PYTHONUNBUFFERED: int = Field(1)

    # ==============================
    # 구글 로그인 (선택적)
    # ==============================
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None

    # ==============================
    # Pydantic Settings Config
    # ==============================
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",   # 알 수 없는 필드는 무시
    }

    # ==============================
    # Post-init: 동적 값 세팅
    # ==============================
    def model_post_init(self, __context: Any) -> None:
        # DATABASE_URL 기본값 생성
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
                f"{self.POSTGRES_DB}"
            )
        # MAIL_FROM 기본값 설정
        if self.MAIL_FROM is None:
            self.MAIL_FROM = self.MAIL_USERNAME


settings = Settings()
