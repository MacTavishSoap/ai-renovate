"""FastAPI 入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import init_db
from .api import generations_router, users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时初始化数据库"""
    init_db()
    yield


app = FastAPI(
    title="AI 家装 API",
    version="0.1.0",
    lifespan=lifespan,
)

# 路由
app.include_router(users_router)
app.include_router(generations_router)


@app.get("/health")
async def health():
    """健康检查（Docker healthcheck 用）"""
    return {"status": "ok"}
