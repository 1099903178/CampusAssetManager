"""
CampusAssetManager/backend/app/schemas/statistics.py
统计数据Schema模型

功能说明：
- 定义数据概览的响应结构
- 提供统计数据验证和序列化

设计原则：
- 声明式：使用Pydantic声明式定义数据结构
- 类型安全：使用类型提示确保数据类型正确

作者：CampusAssetManager开发团队
日期：2026-01-09
"""

from pydantic import BaseModel, Field
from typing import Optional


class StatisticsOverview(BaseModel):
    """
    数据概览响应模型
    
    包含物品总数、库存总数、今日入库、今日出库、预警数量等关键指标。
    """
    # 物品统计
    total_goods: int = Field(
        ...,
        description="物品总数（状态正常的物品数量）",
        example=150
    )
    
    # 库存统计
    total_stock: int = Field(
        ...,
        description="库存总数（所有物品的当前库存总和）",
        example=12500
    )
    
    # 今日入库
    today_stock_in: int = Field(
        ...,
        description="今日入库数量（今天创建的入库记录数量总和）",
        example=50
    )
    
    # 今日出库
    today_stock_out: int = Field(
        ...,
        description="今日出库数量（今天创建的出库记录数量总和）",
        example=30
    )
    
    # 预警统计
    warning_count: int = Field(
        ...,
        description="预警数量（当前库存低于最小阈值的物品数量）",
        example=5
    )
    
    # 时间戳
    update_time: Optional[str] = Field(
        None,
        description="数据更新时间",
        example="2026-01-09 12:00:00"
    )
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "total_goods": 150,
                "total_stock": 12500,
                "today_stock_in": 50,
                "today_stock_out": 30,
                "warning_count": 5,
                "update_time": "2026-01-09 12:00:00"
            }
        }