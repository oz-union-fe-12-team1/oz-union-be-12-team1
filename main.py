from typing import AsyncIterator, Dict
from starlette.middleware.cors import CORSMiddleware
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
    inquiries,
    user_location,
    weather,
    quiz,
    news,
    gemini,
    google_auth
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await init_db()
    try:
        yield
    finally:
        await close_db()

app = FastAPI(lifespan=lifespan)

origins = [
    # 로컬 개발
    "http://localhost:5173",
    "https://localhost:5173",
    "http://0.0.0.0:8000/docs",

    # EC2 퍼블릭 IP (http/https 둘 다)
    "http://3.24.190.187:8000",
    "https://3.24.190.187:8000",

    # 프론트 Vercel 배포 도메인
    "https://nyangnyang.vercel.app",
    "https://develop-nyangnyang.vercel.app",

    # 커스텀 도메인 (www 유무 + http/https)
    "http://nyangbiseo.store",
    "https://nyangbiseo.store",
    "http://www.nyangbiseo.store",
    "https://www.nyangbiseo.store",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # 주소
    allow_methods=["*"], #crud
    allow_headers=["*"], #헤더
    allow_credentials=True,#인증서
)

#로드밸런서 대상그룹 헬스채크 포인트

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


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
app.include_router(google_auth.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)