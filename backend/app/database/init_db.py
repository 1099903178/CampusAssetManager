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

作者：CampusAssetManager开发团队
日期：2025-01-05
"""

from sqlalchemy.orm import Session
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
from ..core.security import get_password_hash


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


def create_test_users(db: Session):
    """
    创建测试用户
    
    Args:
        db (Session): 数据库会话
    
    说明：
        - admin/admin123 (超级管理员)
        - user/user123 (普通用户)
    """
    # 检查是否已存在admin用户
    existing_admin = db.query(User).filter(User.username == "admin").first()
    
    if not existing_admin:
        # 创建超级管理员
        admin = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            real_name="系统管理员",
            role="super_admin",
            phone="13800138000",
            email="admin@campus.edu",
            is_active=True
        )
        db.add(admin)
        print("[OK] 创建超级管理员用户: admin/admin123")
    
    # 检查是否已存在test用户
    existing_test = db.query(User).filter(User.username == "test").first()
    
    if not existing_test:
        # 创建测试用户
        test_user = User(
            username="test",
            password_hash=get_password_hash("test123"),
            real_name="测试用户",
            role="user",
            phone="13900139000",
            email="test@campus.edu",
            is_active=True
        )
        db.add(test_user)
        print("[OK] 创建测试用户: test/test123")
    
    # 提交更改
    db.commit()


def create_test_categories(db: Session):
    """
    创建测试分类
    
    Args:
        db (Session): 数据库会话
    
    说明：
        - 创建与导入模板示例数据匹配的分类
    """
    # 检查是否已存在分类数据
    existing_categories = db.query(GoodsCategory).all()
    
    if not existing_categories:
        # 创建办公设备分类
        category_sb = GoodsCategory(
            category_name="办公设备",
            category_code="BG_SB",
            parent_id=None,
            level=1,
            description="办公用品设备",
            sort_order=1,
            is_active=1
        )
        db.add(category_sb)
        print("[OK] 创建分类: 办公设备 (BG_SB)")
        
        # 创建电子设备分类
        category_dp = GoodsCategory(
            category_name="电子设备",
            category_code="BG_DP",
            parent_id=None,
            level=1,
            description="电子数码设备",
            sort_order=2,
            is_active=1
        )
        db.add(category_dp)
        print("[OK] 创建分类: 电子设备 (BG_DP)")
        
        # 提交更改
        db.commit()


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
        
        # 创建会话
        db = Session(bind=engine)
        
        try:
            # 创建测试用户
            create_test_users(db)
            # 创建测试分类
            create_test_categories(db)
        finally:
            # 关闭会话
            db.close()
        
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