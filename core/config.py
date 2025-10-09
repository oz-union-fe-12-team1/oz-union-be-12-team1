from typing import Any
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ==============================
    # CORS
    # ==============================
    CORS_ALLOW_ORIGINS: list[str] = Field(default=["*"], description="CORS 허용 도메인")

    # ==============================
    # JWT / Token
    # ==============================
    SECRET_KEY: str = Field(default="please_change_me_32+chars", description="JWT Secret Key")
    ALGORITHM: str = Field(default="HS256", description="암호화 알고리즘")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access Token 만료 시간(분)")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh Token 만료 기간(일)")

    # ==============================
    # Database
    # ==============================
    POSTGRES_USER: str = Field(default="postgres", description="DB 사용자명")
    POSTGRES_PASSWORD: str = Field(default="postgres", description="DB 비밀번호")
    POSTGRES_DB: str = Field(default="postgres", description="DB 이름")
    POSTGRES_HOST: str = Field(default="db", description="DB 호스트명")
    POSTGRES_PORT: int = Field(default=5432, description="DB 포트")
    DATABASE_URL: str | None = Field(default=None, description="DB 연결 URL")

    # ==============================
    # Gemini (Google Generative AI)
    # ==============================
    GEMINI_API_KEY: str = Field(default="", description="Gemini API Key")
    GEMINI_URL: str = Field(
        default="https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent",
        description="Gemini API 기본 URL"
    )

    # ==============================
    # OpenWeather
    # ==============================
    OPENWEATHER_API_KEY: str = Field(default="", description="OpenWeather API Key")

    # ==============================
    # Mail
    # ==============================
    MAIL_USERNAME: str = Field(default="", description="메일 계정")
    MAIL_PASSWORD: str = Field(default="", description="메일 비밀번호")
    MAIL_FROM: str | None = Field(default=None, description="발신 이메일 주소")
    MAIL_PORT: int = Field(default=587, description="메일 포트 번호")
    MAIL_SERVER: str = Field(default="smtp.gmail.com", description="메일 서버 주소")
    MAIL_STARTTLS: bool = Field(default=True, description="STARTTLS 사용 여부")
    MAIL_SSL_TLS: bool = Field(default=False, description="SSL/TLS 사용 여부")
    USE_CREDENTIALS: bool = Field(default=True, description="메일 인증 필요 여부")
    VALIDATE_CERTS: bool = Field(default=True, description="인증서 유효성 검사 여부")

    # ==============================
    # AWS S3 (Presigned URL)
    # ==============================
    AWS_ACCESS_KEY_ID: str = Field(default="", description="AWS Access Key")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", description="AWS Secret Key")
    AWS_REGION: str = Field(default="ap-northeast-2", description="AWS 리전")
    AWS_S3_BUCKET: str = Field(default="nyangbucket", description="S3 버킷 이름")

    # ==============================
    # Environment
    # ==============================
    PYTHONUNBUFFERED: int = Field(default=1, description="버퍼링 비활성화")

    # ==============================
    # Google Login (Optional)
    # ==============================
    GOOGLE_CLIENT_ID: str | None = Field(default=None, description="Google Client ID")
    GOOGLE_SECRET: str | None = Field(default=None, description="Google Secret")
    GOOGLE_REDIRECT_URI: str | None = Field(default=None, description="Google Redirect URI")

    # ==============================
    # Pydantic Settings Config
    # ==============================
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }

    # ==============================
    # Dynamic Post Init
    # ==============================
    def model_post_init(self, __context: Any) -> None:
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        if self.MAIL_FROM is None:
            self.MAIL_FROM = self.MAIL_USERNAME


settings = Settings()

print("AWS_ACCESS_KEY_ID:", settings.AWS_ACCESS_KEY_ID[:6] + "********")
print("AWS_REGION:", settings.AWS_REGION)