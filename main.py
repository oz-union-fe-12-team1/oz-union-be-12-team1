from typing import AsyncIterator, Dict
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from core.db import init_db, close_db

# ==================================================
# 라우터 import
# ==================================================
from api.v1 import (
    auth,
    admin,
    users,
    todos,
    schedules,
    inquiries,
    user_location,
    weather,
    quiz,
    news,
    gemini,
    google_auth,
    s3,  
)

# ==================================================
# Lifespan (DB 연결 관리)
# ==================================================
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await init_db()
    try:
        yield
    finally:
        await close_db()


# ==================================================
# 앱 생성
# ==================================================
app = FastAPI(lifespan=lifespan)

# ==================================================
# CORS 설정
# ==================================================
origins = [
    # 로컬 개발
    "http://localhost:5173",
    "https://localhost:5173",
    "http://0.0.0.0:8000/docs",

    # EC2 퍼블릭 IP
    "http://3.24.190.187:8000",
    "https://3.24.190.187:8000",

    # 프론트 Vercel 배포
    "https://nyangnyang.vercel.app",
    "https://develop-nyangnyang.vercel.app",

    # 커스텀 도메인
    "http://nyangbiseo.store",
    "https://nyangbiseo.store",
    "http://www.nyangbiseo.store",
    "https://www.nyangbiseo.store",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ==================================================
# Health Check
# ==================================================
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# ==================================================
# 라우터 등록
# ==================================================
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(schedules.router)
app.include_router(todos.router)
app.include_router(inquiries.router)
app.include_router(user_location.router)
app.include_router(weather.router)
app.include_router(quiz.router)
app.include_router(news.router)
app.include_router(gemini.router)
app.include_router(google_auth.router)
app.include_router(s3.router)  


# ==================================================
# 로컬 실행
# ==================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
