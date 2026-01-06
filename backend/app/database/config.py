"""
CampusAssetManager/backend/app/database/config.py
数据库配置模块

功能说明：
- 定义数据库连接配置
- 提供数据库会话管理
- 配置SQLite数据库路径

设计原则：
- 声明式：通过类属性定义配置
- 封装清晰：提供简洁的数据库访问接口

作者：CampusAssetManager开发团队
日期：2025-01-05
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# SQLite数据库文件路径
DATABASE_URL = "sqlite:///./campus_asset.db"

# 创建数据库引擎
# connect_args 参数仅用于SQLite，解决多线程问题
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # 设置为True可查看SQL执行日志
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建声明式基类
# 所有ORM模型都将继承此类
Base = declarative_base()


def get_db() -> Session:
    """
    获取数据库会话
    
    这是一个依赖注入函数，用于在FastAPI路由中获取数据库会话。
    使用yield确保在请求结束后自动关闭会话。
    
    Yields:
        Session: SQLAlchemy数据库会话对象
        
    Examples:
        >>> @app.get("/users")
        >>> def get_users(db: Session = Depends(get_db)):
        >>>     users = db.query(User).all()
        >>>     return users
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()