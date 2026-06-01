"""
供应商付款查询系统 — FastAPI 主入口
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    from backend.database import init_db
    init_db()
    logger.info("✅ 数据库初始化完成")
    logger.info(f"🚀 供应商付款查询系统已启动")
    yield
    logger.info("👋 服务器关闭")


app = FastAPI(
    title="供应商付款查询系统",
    description="AI 驱动的财务智能助手 — 支持自然语言查询供应商付款信息",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from backend.routers.payments import router as payments_router
app.include_router(payments_router)

# 挂载前端静态文件
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "供应商付款查询系统", "version": "1.0.0"}
