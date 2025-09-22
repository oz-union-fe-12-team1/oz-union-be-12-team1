import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class Settings:
    # ==============================
    # Database 설정
    # ==============================
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    #  Tortoise ORM 
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    # ==============================
    # Google 서비스 계정
    # ==============================
    GOOGLE_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "google-credentials.json")
    GOOGLE_SPREADSHEET_ID: str = os.getenv("GOOGLE_SPREADSHEET_ID", "")
    GOOGLE_SHEET_NAME: str = os.getenv("GOOGLE_SHEET_NAME", "")

    # ==============================
    # Gemini API (Google Generative Language)
    # ==============================
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    GEMINI_URL: str = (
        f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        if GEMINI_API_KEY else None
    )

    # ==============================
    # OpenWeather API
    # ==============================
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY")

    # ==============================
    # 앱 환경 설정
    # ==============================
    PYTHONUNBUFFERED: str = os.getenv("PYTHONUNBUFFERED", "1")


# 전역에서 import 해서 쓰도록 인스턴스 생성
settings = Settings()
