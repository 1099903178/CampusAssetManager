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

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from ...database.config import get_db
from ...services.statistics_service import StatisticsService
from .auth import get_current_user
from ...schemas.statistics import StatisticsOverview
from ...schemas.common import BaseResponse
from ...models.sys_user import User


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
    current_user: User = Depends(get_current_user)
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