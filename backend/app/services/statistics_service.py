"""
CampusAssetManager/backend/app/services/statistics_service.py
统计服务模块

功能说明：
- 获取系统数据概览统计
- 实时统计物品、库存、入库、出库等关键指标
- 预警物品统计

设计原则：
- 面向对象：使用StatisticsService类封装统计逻辑
- 声明式：使用SQLAlchemy ORM进行数据库查询
- 封装清晰：提供简洁的公共方法

作者：CampusAssetManager开发团队
日期：2026-01-09
"""

from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..models.goods_info import Goods
from ..models.stock_info import Stock
from ..models.stock_in import StockIn
from ..models.stock_out import StockOut
from ..schemas.statistics import StatisticsOverview


class StatisticsService:
    """
    统计服务类
    
    提供数据统计功能，包括物品总数、库存总数、今日入库、今日出库、预警数量等。
    """
    
    @staticmethod
    def get_statistics_overview(db: Session) -> StatisticsOverview:
        """
        获取数据概览统计
        
        统计内容：
        - 物品总数：状态正常的物品数量
        - 库存总数：所有物品的当前库存总和
        - 今日入库：今天创建的入库记录数量总和
        - 今日出库：今天创建的出库记录数量总和
        - 预警数量：当前库存低于最小阈值的物品数量
        
        Args:
            db (Session): 数据库会话
        
        Returns:
            StatisticsOverview: 数据概览统计结果
        
        Examples:
            >>> from app.database.config import SessionLocal
            >>> db = SessionLocal()
            >>> stats = StatisticsService.get_statistics_overview(db)
            >>> print(f"物品总数: {stats.total_goods}")
        """
        try:
            # 获取今天的日期（忽略时间部分）
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())
            
            # 1. 统计物品总数（状态为1表示正常）
            total_goods = db.query(Goods).filter(
                Goods.status == 1
            ).count()
            
            # 2. 统计库存总数（所有物品的current_stock总和）
            total_stock_result = db.query(
                func.sum(Stock.current_stock)
            ).scalar()
            total_stock = int(total_stock_result) if total_stock_result else 0
            
            # 3. 统计今日入库数量（今天创建的入库记录数量总和）
            today_stock_in_result = db.query(
                func.sum(StockIn.in_quantity)
            ).filter(
                StockIn.in_time >= today_start,
                StockIn.in_time <= today_end
            ).scalar()
            today_stock_in = int(today_stock_in_result) if today_stock_in_result else 0
            
            # 4. 统计今日出库数量（今天创建的出库记录数量总和）
            today_stock_out_result = db.query(
                func.sum(StockOut.out_quantity)
            ).filter(
                StockOut.out_time >= today_start,
                StockOut.out_time <= today_end
            ).scalar()
            today_stock_out = int(today_stock_out_result) if today_stock_out_result else 0
            
            # 5. 统计预警数量（当前库存低于最小阈值的物品数量）
            warning_count = db.query(Stock).filter(
                Stock.current_stock < Stock.min_stock
            ).count()
            
            # 构建统计数据对象
            statistics = StatisticsOverview(
                total_goods=total_goods,
                total_stock=total_stock,
                today_stock_in=today_stock_in,
                today_stock_out=today_stock_out,
                warning_count=warning_count,
                update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            return statistics
            
        except Exception as e:
            # 记录错误并重新抛出异常
            raise RuntimeError(f"获取统计数据失败: {str(e)}")