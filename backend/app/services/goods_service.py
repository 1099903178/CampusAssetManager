"""
CampusAssetManager/backend/app/services/goods_service.py
物品管理服务类

功能说明：
- 物品分类列表查询
- 创建物品分类
- 获取分类详情
- 更新分类信息
- 删除分类
- 物品列表查询（支持分页、搜索）
- 创建物品
- 获取物品详情
- 更新物品信息
- 删除物品（软删除）

设计原则：
- 面向对象：使用 GoodsService 类封装物品管理逻辑
- 声明式：使用 Pydantic 定义数据模型
- 封装清晰：提供简洁的公共方法

作者：CampusAssetManager开发团队
日期：2026-01-06
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..models.goods_category import GoodsCategory
from ..models.goods_info import Goods
from ..schemas.goods import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
    GoodsCreate,
    GoodsUpdate,
    GoodsQuery,
    GoodsResponse,
    GoodsListResponse
)


class GoodsService:
    """
    物品管理服务类
    
    负责处理物品相关的所有业务逻辑
    """
    
    # ==================== 物品分类管理 ====================
    
    def get_category_list(
        self,
        db: Session
    ) -> CategoryListResponse:
        """
        查询物品分类列表
        
        Args:
            db (Session): 数据库会话
        
        Returns:
            CategoryListResponse: 分类列表响应
        
        Examples:
            >>> service = GoodsService()
            >>> result = service.get_category_list(db)
        """
        # 查询所有分类
        categories = db.query(GoodsCategory).order_by(
            GoodsCategory.sort_order,
            GoodsCategory.category_id
        ).all()
        
        # 转换为响应模型
        items = [CategoryResponse.model_validate(category) for category in categories]
        
        return CategoryListResponse(
            items=items,
            total=len(items)
        )
    
    def create_category(
        self,
        category_data: CategoryCreate,
        db: Session
    ) -> CategoryResponse:
        """
        创建新分类
        
        Args:
            category_data (CategoryCreate): 分类创建数据
            db (Session): 数据库会话
        
        Returns:
            CategoryResponse: 创建的分类信息
        
        Raises:
            ValueError: 分类编码已存在
        
        Examples:
            >>> service = GoodsService()
            >>> category_data = CategoryCreate(
            ...     category_name="办公设备",
            ...     category_code="BG_SB"
            ... )
            >>> category = service.create_category(category_data, db)
        """
        # 检查分类编码是否已存在
        existing_category = db.query(GoodsCategory).filter(
            GoodsCategory.category_code == category_data.category_code
        ).first()
        
        if existing_category:
            raise ValueError("分类编码已存在")
        
        # 计算分类层级
        level = 1
        if category_data.parent_id:
            parent_category = db.query(GoodsCategory).filter(
                GoodsCategory.category_id == category_data.parent_id
            ).first()
            if parent_category:
                level = parent_category.level + 1
            else:
                raise ValueError("父分类不存在")
        
        # 创建分类对象
        new_category = GoodsCategory(
            category_name=category_data.category_name,
            category_code=category_data.category_code,
            parent_id=category_data.parent_id,
            level=level,
            description=category_data.description,
            sort_order=category_data.sort_order,
            is_active=category_data.is_active
        )
        
        # 保存到数据库
        try:
            db.add(new_category)
            db.commit()
            db.refresh(new_category)
            return CategoryResponse.model_validate(new_category)
        except Exception as e:
            db.rollback()
            raise Exception(f"创建分类失败: {str(e)}")
    
    def get_category_by_id(
        self,
        category_id: int,
        db: Session
    ) -> CategoryResponse:
        """
        根据ID获取分类详情
        
        Args:
            category_id (int): 分类ID
            db (Session): 数据库会话
        
        Returns:
            CategoryResponse: 分类信息
        
        Raises:
            ValueError: 分类不存在
        
        Examples:
            >>> service = GoodsService()
            >>> category = service.get_category_by_id(1, db)
        """
        category = db.query(GoodsCategory).filter(
            GoodsCategory.category_id == category_id
        ).first()
        
        if not category:
            raise ValueError("分类不存在")
        
        return CategoryResponse.model_validate(category)
    
    def update_category(
        self,
        category_id: int,
        category_data: CategoryUpdate,
        db: Session
    ) -> CategoryResponse:
        """
        更新分类信息
        
        Args:
            category_id (int): 分类ID
            category_data (CategoryUpdate): 分类更新数据
            db (Session): 数据库会话
        
        Returns:
            CategoryResponse: 更新后的分类信息
        
        Raises:
            ValueError: 分类不存在
        
        Examples:
            >>> service = GoodsService()
            >>> category_data = CategoryUpdate(category_name="新分类名")
            >>> category = service.update_category(1, category_data, db)
        """
        # 查询分类
        category = db.query(GoodsCategory).filter(
            GoodsCategory.category_id == category_id
        ).first()
        
        if not category:
            raise ValueError("分类不存在")
        
        # 更新字段
        update_dict = category_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(category, field, value)
        
        # 保存到数据库
        try:
            db.commit()
            db.refresh(category)
            return CategoryResponse.model_validate(category)
        except Exception as e:
            db.rollback()
            raise Exception(f"更新分类失败: {str(e)}")
    
    def delete_category(
        self,
        category_id: int,
        db: Session
    ) -> None:
        """
        删除分类
        
        注意：删除分类前需要检查是否有子分类或关联的物品
        
        Args:
            category_id (int): 分类ID
            db (Session): 数据库会话
        
        Raises:
            ValueError: 分类不存在、有子分类或有关联物品
        
        Examples:
            >>> service = GoodsService()
            >>> service.delete_category(1, db)
        """
        # 查询分类
        category = db.query(GoodsCategory).filter(
            GoodsCategory.category_id == category_id
        ).first()
        
        if not category:
            raise ValueError("分类不存在")
        
        # 检查是否有子分类
        has_children = db.query(GoodsCategory).filter(
            GoodsCategory.parent_id == category_id
        ).first()
        
        if has_children:
            raise ValueError("该分类下包含子分类，无法删除")
        
        # 检查是否有关联的物品
        has_goods = db.query(Goods).filter(
            Goods.category_id == category_id
        ).first()
        
        if has_goods:
            raise ValueError("该分类下包含物品，无法删除")
        
        # 删除分类
        try:
            db.delete(category)
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"删除分类失败: {str(e)}")
    
    # ==================== 物品信息管理 ====================
    
    def get_goods_list(
        self,
        query: GoodsQuery,
        db: Session
    ) -> GoodsListResponse:
        """
        查询物品列表
        
        Args:
            query (GoodsQuery): 查询参数（分页、搜索、筛选）
            db (Session): 数据库会话
        
        Returns:
            GoodsListResponse: 物品列表响应
        
        Examples:
            >>> service = GoodsService()
            >>> query = GoodsQuery(page=1, page_size=20)
            >>> result = service.get_goods_list(query, db)
        """
        # 构建基础查询（关联分类表）
        db_query = db.query(
            Goods,
            GoodsCategory.category_name
        ).outerjoin(
            GoodsCategory,
            Goods.category_id == GoodsCategory.category_id
        )
        
        # 搜索过滤
        if query.search:
            search_pattern = f"%{query.search}%"
            db_query = db_query.filter(
                or_(
                    Goods.goods_name.like(search_pattern),
                    Goods.goods_code.like(search_pattern)
                )
            )
        
        # 分类过滤
        if query.category_id:
            db_query = db_query.filter(Goods.category_id == query.category_id)
        
        # 状态过滤
        if query.status:
            db_query = db_query.filter(Goods.status == query.status)
        
        # 计算总数
        total = db_query.count()
        
        # 分页
        offset = (query.page - 1) * query.page_size
        goods_list = db_query.offset(offset).limit(query.page_size).all()
        
        # 转换为响应模型
        items = []
        for goods, category_name in goods_list:
            goods_dict = {
                **GoodsResponse.model_validate(goods).model_dump(),
                'category_name': category_name
            }
            items.append(GoodsResponse(**goods_dict))
        
        return GoodsListResponse(
            items=items,
            total=total,
            page=query.page,
            page_size=query.page_size
        )
    
    def create_goods(
        self,
        goods_data: GoodsCreate,
        db: Session
    ) -> GoodsResponse:
        """
        创建新物品
        
        Args:
            goods_data (GoodsCreate): 物品创建数据
            db (Session): 数据库会话
        
        Returns:
            GoodsResponse: 创建的物品信息
        
        Raises:
            ValueError: 物品编码已存在、分类不存在
        
        Examples:
            >>> service = GoodsService()
            >>> goods_data = GoodsCreate(
            ...     goods_name="笔记本电脑",
            ...     goods_code="NB_001",
            ...     category_id=1,
            ...     unit="台",
            ...     purchase_price=8000.00
            ... )
            >>> goods = service.create_goods(goods_data, db)
        """
        # 检查物品编码是否已存在
        existing_goods = db.query(Goods).filter(
            Goods.goods_code == goods_data.goods_code
        ).first()
        
        if existing_goods:
            raise ValueError("物品编码已存在")
        
        # 检查分类是否存在
        category = db.query(GoodsCategory).filter(
            GoodsCategory.category_id == goods_data.category_id
        ).first()
        
        if not category:
            raise ValueError("分类不存在")
        
        # 创建物品对象
        new_goods = Goods(
            goods_name=goods_data.goods_name,
            goods_code=goods_data.goods_code,
            category_id=goods_data.category_id,
            specification=goods_data.specification,
            unit=goods_data.unit,
            purchase_price=goods_data.purchase_price,
            retail_price=goods_data.retail_price,
            description=goods_data.description,
            status=goods_data.status
        )
        
        # 保存到数据库
        try:
            db.add(new_goods)
            db.commit()
            db.refresh(new_goods)
            return GoodsResponse.model_validate(new_goods)
        except Exception as e:
            db.rollback()
            raise Exception(f"创建物品失败: {str(e)}")
    
    def get_goods_by_id(
        self,
        goods_id: int,
        db: Session
    ) -> GoodsResponse:
        """
        根据ID获取物品详情
        
        Args:
            goods_id (int): 物品ID
            db (Session): 数据库会话
        
        Returns:
            GoodsResponse: 物品信息
        
        Raises:
            ValueError: 物品不存在
        
        Examples:
            >>> service = GoodsService()
            >>> goods = service.get_goods_by_id(1, db)
        """
        # 查询物品（包含分类信息）
        result = db.query(
            Goods,
            GoodsCategory.category_name
        ).outerjoin(
            GoodsCategory,
            Goods.category_id == GoodsCategory.category_id
        ).filter(
            Goods.goods_id == goods_id
        ).first()
        
        if not result:
            raise ValueError("物品不存在")
        
        goods, category_name = result
        
        # 构建响应数据
        goods_dict = {
            **GoodsResponse.model_validate(goods).model_dump(),
            'category_name': category_name
        }
        
        return GoodsResponse(**goods_dict)
    
    def update_goods(
        self,
        goods_id: int,
        goods_data: GoodsUpdate,
        db: Session
    ) -> GoodsResponse:
        """
        更新物品信息
        
        Args:
            goods_id (int): 物品ID
            goods_data (GoodsUpdate): 物品更新数据
            db (Session): 数据库会话
        
        Returns:
            GoodsResponse: 更新后的物品信息
        
        Raises:
            ValueError: 物品不存在、分类不存在
        
        Examples:
            >>> service = GoodsService()
            >>> goods_data = GoodsUpdate(goods_name="新名称")
            >>> goods = service.update_goods(1, goods_data, db)
        """
        # 查询物品
        goods = db.query(Goods).filter(Goods.goods_id == goods_id).first()
        
        if not goods:
            raise ValueError("物品不存在")
        
        # 如果更新分类，需要检查分类是否存在
        if goods_data.category_id is not None:
            category = db.query(GoodsCategory).filter(
                GoodsCategory.category_id == goods_data.category_id
            ).first()
            
            if not category:
                raise ValueError("分类不存在")
        
        # 更新字段
        update_dict = goods_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(goods, field, value)
        
        # 保存到数据库
        try:
            db.commit()
            db.refresh(goods)
            return GoodsResponse.model_validate(goods)
        except Exception as e:
            db.rollback()
            raise Exception(f"更新物品失败: {str(e)}")
    
    def delete_goods(
        self,
        goods_id: int,
        db: Session
    ) -> None:
        """
        删除物品（软删除）
        
        注意：此操作为软删除，仅将物品的 status 字段设置为 2（报废）
        
        Args:
            goods_id (int): 物品ID
            db (Session): 数据库会话
        
        Raises:
            ValueError: 物品不存在
        
        Examples:
            >>> service = GoodsService()
            >>> service.delete_goods(1, db)
        """
        # 查询物品
        goods = db.query(Goods).filter(Goods.goods_id == goods_id).first()
        
        if not goods:
            raise ValueError("物品不存在")
        
        # 软删除：设置状态为2（报废）
        try:
            goods.status = 2
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"删除物品失败: {str(e)}")