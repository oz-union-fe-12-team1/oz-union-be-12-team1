from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.db import init_db, close_db

# 라우터 import 추가
from app.api import news, weather, quiz, gemini


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        yield
    finally:
        await close_db()


app = FastAPI(lifespan=lifespan)

# 여기서 라우터 등록
app.include_router(news.router, prefix="/api", tags=["News"])
app.include_router(weather.router, prefix="/api", tags=["Weather"])
app.include_router(quiz.router, prefix="/api", tags=["Quiz"])
app.include_router(gemini.router, prefix="/api", tags=["Gemini"])


@app.get("/")
def root():
    return {"message": "Hello, FastAPI is running!"}
