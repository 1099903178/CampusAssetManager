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

from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from ..models.stock_in import StockIn
from ..models.stock_out import StockOut
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
    StockListResponse
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
            
        finally:
            try:
                db.commit()
            except:
                pass
    
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