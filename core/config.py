import os
from dotenv import load_dotenv

# .env 로드
load_dotenv()


class Settings:
    # ==============================
    # JWT / 토큰
    # ==============================
    SECRET_KEY: str = os.getenv("SECRET_KEY") or "please_change_me_32+chars"
    ALGORITHM: str = os.getenv("ALGORITHM") or "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or 30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS") or 7)

    # ==============================
    # Database
    # ==============================
    POSTGRES_USER: str = os.getenv("POSTGRES_USER") or "postgres"
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD") or "postgres"
    POSTGRES_DB: str = os.getenv("POSTGRES_DB") or "postgres"
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST") or "db"
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT") or 5432)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL"
    ) or f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # ==============================
    # Google Sheets
    # ==============================
    GOOGLE_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE") or "google-credentials.json"
    GOOGLE_SPREADSHEET_ID: str = os.getenv("GOOGLE_SPREADSHEET_ID") or ""
    GOOGLE_SHEET_NAME: str = os.getenv("GOOGLE_SHEET_NAME") or "quiz"

    # ==============================
    # Gemini
    # ==============================
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY") or ""

    # ==============================
    # OpenWeather
    # ==============================
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY") or ""

    # ==============================
    # Mail (FastAPI-Mail)
    # ==============================
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME") or ""
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD") or ""
    MAIL_FROM: str = os.getenv("MAIL_FROM") or MAIL_USERNAME
    MAIL_PORT: int = int(os.getenv("MAIL_PORT") or 587)
    MAIL_SERVER: str = os.getenv("MAIL_SERVER") or "smtp.gmail.com"
    MAIL_STARTTLS: bool = (os.getenv("MAIL_STARTTLS") or "True").lower() == "true"
    MAIL_SSL_TLS: bool = (os.getenv("MAIL_SSL_TLS") or "False").lower() == "true"
    USE_CREDENTIALS: bool = (os.getenv("USE_CREDENTIALS") or "True").lower() == "true"
    VALIDATE_CERTS: bool = (os.getenv("VALIDATE_CERTS") or "True").lower() == "true"

    # ==============================
    # 앱 환경 설정
    # ==============================
    PYTHONUNBUFFERED: int = int(os.getenv("PYTHONUNBUFFERED") or 1)


# 전역 인스턴스
settings = Settings()
