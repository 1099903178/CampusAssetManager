"""
CampusAssetManager/backend/main.py
FastAPI主程序入口

功能说明：
- 应用程序初始化
- 路由注册
- 中间件配置
- CROS配置

设计原则：
- 声明式：使用FastAPI的装饰器定义路由
- 模块化：每个模块独立管理路由
- RESTful：遵循REST API设计规范

作者：CampusAssetManager开发团队
日期：2026-01-06
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.api.v1 import auth, users, goods, stock, system
from app.api.v1 import statistics
from app.database.config import engine, Base
from app.middleware.operation_log import OperationLogMiddleware

# ==================== 创建FastAPI应用 ====================

app = FastAPI(
    title="校物通校园物品量化管理系统",
    description="提供校园物品管理、库存管理等功能的API服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==================== CORS配置 ====================

# 配置跨域资源共享（CORS）
# 支持局域网访问：允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（支持局域网访问）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册操作日志记录中间件
app.add_middleware(OperationLogMiddleware)

# ==================== 路由注册 ====================

# 注册认证路由
app.include_router(
    auth.router,
    prefix="/v1",
    tags=["认证"]
)

# 注册用户管理路由
app.include_router(
    users.router,
    prefix="/v1",
    tags=["用户管理"]
)

# 注册物品管理路由
app.include_router(
    goods.router,
    prefix="/v1",
    tags=["物品管理"]
)

# 注册库存管理路由
app.include_router(
    stock.router,
    prefix="/v1",
    tags=["库存管理"]
)

# 注册系统管理路由
app.include_router(
    system.router,
    prefix="/v1",
    tags=["系统管理"]
)

# 注册统计路由
app.include_router(
    statistics.router,
    prefix="/v1",
    tags=["统计数据"]
)

# ==================== 数据库初始化 ====================

# 启动时创建数据库表（仅用于开发环境）
# 生产环境建议使用Alembic进行数据库迁移
@app.on_event("startup")
async def startup_event():
    """
    应用启动时的初始化事件
    
    创建所有数据库表
    """
    Base.metadata.create_all(bind=engine)


# ==================== 健康检查接口 ====================

@app.get("/", tags=["系统"])
def read_root():
    """
    根路径
    
    返回API基本信息
    """
    return {
        "message": "校物通校园物品量化管理系统API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["系统"])
def health_check():
    """
    健康检查接口
    
    返回服务健康状态
    """
    return {
        "status": "healthy",
        "service": "campus-asset-manager"
    }