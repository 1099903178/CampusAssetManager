"""
CampusAssetManager/backend/verify_models.py
模型验证脚本

功能说明：
- 验证所有ORM模型是否正确导入
- 测试数据库连接和初始化
- 验证表结构创建

使用方法：
    python backend/verify_models.py

作者：CampusAssetManager开发团队
日期：2025-01-05
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def verify_imports():
    """
    验证所有模型是否可以正确导入
    
    Returns:
        bool: 所有模型导入成功返回True，否则返回False
    """
    print("1. 验证模型导入...")
    
    try:
        from app.models import (
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
        print("   [OK] 所有模型导入成功")
        return True
    except ImportError as e:
        print(f"   [FAIL] 模型导入失败: {e}")
        return False


def verify_database_config():
    """
    验证数据库配置
    
    Returns:
        bool: 数据库配置正确返回True，否则返回False
    """
    print("2. 验证数据库配置...")
    
    try:
        from app.database.config import engine, Base, get_db
        print("   [OK] 数据库配置正确")
        return True
    except Exception as e:
        print(f"   [FAIL] 数据库配置失败: {e}")
        return False


def verify_table_structure():
    """
    验证表结构
    
    Returns:
        bool: 表结构验证成功返回True，否则返回False
    """
    print("3. 验证表结构...")
    
    try:
        from app.database.config import Base
        from app.models import (
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
        
        # 预期的表名列表
        expected_tables = [
            "sys_user",
            "goods_category",
            "goods_info",
            "stock_info",
            "stock_in",
            "stock_out",
            "stock_check",
            "sys_operation_log",
            "sys_config"
        ]
        
        # 获取实际的表名列表
        actual_tables = list(Base.metadata.tables.keys())
        
        # 验证表数量
        if len(actual_tables) != len(expected_tables):
            print(f"   [FAIL] 表数量不正确: 期望{len(expected_tables)}个，实际{len(actual_tables)}个")
            return False
        
        # 验证表名
        missing_tables = set(expected_tables) - set(actual_tables)
        extra_tables = set(actual_tables) - set(expected_tables)
        
        if missing_tables:
            print(f"   [FAIL] 缺少表: {', '.join(missing_tables)}")
            return False
        
        if extra_tables:
            print(f"   [FAIL] 额外表: {', '.join(extra_tables)}")
            return False
        
        print(f"   [OK] 表结构验证通过 ({len(expected_tables)}个表)")
        return True
        
    except Exception as e:
        print(f"   [FAIL] 表结构验证失败: {e}")
        return False


def verify_field_structure():
    """
    验证关键字段结构
    
    Returns:
        bool: 字段结构验证成功返回True，否则返回False
    """
    print("4. 验证关键字段...")
    
    try:
        from app.models import User, Goods, Stock
        
        # 验证User表关键字段
        user_fields = ['user_id', 'username', 'password_hash', 'real_name', 'role']
        for field in user_fields:
            if not hasattr(User, field):
                print(f"   [FAIL] User表缺少字段: {field}")
                return False
        
        # 验证Goods表关键字段
        goods_fields = ['goods_id', 'goods_name', 'goods_code', 'category_id', 'unit']
        for field in goods_fields:
            if not hasattr(Goods, field):
                print(f"   [FAIL] Goods表缺少字段: {field}")
                return False
        
        # 验证Stock表关键字段
        stock_fields = ['stock_id', 'goods_id', 'current_stock', 'total_value']
        for field in stock_fields:
            if not hasattr(Stock, field):
                print(f"   [FAIL] Stock表缺少字段: {field}")
                return False
        
        print("   [OK] 关键字段验证通过")
        return True
        
    except Exception as e:
        print(f"   [FAIL] 字段结构验证失败: {e}")
        return False


def test_database_initialization():
    """
    测试数据库初始化
    
    Returns:
        bool: 数据库初始化成功返回True，否则返回False
    """
    print("5. 测试数据库初始化...")
    
    try:
        from app.database import init_db
        init_db.init_database()
        print("   [OK] 数据库初始化成功")
        return True
    except Exception as e:
        print(f"   [FAIL] 数据库初始化失败: {e}")
        return False


def main():
    """
    主函数
    
    执行所有验证测试，并输出验证结果。
    """
    print("=" * 60)
    print("开始验证数据库和模型层...")
    print("=" * 60)
    print()
    
    # 执行所有验证测试
    results = []
    results.append(verify_imports())
    results.append(verify_database_config())
    results.append(verify_table_structure())
    results.append(verify_field_structure())
    results.append(test_database_initialization())
    
    print()
    print("=" * 60)
    
    # 输出验证结果
    if all(results):
        print("[OK] 所有验证通过！数据库和模型层创建成功。")
        return 0
    else:
        print("[FAIL] 部分验证失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())