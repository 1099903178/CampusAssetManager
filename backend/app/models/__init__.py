"""
CampusAssetManager/backend/app/models/__init__.py
ORM模型模块导出文件

功能说明：
- 导出所有ORM模型类
- 提供统一的模型访问接口

设计原则：
- 封装清晰：通过__init__.py导出公共接口

作者：CampusAssetManager开发团队
日期：2025-01-05
"""

from .sys_user import User
from .goods_category import GoodsCategory
from .goods_info import Goods
from .stock_info import Stock
from .stock_in import StockIn
from .stock_out import StockOut
from .stock_check import StockCheck
from .sys_operation_log import OperationLog
from .sys_config import Config

__all__ = [
    "User",
    "GoodsCategory",
    "Goods",
    "Stock",
    "StockIn",
    "StockOut",
    "StockCheck",
    "OperationLog",
    "Config",
]