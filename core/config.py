from typing import Any, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==============================
    # 기본 설정
    # ==============================
    APP_NAME: str = Field(default="OZ Union Backend")
    APP_ENV: str = Field(default="local")
    TZ: str = Field(default="Asia/Seoul")

    # ==============================
    # 보안 / 토큰
    # ==============================
    SECRET_KEY: str = Field(default="please_change_me_32+chars")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # ==============================
    # Database
    # ==============================
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="postgres")
    POSTGRES_HOST: str = Field(default="db")
    POSTGRES_PORT: int = Field(default=5432)
    DATABASE_URL: Optional[str] = None

    # ==============================
    # Gemini (Google Generative AI)
    # ==============================
    GEMINI_API_KEY: str = Field(default="", description="Gemini API Key")
    GEMINI_URL: str = Field(
        default="https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent",
        description="Gemini API 기본 URL",
    )

    # ==============================
    # 외부 API
    # ==============================
    OPENWEATHER_API_KEY: str = Field(default="", description="OpenWeather API Key")

    # ==============================
    # 이메일 설정
    # ==============================
    MAIL_USERNAME: str = Field(default="")
    MAIL_PASSWORD: str = Field(default="")
    MAIL_FROM: Optional[str] = Field(default=None)
    MAIL_PORT: int = Field(default=587)
    MAIL_SERVER: str = Field(default="smtp.gmail.com")
    MAIL_STARTTLS: bool = Field(default=True)
    MAIL_SSL_TLS: bool = Field(default=False)
    USE_CREDENTIALS: bool = Field(default=True)
    VALIDATE_CERTS: bool = Field(default=True)

    # ==============================
    # AWS S3
    # ==============================
    AWS_ACCESS_KEY_ID: str = Field(default="", description="AWS Access Key")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", description="AWS Secret Key")
    AWS_REGION: str = Field(default="ap-northeast-2", description="S3 Region")
    AWS_S3_BUCKET: str = Field(default="nyangbucket", description="S3 Bucket Name")

    # ==============================
    # Google OAuth
    # ==============================
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None)
    GOOGLE_SECRET: Optional[str] = Field(default=None)
    GOOGLE_REDIRECT_URI: Optional[str] = Field(default=None)

    # ==============================
    # Python 환경
    # ==============================
    PYTHONUNBUFFERED: int = Field(default=1)

    # ==============================
    # 환경 설정 (SettingsConfigDict)
    # ==============================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ==============================
    # 후처리 로직
    # ==============================
    def model_post_init(self, __context: Any) -> None:
        """DATABASE_URL 자동 구성 및 MAIL_FROM 기본값 보정"""
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        if self.MAIL_FROM is None:
            self.MAIL_FROM = self.MAIL_USERNAME


# ==============================
# Settings 인스턴스 생성
# ==============================
settings = Settings()

# Debug 출력 (mypy 무시 가능)
print(" AWS_REGION:", settings.AWS_REGION)
print(" AWS_S3_BUCKET:", settings.AWS_S3_BUCKET)
