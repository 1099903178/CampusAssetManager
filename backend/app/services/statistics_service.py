"""
CampusAssetManager/backend/app/services/statistics_service.py
统计服务模块

功能说明：
- 获取系统数据概览统计
- 实时统计物品、库存、入库、出库等关键指标
- 预警物品统计
- 库存趋势统计
- 物品排行榜统计
- 分类统计

设计原则：
- 面向对象：使用StatisticsService类封装统计逻辑
- 声明式：使用SQLAlchemy ORM进行数据库查询
- 封装清晰：提供简洁的公共方法
- 时区统一：使用UTC时间进行所有时间计算，避免时区混淆

作者：CampusAssetManager开发团队
日期：2026-01-09
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import func, and_, desc
from sqlalchemy.orm import Session, joinedload
from ..models.goods_info import Goods
from ..models.goods_category import GoodsCategory
from ..models.stock_info import Stock
from ..models.stock_in import StockIn
from ..models.stock_out import StockOut
from ..schemas.statistics import (
    StatisticsOverview,
    StockTrendResponse,
    StockTrendItem,
    GoodsRankingResponse,
    GoodsRankingItem,
    CategoryStatsResponse,
    CategoryStatsItem,
    StockAlertResponse,
    StockAlertItem
)


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
            # 使用UTC时间获取今天的日期（避免时区混淆）
            utc_now = datetime.now(timezone.utc)
            today_utc = utc_now.date()
            today_start = datetime.combine(today_utc, datetime.min.time()).replace(tzinfo=timezone.utc)
            today_end = datetime.combine(today_utc, datetime.max.time()).replace(tzinfo=timezone.utc)
            
            # 1. 统计物品总数（所有状态的物品）
            total_goods_all = db.query(Goods).count()
            
            # 2. 统计正常物品总数（状态为1表示正常）
            total_goods_normal = db.query(Goods).filter(
                Goods.status == 1
            ).count()
            
            # 3. 统计库存总数（所有物品的current_stock总和）
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
            
            # 构建统计数据对象（使用UTC时间）
            statistics = StatisticsOverview(
                total_goods=total_goods_all,
                total_goods_normal=total_goods_normal,
                total_stock=total_stock,
                today_stock_in=today_stock_in,
                today_stock_out=today_stock_out,
                warning_count=warning_count,
                update_time=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            )
            
            return statistics
            
        except Exception as e:
            # 记录错误并重新抛出异常
            raise RuntimeError(f"获取统计数据失败: {str(e)}")
    
    @staticmethod
    def get_stock_trend(
        db: Session,
        start_date: str = None,
        end_date: str = None,
        goods_id: int = None
    ) -> StockTrendResponse:
        """
        获取库存趋势统计
        
        统计指定时间范围内的库存变化趋势，支持按物品筛选。
        如果不指定物品，则统计整体库存趋势。
        
        Args:
            db (Session): 数据库会话
            start_date (str): 开始日期（YYYY-MM-DD格式）
            end_date (str): 结束日期（YYYY-MM-DD格式）
            goods_id (int): 物品ID（可选）
        
        Returns:
            StockTrendResponse: 库存趋势统计结果
        
        Raises:
            ValueError: 日期格式错误
            RuntimeError: 查询失败
        
        Examples:
            >>> from app.database.config import SessionLocal
            >>> db = SessionLocal()
            >>> trend = StatisticsService.get_stock_trend(
            ...     db, "2026-01-01", "2026-01-09", goods_id=1
            ... )
        """
        try:
            # 默认时间范围为最近7天（使用UTC时间）
            if not start_date:
                start_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
            if not end_date:
                end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            
            # 验证日期格式
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("日期格式错误，请使用YYYY-MM-DD格式")
            
            # 获取物品信息（如果指定了物品ID）
            goods_info = None
            if goods_id:
                goods_info = db.query(Goods).filter(
                    Goods.goods_id == goods_id
                ).first()
                if not goods_info:
                    raise ValueError(f"物品ID {goods_id} 不存在")
            
            # 生成日期列表
            date_list = []
            current_date = start_dt
            while current_date <= end_dt:
                date_list.append(current_date.strftime("%Y-%m-%d"))
                current_date += timedelta(days=1)
            
            # 查询每个日期的库存情况（基于入库和出库记录计算）
            trend_data = []
            for date_str in date_list:
                query_start = datetime.strptime(date_str, "%Y-%m-%d").replace(
                    hour=0, minute=0, second=0
                )
                query_end = query_start.replace(hour=23, minute=59, second=59)
                
                # 计算该日期的库存
                if goods_id:
                    # 查询指定物品的库存
                    # 库存 = (该日期之前的入库总量 + 当前初始库存) - (该日期之前的出库总量)
                    # 这里简化计算：使用当前库存减去该日期之后的入库出库变动
                    # 更准确的方法是：计算该日期结束时的入库和出库累积
                    
                    # 查询该日期及之前的入库总量
                    in_sum_result = db.query(
                        func.sum(StockIn.in_quantity)
                    ).filter(
                        StockIn.goods_id == goods_id,
                        StockIn.in_time <= query_end
                    ).scalar()
                    total_in = int(in_sum_result) if in_sum_result else 0
                    
                    # 查询该日期及之前的出库总量
                    out_sum_result = db.query(
                        func.sum(StockOut.out_quantity)
                    ).filter(
                        StockOut.goods_id == goods_id,
                        StockOut.out_time <= query_end
                    ).scalar()
                    total_out = int(out_sum_result) if out_sum_result else 0
                    
                    # 库存 = 入库 - 出库
                    stock_quantity = total_in - total_out
                    if stock_quantity < 0:
                        stock_quantity = 0
                else:
                    # 查询所有物品的库存总和
                    # 库存 = (所有物品的入库总量) - (所有物品的出库总量)
                    in_sum_result = db.query(
                        func.sum(StockIn.in_quantity)
                    ).filter(
                        StockIn.in_time <= query_end
                    ).scalar()
                    total_in = int(in_sum_result) if in_sum_result else 0
                    
                    out_sum_result = db.query(
                        func.sum(StockOut.out_quantity)
                    ).filter(
                        StockOut.out_time <= query_end
                    ).scalar()
                    total_out = int(out_sum_result) if out_sum_result else 0
                    
                    stock_quantity = total_in - total_out
                    if stock_quantity < 0:
                        stock_quantity = 0
                
                trend_data.append(StockTrendItem(
                    date=date_str,
                    stock_quantity=stock_quantity
                ))
            
            # 构建响应
            response = StockTrendResponse(
                goods_id=goods_id,
                goods_name=goods_info.goods_name if goods_info else None,
                start_date=start_date,
                end_date=end_date,
                trend_data=trend_data
            )
            
            return response
            
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"获取库存趋势失败: {str(e)}")
    
    @staticmethod
    def get_goods_ranking(
        db: Session,
        ranking_type: str = "in",
        top_n: int = 10
    ) -> GoodsRankingResponse:
        """
        获取物品排行榜统计
        
        根据入库或出库数量统计物品排行榜。
        
        Args:
            db (Session): 数据库会话
            ranking_type (str): 排行榜类型（in/入库，out/出库）
            top_n (int): Top N
        
        Returns:
            GoodsRankingResponse: 物品排行榜统计结果
        
        Raises:
            ValueError: 排行榜类型错误
            RuntimeError: 查询失败
        
        Examples:
            >>> from app.database.config import SessionLocal
            >>> db = SessionLocal()
            >>> ranking = StatisticsService.get_goods_ranking(db, "in", 10)
        """
        try:
            # 验证排行榜类型
            if ranking_type not in ["in", "out"]:
                raise ValueError("排行榜类型必须是 'in' 或 'out'")
            
            # 根据类型选择表
            if ranking_type == "in":
                model = StockIn
                quantity_field = StockIn.in_quantity
                time_field = StockIn.in_time
            else:
                model = StockOut
                quantity_field = StockOut.out_quantity
                time_field = StockOut.out_time
            
            # 查询入库/出库数量最多的物品
            ranking_query = db.query(
                Goods.goods_id,
                Goods.goods_name,
                Goods.goods_code,
                func.sum(quantity_field).label("total_quantity")
            ).join(
                model,
                Goods.goods_id == model.goods_id
            ).group_by(
                Goods.goods_id,
                Goods.goods_name,
                Goods.goods_code
            ).order_by(
                desc("total_quantity")
            ).limit(top_n)
            
            ranking_results = ranking_query.all()
            
            # 构建排行榜列表
            ranking_list = []
            for index, result in enumerate(ranking_results, start=1):
                ranking_item = GoodsRankingItem(
                    rank=index,
                    goods_id=result.goods_id,
                    goods_name=result.goods_name,
                    goods_code=result.goods_code,
                    total_quantity=int(result.total_quantity)
                )
                ranking_list.append(ranking_item)
            
            # 构建响应
            response = GoodsRankingResponse(
                ranking_type=ranking_type,
                top_n=top_n,
                ranking_list=ranking_list
            )
            
            return response
            
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"获取物品排行榜失败: {str(e)}")
    
    @staticmethod
    def get_category_stats(
        db: Session,
        stats_type: str = "stock"
    ) -> CategoryStatsResponse:
        """
        获取分类统计
        
        根据统计类型（库存数量或入库数量）统计各分类的数据。
        
        Args:
            db (Session): 数据库会话
            stats_type (str): 统计类型（stock/库存，in/入库）
        
        Returns:
            CategoryStatsResponse: 分类统计结果
        
        Raises:
            ValueError: 统计类型错误
            RuntimeError: 查询失败
        
        Examples:
            >>> from app.database.config import SessionLocal
            >>> db = SessionLocal()
            >>> stats = StatisticsService.get_category_stats(db, "stock")
        """
        try:
            # 验证统计类型
            if stats_type not in ["stock", "in"]:
                raise ValueError("统计类型必须是 'stock' 或 'in'")
            
            # 查询分类统计
            if stats_type == "stock":
                # 按库存数量统计
                stats_query = db.query(
                    GoodsCategory.category_id,
                    GoodsCategory.category_name,
                    GoodsCategory.category_code,
                    func.sum(Stock.current_stock).label("stock_quantity")
                ).join(
                    Goods,
                    GoodsCategory.category_id == Goods.category_id
                ).join(
                    Stock,
                    Stock.goods_id == Goods.goods_id
                ).group_by(
                    GoodsCategory.category_id,
                    GoodsCategory.category_name,
                    GoodsCategory.category_code
                )
                
                # 执行查询
                stats_results = stats_query.all()
                
                # 构建分类统计列表（in_quantity设置为0）
                category_stats = []
                for result in stats_results:
                    stats_item = CategoryStatsItem(
                        category_id=result.category_id,
                        category_name=result.category_name,
                        category_code=result.category_code,
                        stock_quantity=int(result.stock_quantity) if result.stock_quantity else 0,
                        in_quantity=0
                    )
                    category_stats.append(stats_item)
            else:
                # 按入库数量统计（本月）
                this_month_start = datetime.now().replace(
                    day=1, hour=0, minute=0, second=0
                )
                
                stats_query = db.query(
                    GoodsCategory.category_id,
                    GoodsCategory.category_name,
                    GoodsCategory.category_code,
                    func.sum(StockIn.in_quantity).label("in_quantity")
                ).join(
                    Goods,
                    GoodsCategory.category_id == Goods.category_id
                ).join(
                    StockIn,
                    Goods.goods_id == StockIn.goods_id
                ).filter(
                    StockIn.in_time >= this_month_start
                ).group_by(
                    GoodsCategory.category_id,
                    GoodsCategory.category_name,
                    GoodsCategory.category_code
                )
                
                # 执行查询
                stats_results = stats_query.all()
                
                # 构建分类统计列表（stock_quantity设置为0）
                category_stats = []
                for result in stats_results:
                    stats_item = CategoryStatsItem(
                        category_id=result.category_id,
                        category_name=result.category_name,
                        category_code=result.category_code,
                        stock_quantity=0,
                        in_quantity=int(result.in_quantity) if result.in_quantity else 0
                    )
                    category_stats.append(stats_item)
            
            # 构建响应
            response = CategoryStatsResponse(
                stats_type=stats_type,
                category_stats=category_stats
            )
            
            return response
            
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"获取分类统计失败: {str(e)}")
    
    @staticmethod
    def get_stock_alert(db: Session) -> StockAlertResponse:
        """
        获取库存预警列表
        
        查询当前库存低于最小阈值的物品列表
        
        Args:
            db (Session): 数据库会话
        
        Returns:
            StockAlertResponse: 库存预警列表响应
        
        Raises:
            RuntimeError: 查询失败
        
        Examples:
            >>> from app.database.config import SessionLocal
            >>> db = SessionLocal()
            >>> alert = StatisticsService.get_stock_alert(db)
            >>> print(f"预警物品数量: {alert.total_count}")
        """
        try:
            # 查询当前库存低于最小阈值的物品
            # 使用 joinedload 关联查询物品信息
            alert_stocks = db.query(Stock).options(
                joinedload(Stock.goods)
            ).filter(
                Stock.current_stock < Stock.min_stock
            ).all()
            
            # 构建预警列表
            alert_list = []
            for stock in alert_stocks:
                if stock.goods:
                    alert_item = StockAlertItem(
                        goods_id=stock.goods_id,
                        goods_name=stock.goods.goods_name,
                        current_stock=stock.current_stock,
                        min_stock=stock.min_stock
                    )
                    alert_list.append(alert_item)
            
            # 构建响应
            response = StockAlertResponse(
                alert_list=alert_list,
                total_count=len(alert_list)
            )
            
            return response
            
        except Exception as e:
            raise RuntimeError(f"获取库存预警列表失败: {str(e)}")