import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.db import init_db, close_db

# 라우터 import 추가 (assistant 포함)
from api.v1 import news, weather, quiz, gemini, assistant


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    print("🚀 애플리케이션 시작: 데이터베이스 연결 중...")
    await init_db()
    print(" 데이터베이스 연결 완료")
    try:
        yield
    finally:
        print("🔌 애플리케이션 종료: 데이터베이스 연결 해제 중...")
        await close_db()
        print(" 데이터베이스 연결 해제 완료")


# FastAPI 앱 설정
app = FastAPI(
    title="Star API",
    description="개인 일정 관리 및 AI 어시스턴트 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 설정
cors_origins = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],  # 공백 제거
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(news.router, prefix="/api", tags=["📰 News"])
app.include_router(weather.router, prefix="/api", tags=["🌤️ Weather"])
app.include_router(quiz.router, prefix="/api", tags=["🧠 Quiz"])
app.include_router(gemini.router, prefix="/api", tags=["🤖 Gemini AI"])
app.include_router(assistant.router, prefix="/api", tags=["💬 Assistant"])  # 🔧 추가됨


# 🏠 기본 엔드포인트들
@app.get("/", tags=["🏠 Root"])
def root():
    """API 루트 엔드포인트"""
    return {
        "message": "Hello, Star API is running! ⭐",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "news": "/api/news",
            "weather": "/api/weather",
            "quiz": "/api/quiz", 
            "fortune": "/api/fortune",
            "briefings": "/api/briefings",
            "conversations": "/api/conversations",
            "assistant": "/api/assistant"
        }
    }


@app.get("/health", tags=["🏠 Root"])
def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "star-api",
        "version": "1.0.0",
        "database": "connected"
    }


@app.get("/api", tags=["🏠 Root"])
def api_info():
    """API 정보 엔드포인트"""
    return {
        "api_name": "Star API",
        "version": "1.0.0",
        "description": "개인 일정 관리 및 AI 어시스턴트 API",
        "available_endpoints": {
            "news": {
                "path": "/api/news",
                "description": "최신 뉴스 조회"
            },
            "weather": {
                "path": "/api/weather",
                "description": "날씨 정보 조회",
                "parameters": "lat, lon"
            },
            "quiz": {
                "path": "/api/quiz", 
                "description": "랜덤 퀴즈 조회"
            },
            "fortune": {
                "path": "/api/fortune",
                "description": "운세 조회",
                "parameters": "birthday"
            },
            "briefings": {
                "path": "/api/briefings",
                "description": "아침/저녁 브리핑",
                "parameters": "type (morning/evening)"
            },
            "conversations": {
                "path": "/api/conversations",
                "description": "AI 대화",
                "parameters": "message"
            },
            "assistant": {
                "path": "/api/assistant",
                "description": "AI 어시스턴트 채팅",
                "method": "POST"
            }
        },
        "docs_url": "/docs"
    }


# 예외 처리 (선택사항)
@app.exception_handler(500)
async def internal_server_error(request, exc):
    return {
        "error": "Internal Server Error",
        "message": "서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        "status_code": 500
    }


@app.exception_handler(404)
async def not_found_error(request, exc):
    return {
        "error": "Not Found", 
        "message": "요청하신 엔드포인트를 찾을 수 없습니다.",
        "status_code": 404,
        "available_endpoints": "/api"
    }