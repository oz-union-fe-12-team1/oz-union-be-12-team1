import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # 🔐 JWT / 토큰 관련
    SECRET_KEY: str = os.getenv("SECRET_KEY", "please_change_me_32+chars")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

settings = Settings()
