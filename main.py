from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.db import init_db, close_db

# 라우터 import
from api.v1 import (
    auth,
    admin,
    users,
    todos,
    schedules,
    notifications,
    inquiries,
    user_location,
    weather,
    quiz,
    news,
    gemini,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        yield
    finally:
        await close_db()

app = FastAPI(lifespan=lifespan)

# 라우터 등록
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(schedules.router)  #  일정 API 추가
app.include_router(todos.router)      #  할 일 API 추가
app.include_router(inquiries.router)
app.include_router(schedules.router)
app.include_router(todos.router)
app.include_router(user_location.router)

app.include_router(weather.router)
app.include_router(quiz.router)       # 퀴즈 API
app.include_router(news.router)       # 뉴스 API
app.include_router(gemini.router)     # 제미나이 API


@app.get("/")
def root():
    return {"message": "Hello, FastAPI is running!"}
