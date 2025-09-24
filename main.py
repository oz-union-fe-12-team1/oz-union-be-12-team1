from fastapi import FastAPI
from fastapi.routing import APIRouter
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any
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
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
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
app.include_router(schedules.router)   # 일정 API
app.include_router(todos.router)       # 할 일 API
app.include_router(inquiries.router)
#app.include_router(notifications.router)  # ✅ 빠져있던 notifications 추가
app.include_router(user_location.router)
app.include_router(weather.router)
app.include_router(quiz.router)        # 퀴즈 API
app.include_router(news.router)        # 뉴스 API
app.include_router(gemini.router)      # 제미나이 API


@app.get("/")
def root() -> Dict[str, str]:
    """Root endpoint for health check."""
    return {"message": "Hello, FastAPI is running!"}
