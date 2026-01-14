"""
CampusAssetManager/backend/app/schemas/statistics.py
统计数据Schema模型

功能说明：
- 定义数据概览的响应结构
- 提供统计数据验证和序列化
- 定义库存趋势、排行榜、分类统计的数据模型

设计原则：
- 声明式：使用Pydantic声明式定义数据结构
- 类型安全：使用类型提示确保数据类型正确

作者：CampusAssetManager开发团队
日期：2026-01-09
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class StockAlertItem(BaseModel):
    """
    库存预警数据项模型
    """
    goods_id: int = Field(
        ...,
        description="物品ID",
        example=1
    )
    
    goods_name: str = Field(
        ...,
        description="物品名称",
        example="笔记本电脑"
    )
    
    current_stock: int = Field(
        ...,
        description="当前库存",
        example=5
    )
    
    min_stock: int = Field(
        ...,
        description="安全库存（最小库存阈值）",
        example=10
    )
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "goods_id": 1,
                "goods_name": "笔记本电脑",
                "current_stock": 5,
                "min_stock": 10
            }
        }


class StockAlertResponse(BaseModel):
    """
    库存预警响应模型
    """
    alert_list: List[StockAlertItem] = Field(
        ...,
        description="库存预警列表"
    )
    
    total_count: int = Field(
        ...,
        description="预警总数",
        example=5
    )
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "alert_list": [
                    {
                        "goods_id": 1,
                        "goods_name": "笔记本电脑",
                        "current_stock": 5,
                        "min_stock": 10
                    }
                ],
                "total_count": 1
            }
        }


class StatisticsOverview(BaseModel):
    """
    数据概览响应模型
    
    包含物品总数、库存总数、今日入库、今日出库、预警数量等关键指标。
    """
    # 物品统计
    total_goods: int = Field(
        ...,
        description="物品总数（所有状态的物品数量）",
        example=150
    )
    
    # 物品统计（正常物品）
    total_goods_normal: int = Field(
        ...,
        description="正常物品总数（状态正常的物品数量）",
        example=120
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


class StockTrendItem(BaseModel):
    """
    库存趋势数据项模型
    """
    date: str = Field(
        ...,
        description="日期（YYYY-MM-DD格式）",
        example="2026-01-09"
    )
    
    stock_quantity: int = Field(
        ...,
        description="库存数量",
        example=100
    )
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "date": "2026-01-09",
                "stock_quantity": 100
            }
        }


class StockTrendResponse(BaseModel):
    """
    库存趋势响应模型
    """
    goods_id: Optional[int] = Field(
        None,
        description="物品ID（筛选特定物品时有值）",
        example=1
    )
    
    goods_name: Optional[str] = Field(
        None,
        description="物品名称（筛选特定物品时有值）",
        example="笔记本电脑"
    )
    
    start_date: str = Field(
        ...,
        description="开始日期",
        example="2026-01-01"
    )
    
    end_date: str = Field(
        ...,
        description="结束日期",
        example="2026-01-09"
    )
    
    trend_data: List[StockTrendItem] = Field(
        ...,
        description="趋势数据列表"
    )
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "goods_id": 1,
                "goods_name": "笔记本电脑",
                "start_date": "2026-01-01",
                "end_date": "2026-01-09",
                "trend_data": [
                    {"date": "2026-01-01", "stock_quantity": 100},
                    {"date": "2026-01-02", "stock_quantity": 105},
                    {"date": "2026-01-03", "stock_quantity": 103}
                ]
            }
        }


class GoodsRankingItem(BaseModel):
    """
    物品排行榜数据项模型
    """
    rank: int = Field(
        ...,
        description="排名",
        example=1
    )
    
    goods_id: int = Field(
        ...,
        description="物品ID",
        example=1
    )
    
    goods_name: str = Field(
        ...,
        description="物品名称",
        example="笔记本电脑"
    )
    
    goods_code: str = Field(
        ...,
        description="物品编码",
        example="G001"
    )
    
    total_quantity: int = Field(
        ...,
        description="总数量",
        example=500
    )
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "rank": 1,
                "goods_id": 1,
                "goods_name": "笔记本电脑",
                "goods_code": "G001",
                "total_quantity": 500
            }
        }


class GoodsRankingResponse(BaseModel):
    """
    物品排行榜响应模型
    """
    ranking_type: str = Field(
        ...,
        description="排行榜类型（in/入库，out/出库）",
        example="in"
    )
    
    top_n: int = Field(
        ...,
        description="Top N",
        example=10
    )
    
    ranking_list: List[GoodsRankingItem] = Field(
        ...,
        description="排行榜列表"
    )
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "ranking_type": "in",
                "top_n": 10,
                "ranking_list": [
                    {
                        "rank": 1,
                        "goods_id": 1,
                        "goods_name": "笔记本电脑",
                        "goods_code": "G001",
                        "total_quantity": 500
                    }
                ]
            }
        }


class CategoryStatsItem(BaseModel):
    """
    分类统计数据项模型
    """
    category_id: int = Field(
        ...,
        description="分类ID",
        example=1
    )
    
    category_name: str = Field(
        ...,
        description="分类名称",
        example="电子设备"
    )
    
    category_code: str = Field(
        ...,
        description="分类编码",
        example="C001"
    )
    
    stock_quantity: int = Field(
        ...,
        description="库存数量",
        example=1000
    )
    
    in_quantity: int = Field(
        ...,
        description="入库数量",
        example=500
    )
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "category_id": 1,
                "category_name": "电子设备",
                "category_code": "C001",
                "stock_quantity": 1000,
                "in_quantity": 500
            }
        }


class CategoryStatsResponse(BaseModel):
    """
    分类统计响应模型
    """
    stats_type: str = Field(
        ...,
        description="统计类型（stock/库存，in/入库）",
        example="stock"
    )
    
    category_stats: List[CategoryStatsItem] = Field(
        ...,
        description="分类统计列表"
    )
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "stats_type": "stock",
                "category_stats": [
                    {
                        "category_id": 1,
                        "category_name": "电子设备",
                        "category_code": "C001",
                        "stock_quantity": 1000,
                        "in_quantity": 500
                    }
                ]
            }
        }