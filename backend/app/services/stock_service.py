"""
CampusAssetManager/backend/app/services/stock_service.py
库存管理服务类

功能说明：
- 入库操作（创建入库记录、更新库存）
- 出库操作（创建出库记录、扣减库存、库存验证）
- 查询入库记录列表（支持分页、搜索）
- 查询出库记录列表（支持分页、搜索）
- 获取入库出库详情
- 记录操作日志

设计原则：
- 面向对象：使用 StockService 类封装库存管理逻辑
- 声明式：使用 Pydantic 定义数据模型
- 事务管理：涉及多个数据库操作的必须使用事务
- 封装清晰：提供简洁的公共方法

作者：CampusAssetManager开发团队
日期：2026-01-08
"""

import logging
logger = logging.getLogger(__name__)

from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import or_, literal, and_, update
from datetime import datetime

from ..models.stock_in import StockIn
from ..models.stock_out import StockOut
from ..models.stock_check import StockCheck
from ..models.stock_info import Stock
from ..models.goods_info import Goods
from ..models.goods_category import GoodsCategory
from ..models.sys_user import User
from ..models.sys_operation_log import OperationLog
from ..schemas.stock import (
    StockInCreate,
    StockInResponse,
    StockInListResponse,
    StockInQuery,
    StockOutCreate,
    StockOutResponse,
    StockOutListResponse,
    StockOutQuery,
    StockResponse,
    StockListResponse,
    StockListResponseEnhanced,
    StockCheckCreate,
    StockCheckResponse,
    StockCheckListResponse,
    StockCheckQuery,
    StockAdjustCreate,
    StockAdjustResponse,
    StockLedgerResponse,
    StockLedgerListResponse,
    StockLedgerQuery,
    StockQueryEnriched,
    StockResponseEnhanced
)


