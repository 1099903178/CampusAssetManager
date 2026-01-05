"""
CampusAssetManager/backend/app/database/init_db.py
数据库初始化脚本

功能说明：
- 初始化SQLite数据库
- 创建所有数据表
- 预置初始数据

设计原则：
- 声明式：使用SQLAlchemy ORM自动创建表结构
- 容错性：处理已存在的数据库

使用方法：
    python -m backend.app.database.init_db

作者：系统开发团队
日期：2025-01-05
"""

from sqlalchemy.exc import SQLAlchemyError
from .config import engine, Base
from ..models import (
    User,
    GoodsCategory,
    Goods,
    Stock,
    StockIn,
    StockOut,
    StockCheck,
    OperationLog,
    Config
)


def init_database():
    """
    初始化数据库
    
    创建所有数据表结构，如果表已存在则跳过。
    
    Raises:
        SQLAlchemyError: 数据库操作失败时抛出异常
        
    Examples:
        >>> init_database()
        >>> print("数据库初始化完成")
    """
    # 从Base类获取所有已注册的模型
    Base.metadata.create_all(bind=engine)
    print("[OK] 数据库表结构创建成功")


def main():
    """
    主函数
    
    执行数据库初始化操作，并输出初始化结果。
    """
    try:
        print("=" * 50)
        print("开始初始化数据库...")
        print("=" * 50)
        
        # 初始化数据库
        init_database()
        
        print("=" * 50)
        print("数据库初始化完成！")
        print("=" * 50)
        print(f"数据库文件位置: {engine.url}")
        print(f"已创建表数量: {len(Base.metadata.tables)}")
        print(f"表列表: {', '.join(Base.metadata.tables.keys())}")
        
    except SQLAlchemyError as e:
        print(f"✗ 数据库初始化失败: {str(e)}")
        raise
    except Exception as e:
        print(f"✗ 未知错误: {str(e)}")
        raise


if __name__ == "__main__":
    main()