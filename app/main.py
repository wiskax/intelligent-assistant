# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth
from app.core.database import engine, Base
from app.api import auth, documents, chat, system
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api import auth, documents, rag
# 创建数据库表（开发环境可用，生产环境建议用 Alembic）
# 注意：这里只执行创建表，不会删除已有表
async def init_db():
    async with engine.begin() as conn:
        # 使用 sqlalchemy 的 create_all，生产环境建议用 Alembic 迁移
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="Intelligent Work Assistant",
    description="多用户知识库 + 多智能体协作系统",
    version="0.1.0"
)

# 在 app 定义之后，路由之前添加
@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
    
# CORS 配置（开发环境允许所有）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(system.router)  # 新增
app.include_router(rag.router)  # 新增
@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Service is running"}