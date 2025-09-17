from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.db import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        yield
    finally:
        await close_db()


app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "Hello, FastAPI is running!"}