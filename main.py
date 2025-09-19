from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.db import init_db, close_db

# 라우터 import 추가
from api.v1 import auth, users, todos, schedules, notifications, inquiries, weather, gemini

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        yield
    finally:
        await close_db()

app = FastAPI(lifespan=lifespan)

# ✅ 라우터 등록
app.include_router(auth.router)
#app.include_router(users.router)
#app.include_router(todos.router)
#app.include_router(schedules.router)
#app.include_router(notifications.router)
#app.include_router(inquiries.router)
#app.include_router(weather.router)
#app.include_router(gemini.router)

@app.get("/")
def root():
    return {"message": "Hello, FastAPI is running!"}