class StockService:
    """
    库存管理服务类
    
    负责处理入库出库相关的所有业务逻辑
    """
    
    # ==================== 入库管理 ====================
    
    def create_stock_in(
        self,
        stock_in_data: StockInCreate,
        operator_id: int,
        db: Session
    ) -> StockInResponse:
        """
        创建入库记录
        
        创建入库记录并更新库存，使用事务保证数据一致性。
        
        Args:
            stock_in_data (StockInCreate): 入库数据
            operator_id (int): 操作人ID
            db (Session): 数据库会话
        
        Returns:
            StockInResponse: 创建的入库记录
        
        Raises:
            ValueError: 物品不存在
            Exception: 创建入库失败
        
        Examples:
            >>> service = StockService()
            >>> in_data = StockInCreate(goods_id=1, in_quantity=10, unit_price=100, total_amount=1000)
            >>> result = service.create_stock_in(in_data, 1, db)
        """
        try:
            # 查询分类名称
            category = db.query(GoodsCategory).join(
                Goods, GoodsCategory.category_id == Goods.category_id
            ).filter(
                Goods.goods_id == stock_in_data.goods_id
            ).first()
            
            # 验证物品是否存在
            goods = db.query(Goods).filter(
                Goods.goods_id == stock_in_data.goods_id
            ).first()
            
            if not goods:
                raise ValueError("物品不存在")
            
            # 查询操作人信息
            operator = db.query(User).filter(User.user_id == operator_id).first()
            
            # 生成入库单号
            in_no = self._generate_in_no(db)
            
            # 创建入库记录
            stock_in = StockIn(
                in_no=in_no,
                goods_id=stock_in_data.goods_id,
                operator_id=operator_id,
                in_quantity=stock_in_data.in_quantity,
                unit_price=stock_in_data.unit_price,
                total_amount=stock_in_data.total_amount,
                batch_no=stock_in_data.batch_no,
                supplier=stock_in_data.supplier,
                remark=stock_in_data.remark
            )
            db.add(stock_in)
            db.flush()
            
            # 查询或创建库存记录
            stock = db.query(Stock).filter(
                Stock.goods_id == stock_in_data.goods_id
            ).first()
            
            if stock:
                # 更新库存
                stock.current_stock += stock_in_data.in_quantity
                stock.total_value += stock_in_data.total_amount
                stock.update_time = datetime.utcnow()
            else:
                # 创建库存记录
                stock = Stock(
                    goods_id=stock_in_data.goods_id,
                    current_stock=stock_in_data.in_quantity,
                    total_value=stock_in_data.total_amount,
                    min_stock=0,
                    max_stock=None
                )
                db.add(stock)
            
            # 记录操作日志
            log = OperationLog(
                user_id=operator_id,
                username=operator.username if operator else "未知用户",
                operation="create",
                module="stock_in",
                method="POST",
                url="/v1/stock/in",
                params=f"goods_id={stock_in_data.goods_id}, in_quantity={stock_in_data.in_quantity}",
                result="success",
                ip_address=""
            )
            db.add(log)
            
            # 构建包含物品信息的响应数据
            response_data = {
                'in_id': stock_in.in_id,
                'in_no': stock_in.in_no,
                'goods_id': stock_in.goods_id,
                'operator_id': stock_in.operator_id,
                'in_quantity': stock_in.in_quantity,
                'unit_price': stock_in.unit_price,
                'total_amount': stock_in.total_amount,
                'batch_no': stock_in.batch_no,
                'supplier': stock_in.supplier,
                'remark': stock_in.remark,
                'in_time': stock_in.in_time,
                'goods_name': goods.goods_name if goods else '',
                'goods_code': goods.goods_code if goods else '',
                'category_name': category.category_name if category else ''
            }
            
            # 提交事务
            db.commit()
            
            return StockInResponse.model_validate(response_data)
        except ValueError:
            raise
        except Exception as e:
            db.rollback()
            raise Exception(f"创建入库记录失败: {str(e)}")
    
    def get_stock_in_list(
        self,
        query_params: StockInQuery,
        db: Session
    ) -> StockInListResponse:
        """
        查询入库记录列表（支持分页、搜索，包含物品信息）
        
        Args:
            query_params (StockInQuery): 查询参数
            db (Session): 数据库会话
        
        Returns:
            StockInListResponse: 入库记录列表（包含物品名称、编码和分类名称）
        
        Examples:
            >>> service = StockService()
            >>> query = StockInQuery(page=1, page_size=20)
            >>> result = service.get_stock_in_list(query, db)
        """
        # 构建基础查询
        query = db.query(StockIn, Goods, GoodsCategory).join(
            Goods, StockIn.goods_id == Goods.goods_id
        ).join(
            GoodsCategory, Goods.category_id == GoodsCategory.category_id
        )
        
        # 搜索条件
        if query_params.search:
            search = f"%{query_params.search}%"
            query = query.filter(
                or_(
                    StockIn.in_no.like(search),
                    Goods.goods_name.like(search)
                )
            )
        
        # 按物品筛选
        if query_params.goods_id:
            query = query.filter(StockIn.goods_id == query_params.goods_id)
        
        # 按日期范围筛选
        if query_params.start_date:
            query = query.filter(StockIn.in_time >= query_params.start_date)
        
        if query_params.end_date:
            query = query.filter(StockIn.in_time <= query_params.end_date)
        
        # 查询总数
        total = query.count()
        
        # 分页查询
        offset = (query_params.page - 1) * query_params.page_size
        items = query.order_by(StockIn.in_time.desc()).offset(offset).limit(
            query_params.page_size
        ).all()
        
        # 构建响应数据（包含物品信息）
        stock_in_items = []
        for stock_in, goods, category in items:
            item_data = {
                'in_id': stock_in.in_id,
                'in_no': stock_in.in_no,
                'goods_id': stock_in.goods_id,
                'operator_id': stock_in.operator_id,
                'in_quantity': stock_in.in_quantity,
                'unit_price': stock_in.unit_price,
                'total_amount': stock_in.total_amount,
                'batch_no': stock_in.batch_no,
                'supplier': stock_in.supplier,
                'remark': stock_in.remark,
                'in_time': stock_in.in_time,
                'goods_name': goods.goods_name,
                'goods_code': goods.goods_code,
                'category_name': category.category_name
            }
            stock_in_items.append(StockInResponse.model_validate(item_data))
        
        return StockInListResponse(
            items=stock_in_items,
            total=total,
            page=query_params.page,
            page_size=query_params.page_size
        )
    
    def get_stock_in_by_id(
        self,
        in_id: int,
        db: Session
    ) -> StockInResponse:
        """
        根据ID获取入库详情
        
        Args:
            in_id (int): 入库记录ID
            db (Session): 数据库会话
        
        Returns:
            StockInResponse: 入库记录详情
        
        Raises:
            ValueError: 入库记录不存在
        
        Examples:
            >>> service = StockService()
            >>> result = service.get_stock_in_by_id(1, db)
        """
        stock_in = db.query(StockIn).filter(
            StockIn.in_id == in_id
        ).first()
        
        if not stock_in:
            raise ValueError("入库记录不存在")
        
        return StockInResponse.model_validate(stock_in)
    
    # ==================== 出库管理 ====================
    
    def create_stock_out(
        self,
        stock_out_data: StockOutCreate,
        operator_id: int,
        db: Session
    ) -> StockOutResponse:
        """
        创建出库记录
        
        创建出库记录并扣减库存，检查库存是否充足。
        
        Args:
            stock_out_data (StockOutCreate): 出库数据
            operator_id (int): 操作人ID
            db (Session): 数据库会话
        
        Returns:
            StockOutResponse: 创建的出库记录
        
        Raises:
            ValueError: 物品不存在或库存不足
            Exception: 创建出库失败
        
        Examples:
            >>> service = StockService()
            >>> out_data = StockOutCreate(goods_id=1, out_quantity=5, unit_price=100, total_amount=500)
            >>> result = service.create_stock_out(out_data, 1, db)
        """
        try:
            # 查询分类名称
            category = db.query(GoodsCategory).join(
                Goods, GoodsCategory.category_id == Goods.category_id
            ).filter(
                Goods.goods_id == stock_out_data.goods_id
            ).first()
            
            # 验证物品是否存在
            goods = db.query(Goods).filter(
                Goods.goods_id == stock_out_data.goods_id
            ).first()
            
            if not goods:
                raise ValueError("物品不存在")
            
            # 查询操作人信息
            operator = db.query(User).filter(User.user_id == operator_id).first()
            
            # 检查库存是否充足
            stock = db.query(Stock).filter(
                Stock.goods_id == stock_out_data.goods_id
            ).first()
            
            if not stock or stock.current_stock < stock_out_data.out_quantity:
                raise ValueError(f"库存不足，当前库存：{stock.current_stock if stock else 0}，需出库：{stock_out_data.out_quantity}")
            
            # 生成出库单号
            out_no = self._generate_out_no(db)
            
            # 创建出库记录
            stock_out = StockOut(
                out_no=out_no,
                goods_id=stock_out_data.goods_id,
                operator_id=operator_id,
                out_quantity=stock_out_data.out_quantity,
                unit_price=stock_out_data.unit_price,
                total_amount=stock_out_data.total_amount,
                receiver=stock_out_data.receiver,
                department=stock_out_data.department,
                purpose=stock_out_data.purpose,
                remark=stock_out_data.remark
            )
            db.add(stock_out)
            db.flush()
            
            # 扣减库存
            stock.current_stock -= stock_out_data.out_quantity
            stock.total_value -= stock_out_data.total_amount
            stock.update_time = datetime.utcnow()
            
            # 记录操作日志
            log = OperationLog(
                user_id=operator_id,
                username=operator.username if operator else "未知用户",
                operation="create",
                module="stock_out",
                method="POST",
                url="/v1/stock/out",
                params=f"goods_id={stock_out_data.goods_id}, out_quantity={stock_out_data.out_quantity}",
                result="success",
                ip_address=""
            )
            db.add(log)
            
            # 构建包含物品信息的响应数据
            response_data = {
                'out_id': stock_out.out_id,
                'out_no': stock_out.out_no,
                'goods_id': stock_out.goods_id,
                'operator_id': stock_out.operator_id,
                'out_quantity': stock_out.out_quantity,
                'unit_price': stock_out.unit_price,
                'total_amount': stock_out.total_amount,
                'receiver': stock_out.receiver,
                'department': stock_out.department,
                'purpose': stock_out.purpose,
                'remark': stock_out.remark,
                'out_time': stock_out.out_time,
                'goods_name': goods.goods_name if goods else '',
                'goods_code': goods.goods_code if goods else '',
                'category_name': category.category_name if category else ''
            }
            
            # 提交事务
            db.commit()
            
            return StockOutResponse.model_validate(response_data)
        except ValueError:
            raise
        except Exception as e:
            db.rollback()
            raise Exception(f"创建出库记录失败: {str(e)}")
            
    
    def get_stock_out_list(
        self,
        query_params: StockOutQuery,
        db: Session
    ) -> StockOutListResponse:
        """
        查询出库记录列表（支持分页、搜索，包含物品信息）
        
        Args:
            query_params (StockOutQuery): 查询参数
            db (Session): 数据库会话
        
        Returns:
            StockOutListResponse: 出库记录列表（包含物品名称、编码和分类名称）
        
        Examples:
            >>> service = StockService()
            >>> query = StockOutQuery(page=1, page_size=20)
            >>> result = service.get_stock_out_list(query, db)
        """
        # 构建基础查询
        query = db.query(StockOut, Goods, GoodsCategory).join(
            Goods, StockOut.goods_id == Goods.goods_id
        ).join(
            GoodsCategory, Goods.category_id == GoodsCategory.category_id
        )
        
        # 搜索条件
        if query_params.search:
            search = f"%{query_params.search}%"
            query = query.filter(
                or_(
                    StockOut.out_no.like(search),
                    Goods.goods_name.like(search)
                )
            )
        
        # 按物品筛选
        if query_params.goods_id:
            query = query.filter(StockOut.goods_id == query_params.goods_id)
        
        # 按日期范围筛选
        if query_params.start_date:
            query = query.filter(StockOut.out_time >= query_params.start_date)
        
        if query_params.end_date:
            query = query.filter(StockOut.out_time <= query_params.end_date)
        
        # 查询总数
        total = query.count()
        
        # 分页查询
        offset = (query_params.page - 1) * query_params.page_size
        items = query.order_by(StockOut.out_time.desc()).offset(offset).limit(
            query_params.page_size
        ).all()
        
        # 构建响应数据（包含物品信息）
        stock_out_items = []
        for stock_out, goods, category in items:
            item_data = {
                'out_id': stock_out.out_id,
                'out_no': stock_out.out_no,
                'goods_id': stock_out.goods_id,
                'operator_id': stock_out.operator_id,
                'out_quantity': stock_out.out_quantity,
                'unit_price': stock_out.unit_price,
                'total_amount': stock_out.total_amount,
                'receiver': stock_out.receiver,
                'department': stock_out.department,
                'purpose': stock_out.purpose,
                'remark': stock_out.remark,
                'out_time': stock_out.out_time,
                'goods_name': goods.goods_name,
                'goods_code': goods.goods_code,
                'category_name': category.category_name
            }
            stock_out_items.append(StockOutResponse.model_validate(item_data))
        
        return StockOutListResponse(
            items=stock_out_items,
            total=total,
            page=query_params.page,
            page_size=query_params.page_size
        )
    
    def get_stock_out_by_id(
        self,
        out_id: int,
        db: Session
    ) -> StockOutResponse:
        """
        根据ID获取出库详情
        
        Args:
            out_id (int): 出库记录ID
            db (Session): 数据库会话
        
        Returns:
            StockOutResponse: 出库记录详情
        
        Raises:
            ValueError: 出库记录不存在
        
        Examples:
            >>> service = StockService()
            >>> result = service.get_stock_out_by_id(1, db)
        """
        stock_out = db.query(StockOut).filter(
            StockOut.out_id == out_id
        ).first()
        
        if not stock_out:
            raise ValueError("出库记录不存在")
        
        return StockOutResponse.model_validate(stock_out)
    
    # ==================== 库存管理 ====================
    
    def get_stock_list(
        self,
        page: int = 1,
        page_size: int = 20,
        db: Session = None
    ) -> StockListResponse:
        """
        查询库存列表（支持分页）
        
        查询库存信息并关联物品和分类信息。
        
        Args:
            page (int): 页码
            page_size (int): 每页数量
            db (Session): 数据库会话
        
        Returns:
            StockListResponse: 库存列表（包含物品名称和分类名称）
        
        Examples:
            >>> service = StockService()
            >>> result = service.get_stock_list(page=1, page_size=20, db=db)
        """
        from ..models.goods_category import GoodsCategory
        
        # 查询总数（JOIN goods表）
        total = db.query(Stock).join(Goods).count()
        
        # 分页查询（JOIN goods和goods_category表）
        offset = (page - 1) * page_size
        items = db.query(
            Stock,
            Goods,
            GoodsCategory
        ).join(
            Goods, Stock.goods_id == Goods.goods_id
        ).join(
            GoodsCategory, Goods.category_id == GoodsCategory.category_id
        ).order_by(
            Stock.goods_id
        ).offset(offset).limit(page_size).all()
        
        # 构建响应数据
        stock_items = []
        for stock, goods, category in items:
            stock_data = {
                'stock_id': stock.stock_id,
                'goods_id': stock.goods_id,
                'goods_name': goods.goods_name,
                'goods_code': goods.goods_code if goods else '',
                'category_name': category.category_name if category else '',
                'current_stock': stock.current_stock,
                'total_value': stock.total_value,
                'min_stock': stock.min_stock,
                'max_stock': stock.max_stock,
                'create_time': stock.create_time,
                'update_time': stock.update_time,
                'purchase_price': goods.purchase_price if goods else 0,
                'retail_price': goods.retail_price if goods else None,
                'status': goods.status if goods else 1
            }
            stock_items.append(stock_data)
        
        return StockListResponse(
            items=stock_items,
            total=total,
            page=page,
            page_size=page_size
        )
    
    # ==================== 辅助方法 ====================
    
    def _generate_in_no(self, db: Session) -> str:
        """
        生成入库单号
        
        格式：IN + YYYYMMDD + 序号
        
        Args:
            db (Session): 数据库会话
        
        Returns:
            str: 入库单号
        """
        date_str = datetime.now().strftime("%Y%m%d")
        
        # 查询当天的入库记录数量
        count = db.query(StockIn).filter(
            StockIn.in_no.like(f"IN-{date_str}%")
        ).count()
        
        # 生成单号
        serial = str(count + 1).zfill(3)
        return f"IN-{date_str}-{serial}"
    
    def _generate_out_no(self, db: Session) -> str:
        """
        生成出库单号
        
        格式：OUT + YYYYMMDD + 序号
        
        Args:
            db (Session): 数据库会话
        
        Returns:
            str: 出库单号
        """
        date_str = datetime.now().strftime("%Y%m%d")
        
        # 查询当天的出库记录数量
        count = db.query(StockOut).filter(
            StockOut.out_no.like(f"OUT-{date_str}%")
        ).count()
        
        # 生成单号
        serial = str(count + 1).zfill(3)
        return f"OUT-{date_str}-{serial}"
    
    # ==================== 盘点管理 ====================
    
    def create_stock_check(
        self,
        check_data: StockCheckCreate,
        checker_id: int,
        db: Session
    ) -> StockCheckResponse:
        """
        创建盘点记录
        
        创建盘点记录并计算差异，生成盘点单号。
        
        Args:
            check_data (StockCheckCreate): 盘点数据
            checker_id (int): 盘点人ID
            db (Session): 数据库会话
        
        Returns:
            StockCheckResponse: 创建的盘点记录
        
        Raises:
            ValueError: 物品不存在或库存记录不存在
            Exception: 创建盘点失败
        
        Examples:
            >>> service = StockService()
            >>> check_data = StockCheckCreate(goods_id=1, actual_stock=100)
            >>> result = service.create_stock_check(check_data, 1, db)
        """
        try:
            # 查询分类名称
            category = db.query(GoodsCategory).join(
                Goods, GoodsCategory.category_id == Goods.category_id
            ).filter(
                Goods.goods_id == check_data.goods_id
            ).first()
            
            # 验证物品是否存在
            goods = db.query(Goods).filter(
                Goods.goods_id == check_data.goods_id
            ).first()
            
            if not goods:
                raise ValueError("物品不存在")
            
            # 查询盘点人信息
            checker = db.query(User).filter(User.user_id == checker_id).first()
            
            # 查询库存记录
            stock = db.query(Stock).filter(
                Stock.goods_id == check_data.goods_id
            ).first()
            
            if not stock:
                raise ValueError("库存记录不存在，请先进行入库操作")
            
            # 计算账面与实际差异
            book_stock = stock.current_stock
            actual_stock = check_data.actual_stock
            diff_quantity = actual_stock - book_stock
            
            # 判断盘点结果
            if diff_quantity == 0:
                check_result = "normal"
            elif diff_quantity > 0:
                check_result = "over"
            else:
                check_result = "short"
            
            # 生成盘点单号
            check_no = self._generate_check_no(db)
            
            # 创建盘点记录
            stock_check = StockCheck(
                check_no=check_no,
                goods_id=check_data.goods_id,
                checker_id=checker_id,
                book_stock=book_stock,
                actual_stock=actual_stock,
                diff_quantity=diff_quantity,
                check_result=check_result,
                remark=check_data.remark
            )
            db.add(stock_check)
            db.flush()
            
            # 如果有差异，更新库存
            if diff_quantity != 0:
                stock.current_stock = actual_stock
                stock.update_time = datetime.utcnow()
            
            # 记录操作日志
            log = OperationLog(
                user_id=checker_id,
                username=checker.username if checker else "未知用户",
                operation="create",
                module="stock_check",
                method="POST",
                url="/v1/stock/check",
                params=f"goods_id={check_data.goods_id}, actual_stock={check_data.actual_stock}",
                result="success",
                ip_address=""
            )
            db.add(log)
            
            # 构建包含物品信息的响应数据
            response_data = {
                'check_id': stock_check.check_id,
                'check_no': stock_check.check_no,
                'goods_id': stock_check.goods_id,
                'checker_id': stock_check.checker_id,
                'book_stock': stock_check.book_stock,
                'actual_stock': stock_check.actual_stock,
                'diff_quantity': stock_check.diff_quantity,
                'check_result': stock_check.check_result,
                'remark': stock_check.remark,
                'check_time': stock_check.check_time,
                'goods_name': goods.goods_name if goods else '',
                'goods_code': goods.goods_code if goods else '',
                'checker_name': checker.username if checker else ''
            }
            
            # 提交事务
            db.commit()
            
            return StockCheckResponse.model_validate(response_data)
        except ValueError:
            raise
        except Exception as e:
            db.rollback()
            raise Exception(f"创建盘点记录失败: {str(e)}")
    
    def get_stock_check_list(
        self,
        query_params: StockCheckQuery,
        db: Session
    ) -> StockCheckListResponse:
        """
        查询盘点记录列表（支持分页、搜索，包含物品信息）
        
        Args:
            query_params (StockCheckQuery): 查询参数
            db (Session): 数据库会话
        
        Returns:
            StockCheckListResponse: 盘点记录列表（包含物品名称、编码和盘点人名称）
        
        Examples:
            >>> service = StockService()
            >>> query = StockCheckQuery(page=1, page_size=20)
            >>> result = service.get_stock_check_list(query, db)
        """
        # 构建基础查询
        query = db.query(StockCheck, Goods, User).join(
            Goods, StockCheck.goods_id == Goods.goods_id
        ).join(
            User, StockCheck.checker_id == User.user_id
        )
        
        # 搜索条件
        if query_params.search:
            search = f"%{query_params.search}%"
            query = query.filter(
                or_(
                    StockCheck.check_no.like(search),
                    Goods.goods_name.like(search)
                )
            )
        
        # 按物品筛选
        if query_params.goods_id:
            query = query.filter(StockCheck.goods_id == query_params.goods_id)
        
        # 按盘点结果筛选
        if query_params.check_result:
            query = query.filter(StockCheck.check_result == query_params.check_result)
        
        # 按日期范围筛选
        if query_params.start_date:
            query = query.filter(StockCheck.check_time >= query_params.start_date)
        
        if query_params.end_date:
            query = query.filter(StockCheck.check_time <= query_params.end_date)
        
        # 查询总数
        total = query.count()
        
        # 分页查询
        offset = (query_params.page - 1) * query_params.page_size
        items = query.order_by(StockCheck.check_time.desc()).offset(offset).limit(
            query_params.page_size
        ).all()
        
        # 构建响应数据（包含物品信息）
        stock_check_items = []
        for stock_check, goods, checker in items:
            item_data = {
                'check_id': stock_check.check_id,
                'check_no': stock_check.check_no,
                'goods_id': stock_check.goods_id,
                'checker_id': stock_check.checker_id,
                'book_stock': stock_check.book_stock,
                'actual_stock': stock_check.actual_stock,
                'diff_quantity': stock_check.diff_quantity,
                'check_result': stock_check.check_result,
                'remark': stock_check.remark,
                'check_time': stock_check.check_time,
                'goods_name': goods.goods_name,
                'goods_code': goods.goods_code,
                'checker_name': checker.username
            }
            stock_check_items.append(StockCheckResponse.model_validate(item_data))
        
        return StockCheckListResponse(
            items=stock_check_items,
            total=total,
            page=query_params.page,
            page_size=query_params.page_size
        )
    
    def get_stock_check_by_id(
        self,
        check_id: int,
        db: Session
    ) -> StockCheckResponse:
        """
        根据ID获取盘点详情
        
        Args:
            check_id (int): 盘点记录ID
            db (Session): 数据库会话
        
        Returns:
            StockCheckResponse: 盘点记录详情
        
        Raises:
            ValueError: 盘点记录不存在
        
        Examples:
            >>> service = StockService()
            >>> result = service.get_stock_check_by_id(1, db)
        """
        # 关联查询物品和用户信息
        stock_check = db.query(StockCheck, Goods, User).join(
            Goods, StockCheck.goods_id == Goods.goods_id
        ).join(
            User, StockCheck.checker_id == User.user_id
        ).filter(
            StockCheck.check_id == check_id
        ).first()
        
        if not stock_check:
            raise ValueError("盘点记录不存在")
        
        stock_check_obj, goods, checker = stock_check
        
        # 构建包含关联信息的响应数据
        response_data = {
            'check_id': stock_check_obj.check_id,
            'check_no': stock_check_obj.check_no,
            'goods_id': stock_check_obj.goods_id,
            'checker_id': stock_check_obj.checker_id,
            'book_stock': stock_check_obj.book_stock,
            'actual_stock': stock_check_obj.actual_stock,
            'diff_quantity': stock_check_obj.diff_quantity,
            'check_result': stock_check_obj.check_result,
            'remark': stock_check_obj.remark,
            'check_time': stock_check_obj.check_time,
            'goods_name': goods.goods_name if goods else '',
            'goods_code': goods.goods_code if goods else '',
            'checker_name': checker.username if checker else ''
        }
        
        return StockCheckResponse.model_validate(response_data)
    
    # ==================== 库存调整 ====================
    
    def adjust_stock(
        self,
        adjust_data: StockAdjustCreate,
        operator_id: int,
        db: Session
    ) -> StockAdjustResponse:
        """
        手动调整库存（超级管理员权限）
        
        根据调整数量增加或减少库存，记录调整原因。
        
        Args:
            adjust_data (StockAdjustCreate): 调整数据
            operator_id (int): 操作人ID
            db (Session): 数据库会话
        
        Returns:
            StockAdjustResponse: 调整结果
        
        Raises:
            ValueError: 物品不存在或库存不足
            Exception: 调整失败
        
        Examples:
            >>> service = StockService()
            >>> adjust_data = StockAdjustCreate(goods_id=1, adjust_quantity=10, adjust_reason="盘亏调整")
            >>> result = service.adjust_stock(adjust_data, 1, db)
        """
        try:
            # 验证物品是否存在
            goods = db.query(Goods).filter(
                Goods.goods_id == adjust_data.goods_id
            ).first()
            
            if not goods:
                raise ValueError("物品不存在")
            
            # 查询操作人信息
            operator = db.query(User).filter(User.user_id == operator_id).first()
            
            # 查询库存记录
            stock = db.query(Stock).filter(
                Stock.goods_id == adjust_data.goods_id
            ).first()
            
            if not stock:
                raise ValueError("库存记录不存在，请先进行入库操作")
            
            # 验证库存是否充足（减少库存时）
            if adjust_data.adjust_quantity < 0 and stock.current_stock + adjust_data.adjust_quantity < 0:
                raise ValueError(f"库存不足，当前库存：{stock.current_stock}，需减少：{abs(adjust_data.adjust_quantity)}")
            
            # 记录调整前库存
            before_stock = stock.current_stock
            
            # 调整库存
            stock.current_stock += adjust_data.adjust_quantity
            stock.update_time = datetime.utcnow()
            
            # 计算调整后价值（假设单价不变，重新计算总价值）
            unit_price = goods.purchase_price if goods.purchase_price else 0
            stock.total_value = stock.current_stock * unit_price
            
            # 记录操作日志
            log = OperationLog(
                user_id=operator_id,
                username=operator.username if operator else "未知用户",
                operation="adjust",
                module="stock",
                method="PUT",
                url="/v1/stock/adjust",
                params=f"goods_id={adjust_data.goods_id}, adjust_quantity={adjust_data.adjust_quantity}",
                result="success",
                ip_address=""
            )
            db.add(log)
            
            # 构建响应数据
            response_data = {
                'stock_id': stock.stock_id,
                'goods_id': stock.goods_id,
                'goods_name': goods.goods_name if goods else '',
                'goods_code': goods.goods_code if goods else '',
                'before_stock': before_stock,
                'adjust_quantity': adjust_data.adjust_quantity,
                'after_stock': stock.current_stock,
                'adjust_reason': adjust_data.adjust_reason,
                'adjust_time': datetime.utcnow()
            }
            
            # 提交事务
            db.commit()
            
            return StockAdjustResponse.model_validate(response_data)
        except ValueError:
            raise
        except Exception as e:
            db.rollback()
            raise Exception(f"库存调整失败: {str(e)}")
    
    # ==================== 台账查询 ====================
    
    def get_stock_ledger(
        self,
        query_params: StockLedgerQuery,
        db: Session
    ) -> StockLedgerListResponse:
        """
        查询库存台账（合并入库、出库、盘点记录）
        
        Args:
            query_params (StockLedgerQuery): 查询参数
            db (Session): 数据库会话
        
        Returns:
            StockLedgerListResponse: 库存台账列表
        
        Examples:
            >>> service = StockService()
            >>> query = StockLedgerQuery(page=1, page_size=20)
            >>> result = service.get_stock_ledger(query, db)
        """
        ledger_items = []
        
        # 查询入库记录
        if query_params.operation_type in [None, 'in']:
            in_query = db.query(
                StockIn.in_id.label('record_id'),
                StockIn.in_no.label('operation_no'),
                StockIn.goods_id,
                StockIn.in_quantity.label('quantity'),
                StockIn.in_time.label('operation_time'),
                StockIn.remark,
                StockIn.operator_id,
                literal('in').label('operation_type')
            ).join(Goods, StockIn.goods_id == Goods.goods_id)
            
            # 应用筛选条件
            if query_params.search:
                search = f"%{query_params.search}%"
                in_query = in_query.filter(
                    or_(
                        StockIn.in_no.like(search),
                        Goods.goods_name.like(search)
                    )
                )
            
            if query_params.goods_id:
                in_query = in_query.filter(StockIn.goods_id == query_params.goods_id)
            
            if query_params.start_date:
                in_query = in_query.filter(StockIn.in_time >= query_params.start_date)
            
            if query_params.end_date:
                in_query = in_query.filter(StockIn.in_time <= query_params.end_date)
            
            in_records = in_query.all()
            
            # 构建入库台账记录
            for record in in_records:
                goods = db.query(Goods).filter(Goods.goods_id == record.goods_id).first()
                category = db.query(GoodsCategory).join(Goods, GoodsCategory.category_id == Goods.category_id).filter(Goods.goods_id == record.goods_id).first()
                user = db.query(User).filter(User.user_id == record.operator_id).first()
                stock = db.query(Stock).filter(Stock.goods_id == record.goods_id).first()
                
                # 计算操作前后库存（简化处理，使用当前库存减去入库数量作为操作前）
                stock_before = (stock.current_stock - record.quantity) if stock else 0
                stock_after = stock.current_stock if stock else record.quantity
                
                ledger_items.append({
                    'record_id': record.record_id,
                    'operation_type': 'in',
                    'operation_no': record.operation_no,
                    'goods_id': record.goods_id,
                    'goods_name': goods.goods_name if goods else '',
                    'goods_code': goods.goods_code if goods else '',
                    'category_name': category.category_name if category else '',
                    'quantity': record.quantity,
                    'stock_before': stock_before,
                    'stock_after': stock_after,
                    'operator_id': record.operator_id,
                    'operator_name': user.username if user else '',
                    'operation_time': record.operation_time,
                    'remark': record.remark
                })
        
        # 查询出库记录
        if query_params.operation_type in [None, 'out']:
            out_query = db.query(
                StockOut.out_id.label('record_id'),
                StockOut.out_no.label('operation_no'),
                StockOut.goods_id,
                StockOut.out_quantity.label('quantity'),
                StockOut.out_time.label('operation_time'),
                StockOut.remark,
                StockOut.operator_id,
                literal('out').label('operation_type')
            ).join(Goods, StockOut.goods_id == Goods.goods_id)
            
            # 应用筛选条件
            if query_params.search:
                search = f"%{query_params.search}%"
                out_query = out_query.filter(
                    or_(
                        StockOut.out_no.like(search),
                        Goods.goods_name.like(search)
                    )
                )
            
            if query_params.goods_id:
                out_query = out_query.filter(StockOut.goods_id == query_params.goods_id)
            
            if query_params.start_date:
                out_query = out_query.filter(StockOut.out_time >= query_params.start_date)
            
            if query_params.end_date:
                out_query = out_query.filter(StockOut.out_time <= query_params.end_date)
            
            out_records = out_query.all()
            
            # 构建出库台账记录
            for record in out_records:
                goods = db.query(Goods).filter(Goods.goods_id == record.goods_id).first()
                category = db.query(GoodsCategory).join(Goods, GoodsCategory.category_id == Goods.category_id).filter(Goods.goods_id == record.goods_id).first()
                user = db.query(User).filter(User.user_id == record.operator_id).first()
                stock = db.query(Stock).filter(Stock.goods_id == record.goods_id).first()
                
                # 计算操作前后库存
                stock_before = (stock.current_stock + record.quantity) if stock else record.quantity
                stock_after = stock.current_stock if stock else 0
                
                ledger_items.append({
                    'record_id': record.record_id,
                    'operation_type': 'out',
                    'operation_no': record.operation_no,
                    'goods_id': record.goods_id,
                    'goods_name': goods.goods_name if goods else '',
                    'goods_code': goods.goods_code if goods else '',
                    'category_name': category.category_name if category else '',
                    'quantity': record.quantity,
                    'stock_before': stock_before,
                    'stock_after': stock_after,
                    'operator_id': record.operator_id,
                    'operator_name': user.username if user else '',
                    'operation_time': record.operation_time,
                    'remark': record.remark
                })
        
        # 查询盘点记录
        if query_params.operation_type in [None, 'check']:
            check_query = db.query(
                StockCheck.check_id.label('record_id'),
                StockCheck.check_no.label('operation_no'),
                StockCheck.goods_id,
                StockCheck.diff_quantity.label('quantity'),
                StockCheck.check_time.label('operation_time'),
                StockCheck.remark,
                StockCheck.checker_id.label('operator_id'),
                literal('check').label('operation_type')
            ).join(Goods, StockCheck.goods_id == Goods.goods_id)
            
            # 应用筛选条件
            if query_params.search:
                search = f"%{query_params.search}%"
                check_query = check_query.filter(
                    or_(
                        StockCheck.check_no.like(search),
                        Goods.goods_name.like(search)
                    )
                )
            
            if query_params.goods_id:
                check_query = check_query.filter(StockCheck.goods_id == query_params.goods_id)
            
            if query_params.start_date:
                check_query = check_query.filter(StockCheck.check_time >= query_params.start_date)
            
            if query_params.end_date:
                check_query = check_query.filter(StockCheck.check_time <= query_params.end_date)
            
            check_records = check_query.all()
            
            # 构建盘点台账记录
            for record in check_records:
                goods = db.query(Goods).filter(Goods.goods_id == record.goods_id).first()
                category = db.query(GoodsCategory).join(Goods, GoodsCategory.category_id == Goods.category_id).filter(Goods.goods_id == record.goods_id).first()
                user = db.query(User).filter(User.user_id == record.operator_id).first()
                
                # 盘点记录中已包含 book_stock 和 actual_stock
                # 计算操作前后库存：book_stock 是操作前，actual_stock 是操作后
                stock_before = record.quantity  # quantity 这里对应 diff_quantity，但我们需要 book_stock
                # 重新查询盘点记录获取完整信息
                check_record = db.query(StockCheck).filter(StockCheck.check_id == record.record_id).first()
                if check_record:
                    stock_before = check_record.book_stock
                    stock_after = check_record.actual_stock
                
                ledger_items.append({
                    'record_id': record.record_id,
                    'operation_type': 'check',
                    'operation_no': record.operation_no,
                    'goods_id': record.goods_id,
                    'goods_name': goods.goods_name if goods else '',
                    'goods_code': goods.goods_code if goods else '',
                    'category_name': category.category_name if category else '',
                    'quantity': record.quantity,
                    'stock_before': stock_before,
                    'stock_after': stock_after,
                    'operator_id': record.operator_id,
                    'operator_name': user.username if user else '',
                    'operation_time': record.operation_time,
                    'remark': record.remark
                })
        
        # 按时间倒序排序
        ledger_items.sort(key=lambda x: x['operation_time'], reverse=True)
        
        # 分页
        total = len(ledger_items)
        offset = (query_params.page - 1) * query_params.page_size
        paged_items = ledger_items[offset:offset + query_params.page_size]
        
        # 构建响应
        stock_ledger_items = [StockLedgerResponse.model_validate(item) for item in paged_items]
        
        return StockLedgerListResponse(
            items=stock_ledger_items,
            total=total,
            page=query_params.page,
            page_size=query_params.page_size
        )
    
    # ==================== 库存查询增强 ====================
    
    def get_stock_list_enhanced(
        self,
        query_params: StockQueryEnriched,
        db: Session
    ) -> StockListResponseEnhanced:
        """
        增强库存查询（支持预警状态筛选）
        
        Args:
            query_params (StockQueryEnriched): 查询参数
            db (Session): 数据库会话
        
        Returns:
            StockListResponseEnhanced: 库存列表（包含库存状态）
        
        Examples:
            >>> service = StockService()
            >>> query = StockQueryEnriched(page=1, page_size=20, stock_status='low')
            >>> result = service.get_stock_list_enhanced(query, db)
        """
        # 查询总数（JOIN goods表）
        query = db.query(Stock, Goods, GoodsCategory).join(
            Goods, Stock.goods_id == Goods.goods_id
        ).join(
            GoodsCategory, Goods.category_id == GoodsCategory.category_id
        )
        
        # 搜索条件
        if query_params.search:
            search = f"%{query_params.search}%"
            query = query.filter(
                or_(
                    Goods.goods_name.like(search),
                    Goods.goods_code.like(search)
                )
            )
        
        # 按分类筛选
        if query_params.category_id:
            query = query.filter(Goods.category_id == query_params.category_id)
        
        # 按库存状态筛选
        if query_params.stock_status:
            logger.debug(f"【增强库存查询】应用库存状态筛选: stock_status={query_params.stock_status}")
            if query_params.stock_status == 'low':
                query = query.filter(Stock.current_stock < Stock.min_stock)
                logger.debug("  - 应用低库存条件: current_stock < min_stock")
            elif query_params.stock_status == 'over':
                query = query.filter(Stock.max_stock is not None, Stock.current_stock > Stock.max_stock)
                logger.debug("  - 应用库存过高条件: current_stock > max_stock")
            elif query_params.stock_status == 'normal':
                # 合并两个条件到一个 filter 调用
                # 正常库存：当前库存 >= 最小库存 AND (最大库存为空 OR 当前库存 <= 最大库存)
                query = query.filter(
                    Stock.current_stock >= Stock.min_stock,
                    or_(Stock.max_stock.is_(None), Stock.current_stock <= Stock.max_stock)
                )
                logger.debug("  - 应用正常库存条件: current_stock >= min_stock AND (max_stock IS NULL OR current_stock <= max_stock)")
        
        # 只显示低于最小库存的物品
        if query_params.min_stock_only:
            query = query.filter(Stock.current_stock < Stock.min_stock)
            logger.debug(f"【增强库存查询】应用只显示低库存筛选: min_stock_only={query_params.min_stock_only}")
        
        # 查询总数
        logger.debug(f"【增强库存查询】开始查询总数...")
        total = query.count()
        logger.debug(f"【增强库存查询】查询总数完成: total={total}")
        
        # 分页查询
        offset = (query_params.page - 1) * query_params.page_size
        logger.debug(f"【增强库存查询】执行分页查询: page={query_params.page}, size={query_params.page_size}, offset={offset}")
        try:
            items = query.order_by(Stock.goods_id).offset(offset).limit(
                query_params.page_size
            ).all()
            logger.debug(f"【增强库存查询】分页查询成功，返回 {len(items)} 条记录")
        except Exception as e:
            logger.error(f"【增强库存查询】分页查询失败: {str(e)}", exc_info=True)
            raise
        
        # 构建响应数据（包含库存状态）
        stock_items = []
        logger.debug(f"【增强库存查询】开始构建响应数据，共有 {len(items)} 条记录")
        
        for index, (stock, goods, category) in enumerate(items, 1):
            # 计算库存状态
            if stock.current_stock < stock.min_stock:
                stock_status = 'low'
                status_text = '低库存'
            elif stock.max_stock and stock.current_stock > stock.max_stock:
                stock_status = 'over'
                status_text = '库存过高'
            else:
                stock_status = 'normal'
                status_text = '正常'
            
            stock_data = {
                'stock_id': stock.stock_id,
                'goods_id': stock.goods_id,
                'goods_name': goods.goods_name,
                'goods_code': goods.goods_code,
                'category_name': category.category_name,
                'current_stock': stock.current_stock,
                'total_value': stock.total_value,
                'min_stock': stock.min_stock,
                'max_stock': stock.max_stock,
                'create_time': stock.create_time,
                'update_time': stock.update_time,
                'purchase_price': goods.purchase_price,
                'retail_price': goods.retail_price,
                'status': goods.status,
                'stock_status': stock_status,
                'status_text': status_text
            }
            stock_items.append(stock_data)
            if index <= 3:
                logger.debug(f"  - 记录 {index}: goods_id={stock.goods_id}, goods_name={goods.goods_name}, current_stock={stock.current_stock}, status={stock_status}")
        
        logger.info(f"【增强库存查询】响应数据构建完成，共 {len(stock_items)} 条")
        
        logger.info(f"【增强库存查询】查询成功，返回 {len(stock_items)} 条记录，total={total}, page={query_params.page}, page_size={query_params.page_size}")
        
        try:
            return StockListResponseEnhanced(
                items=stock_items,
                total=total,
                page=query_params.page,
                page_size=query_params.page_size
            )
        except Exception as e:
            logger.error(f"【增强库存查询】构建响应失败: {str(e)}", exc_info=True)
            raise Exception(f"构建响应失败: {str(e)}")
    
    # ==================== 辅助方法（新增） ====================
    
    def sync_stock_thresholds(
        self,
        min_stock: int,
        max_stock: int,
        db: Session
    ) -> Dict[str, Any]:
        """
        将全局库存阈值批量同步到所有物品的库存记录
        
        Args:
            min_stock (int): 最小库存阈值
            max_stock (int): 最大库存阈值
            db (Session): 数据库会话
        
        Returns:
            dict: 同步结果 {total, updated}
        
        Examples:
            >>> service = StockService()
            >>> result = service.sync_stock_thresholds(10, 1000, db)
            >>> print(f"共 {result['total']} 条记录，更新 {result['updated']} 条")
        """
        logger.info(f"【同步库存阈值】开始同步: min_stock={min_stock}, max_stock={max_stock}")
        
        try:
            # 查询所有需要更新的库存记录
            stock_query = db.query(Stock).all()
            total = len(stock_query)
            
            logger.debug(f"【同步库存阈值】找到 {total} 条库存记录")
            
            if total == 0:
                return {
                    "total": 0,
                    "updated": 0
                }
            
            # 批量更新库存阈值
            updated_count = 0
            for stock in stock_query:
                # 只有当物品的阈值与全局配置不同时才更新
                if stock.min_stock != min_stock or stock.max_stock != max_stock:
                    stock.min_stock = min_stock
                    stock.max_stock = max_stock
                    updated_count += 1
                    
                    if updated_count <= 3:
                        logger.debug(f"  - 更新 goods_id={stock.goods_id}: min_stock={min_stock}, max_stock={max_stock}")
            
            # 提交更改
            db.commit()
            
            logger.info(f"【同步库存阈值】同步完成: 总数={total}, 更新={updated_count}")
            
            return {
                "total": total,
                "updated": updated_count
            }
        except Exception as e:
            db.rollback()
            logger.error(f"【同步库存阈值】同步失败: {str(e)}", exc_info=True)
            raise Exception(f"同步库存阈值失败: {str(e)}")
    
    def _generate_check_no(self, db: Session) -> str:
        """
        生成盘点单号
        
        格式：CHK + YYYYMMDD + 序号
        
        Args:
            db (Session): 数据库会话
        
        Returns:
            str: 盘点单号
        """
        date_str = datetime.now().strftime("%Y%m%d")
        
        # 查询当天的盘点记录数量
        count = db.query(StockCheck).filter(
            StockCheck.check_no.like(f"CHK-{date_str}%")
        ).count()
        
        # 生成单号
        serial = str(count + 1).zfill(3)
        return f"CHK-{date_str}-{serial}"
    
    # ==================== 库存阈值更新 ====================
    
    def update_stock_threshold(
        self,
        threshold_data,
        db: Session
    ) -> Dict[str, Any]:
        """
        更新单个物品的库存阈值
        
        Args:
            threshold_data: 库存阈值更新数据（StockThresholdUpdate）
            db (Session): 数据库会话
        
        Returns:
            dict: 更新后的库存信息
        
        Examples:
            >>> service = StockService()
            >>> result = service.update_stock_threshold(
            ...     StockThresholdUpdate(goods_id=1, min_stock=10, max_stock=100),
            ...     db
            ... )
        """
        logger.info(f"【更新库存阈值】开始更新goods_id={threshold_data.goods_id}")
        
        try:
            # 查询库存记录
            stock = db.query(Stock).filter(
                Stock.goods_id == threshold_data.goods_id
            ).first()
            
            if not stock:
                raise ValueError(f"物品ID {threshold_data.goods_id} 对应的库存记录不存在")
            
            # 更新库存阈值
            stock.min_stock = threshold_data.min_stock
            stock.max_stock = threshold_data.max_stock
            
            # 提交更改
            db.commit()
            db.refresh(stock)
            
            logger.info(f"【更新库存阈值】更新成功: goods_id={threshold_data.goods_id}, min_stock={threshold_data.min_stock}, max_stock={threshold_data.max_stock}")
            
            return {
                "stock_id": stock.stock_id,
                "goods_id": stock.goods_id,
                "min_stock": stock.min_stock,
                "max_stock": stock.max_stock
            }
        except ValueError:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"【更新库存阈值】更新失败: {str(e)}", exc_info=True)
            raise Exception(f"更新库存阈值失败: {str(e)}")
    
    def batch_update_stock_thresholds(
        self,
        batch_data,
        db: Session
    ) -> Dict[str, Any]:
        """
        批量更新所有物品的库存阈值
        
        Args:
            batch_data: 批量更新数据（StockThresholdBatchUpdate）
            db (Session): 数据库会话
        
        Returns:
            dict: 更新结果 {total, updated}
        
        Examples:
            >>> service = StockService()
            >>> result = service.batch_update_stock_thresholds(
            ...     StockThresholdBatchUpdate(min_stock=10, max_stock=100),
            ...     db
            ... )
        """
        logger.info(f"【批量更新库存阈值】开始更新: min_stock={batch_data.min_stock}, max_stock={batch_data.max_stock}")
        
        try:
            # 查询所有库存记录
            stock_query = db.query(Stock).all()
            total = len(stock_query)
            
            if total == 0:
                return {
                    "total": 0,
                    "updated": 0
                }
            
            # 批量更新库存阈值
            updated_count = 0
            for stock in stock_query:
                # 只有当物品的阈值与全局配置不同时才更新
                if stock.min_stock != batch_data.min_stock or stock.max_stock != batch_data.max_stock:
                    stock.min_stock = batch_data.min_stock
                    stock.max_stock = batch_data.max_stock
                    updated_count += 1
            
            # 提交更改
            db.commit()
            
            logger.info(f"【批量更新库存阈值】更新完成: 总数={total}, 更新={updated_count}")
            
            return {
                "total": total,
                "updated": updated_count
            }
        except Exception as e:
            db.rollback()
            logger.error(f"【批量更新库存阈值】更新失败: {str(e)}", exc_info=True)
            raise Exception(f"批量更新库存阈值失败: {str(e)}")