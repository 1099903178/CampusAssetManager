"""
CampusAssetManager/backend/app/api/v1/statistics.py
统计数据API路由

功能说明：
- 提供数据概览统计API端点
- 获取系统关键指标统计数据

设计原则：
- RESTful API：遵循RESTful设计规范
- 依赖注入：使用FastAPI依赖注入系统
- 权限控制：要求用户登录认证

作者：CampusAssetManager开发团队
日期：2026-01-09
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from ...database.config import get_db
from ...services.statistics_service import StatisticsService
from ...schemas.statistics import (
    StatisticsOverview,
    StockTrendResponse,
    GoodsRankingResponse,
    CategoryStatsResponse
)
from ...schemas.common import BaseResponse
from ...schemas.user import UserResponse
from .auth import get_current_user


# 创建API路由器
router = APIRouter(
    prefix="/statistics",
    tags=["统计数据"]
)


@router.get(
    "/overview",
    summary="获取数据概览",
    description="获取系统数据概览，包括物品总数、库存总数、今日入库、今日出库、预警数量等关键指标"
)
async def get_statistics_overview(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> BaseResponse[StatisticsOverview]:
    """
    获取数据概览统计
    
    权限要求：所有登录用户都可以访问
    
    统计指标：
    - 物品总数：goods_info表中状态正常的记录数
    - 库存总数：stock_info表中所有物品的current_stock总和
    - 今日入库：stock_in表中今天创建的记录数量总和
    - 今日出库：stock_out表中今天创建的记录数量总和
    - 预警数量：stock_info表中current_stock < min_stock的物品数量
    
    Args:
        db (Session): 数据库会话（通过依赖注入）
        current_user (User): 当前登录用户（通过依赖注入）
    
    Returns:
        StatisticsOverview: 数据概览统计结果
    
    Raises:
        HTTPException: 当获取统计数据失败时抛出500错误
    
    Examples:
        GET /v1/statistics/overview
        
        响应示例：
        {
            "code": 200,
            "message": "成功",
            "data": {
                "total_goods": 150,
                "total_stock": 12500,
                "today_stock_in": 50,
                "today_stock_out": 30,
                "warning_count": 5,
                "update_time": "2026-01-09 12:00:00"
            }
        }
    """
    try:
        # 调用统计服务获取数据概览
        statistics = StatisticsService.get_statistics_overview(db)
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "成功",
            "data": statistics
        }
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
        
    except Exception as e:
        # 捕获其他异常并返回500错误
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计数据失败: {str(e)}"
        )


@router.get(
    "/stock-trend",
    summary="获取库存趋势",
    description="获取库存趋势数据，支持时间范围和物品筛选"
)
async def get_stock_trend(
    start_date: Optional[str] = Query(
        None,
        description="开始日期（YYYY-MM-DD格式），默认最近7天"
    ),
    end_date: Optional[str] = Query(
        None,
        description="结束日期（YYYY-MM-DD格式），默认今天"
    ),
    goods_id: Optional[int] = Query(
        None,
        description="物品ID（可选，不指定则统计整体库存）"
    ),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> BaseResponse[StockTrendResponse]:
    """
    获取库存趋势统计
    
    权限要求：所有登录用户都可以访问
    
    统计内容：
    - 库存趋势：按日期统计库存变化
    - 支持时间范围筛选（默认最近7天）
    - 支持按物品筛选（不指定则统计整体库存）
    
    Args:
        start_date (str): 开始日期
        end_date (str): 结束日期
        goods_id (int): 物品ID（可选）
        db (Session): 数据库会话
        current_user (User): 当前登录用户
    
    Returns:
        StockTrendResponse: 库存趋势统计结果
    
    Raises:
        HTTPException: 当获取趋势数据失败时抛出500错误
    
    Examples:
        GET /v1/statistics/stock-trend?start_date=2026-01-01&end_date=2026-01-09
        
        响应示例：
        {
            "code": 200,
            "message": "成功",
            "data": {
                "goods_id": null,
                "goods_name": null,
                "start_date": "2026-01-01",
                "end_date": "2026-01-09",
                "trend_data": [
                    {"date": "2026-01-01", "stock_quantity": 100},
                    {"date": "2026-01-02", "stock_quantity": 105}
                ]
            }
        }
    """
    try:
        # 调用统计服务获取库存趋势
        trend = StatisticsService.get_stock_trend(
            db, start_date, end_date, goods_id
        )
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "成功",
            "data": trend
        }
        
    except ValueError as e:
        # 参数验证错误
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
        
    except Exception as e:
        # 捕获其他异常并返回500错误
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取库存趋势失败: {str(e)}"
        )


@router.get(
    "/goods-ranking",
    summary="获取物品排行榜",
    description="获取物品排行榜，支持入库或出库排行榜"
)
async def get_goods_ranking(
    ranking_type: str = Query(
        "in",
        description="排行榜类型（in/入库，out/出库）"
    ),
    top_n: int = Query(
        10,
        ge=1,
        le=100,
        description="Top N数量（1-100）"
    ),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> BaseResponse[GoodsRankingResponse]:
    """
    获取物品排行榜统计
    
    权限要求：所有登录用户都可以访问
    
    统计内容：
    - 物品入库排行榜：入库数量最多的Top N物品
    - 物品出库排行榜：出库数量最多的Top N物品
    
    Args:
        ranking_type (str): 排行榜类型（in/入库，out/出库）
        top_n (int): Top N数量
        db (Session): 数据库会话
        current_user (User): 当前登录用户
    
    Returns:
        GoodsRankingResponse: 物品排行榜统计结果
    
    Raises:
        HTTPException: 当获取排行榜数据失败时抛出500错误
    
    Examples:
        GET /v1/statistics/goods-ranking?ranking_type=in&top_n=10
        
        响应示例：
        {
            "code": 200,
            "message": "成功",
            "data": {
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
    """
    try:
        # 调用统计服务获取物品排行榜
        ranking = StatisticsService.get_goods_ranking(
            db, ranking_type, top_n
        )
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "成功",
            "data": ranking
        }
        
    except ValueError as e:
        # 参数验证错误
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
        
    except Exception as e:
        # 捕获其他异常并返回500错误
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取物品排行榜失败: {str(e)}"
        )


@router.get(
    "/category-stats",
    summary="获取分类统计",
    description="获取分类统计，支持库存数量或入库数量统计"
)
async def get_category_stats(
    stats_type: str = Query(
        "stock",
        description="统计类型（stock/库存，in/入库）"
    ),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
) -> BaseResponse[CategoryStatsResponse]:
    """
    获取分类统计
    
    权限要求：所有登录用户都可以访问
    
    统计内容：
    - 按库存数量统计：各分类的当前库存数量
    - 按入库数量统计：本月各分类的入库数量
    
    Args:
        stats_type (str): 统计类型（stock/库存，in/入库）
        db (Session): 数据库会话
        current_user (User): 当前登录用户
    
    Returns:
        CategoryStatsResponse: 分类统计结果
    
    Raises:
        HTTPException: 当获取分类统计失败时抛出500错误
    
    Examples:
        GET /v1/statistics/category-stats?stats_type=stock
        
        响应示例：
        {
            "code": 200,
            "message": "成功",
            "data": {
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
    """
    try:
        # 调用统计服务获取分类统计
        stats = StatisticsService.get_category_stats(
            db, stats_type
        )
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "成功",
            "data": stats
        }
        
    except ValueError as e:
        # 参数验证错误
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except HTTPException:
        # 重新抛出HTTP异常
        raise
        
    except Exception as e:
        # 捕获其他异常并返回500错误
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分类统计失败: {str(e)}"
        )