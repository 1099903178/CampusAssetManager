"""
CampusAssetManager/backend/app/api/v1/goods.py
物品管理API端点

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
- 依赖注入：使用FastAPI的依赖注入系统
- 声明式：使用Pydantic定义请求和响应模型
- RESTful：遵循REST API设计规范
- 权限控制：管理员管理，普通用户只读

作者：CampusAssetManager开发团队
日期：2026-01-06
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database.config import get_db
from ...schemas.goods import (
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
from ...services.goods_service import GoodsService

# 创建路由器
router = APIRouter(prefix="/goods", tags=["物品管理"])

# 创建物品服务实例
goods_service = GoodsService()


# ==================== 物品分类管理 ====================

@router.get("/categories", summary="查询物品分类列表")
def get_categories(
    db: Session = Depends(get_db)
):
    """
    查询物品分类列表接口
    
    Args:
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 查询失败时返回
    
    Examples:
        GET /v1/goods/categories
    """
    try:
        # 调用服务层查询分类列表
        result = goods_service.get_category_list(db)
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "查询成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询分类列表失败: {str(e)}"
        )


@router.post("/categories", summary="创建新分类")
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db)
):
    """
    创建新分类接口
    
    Args:
        category_data (CategoryCreate): 分类创建数据
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 创建失败时返回
    
    Examples:
        POST /v1/goods/categories
        {
            "category_name": "办公设备",
            "category_code": "BG_SB",
            "parent_id": null,
            "description": "办公室使用的各类设备",
            "sort_order": 1,
            "is_active": 1
        }
    """
    try:
        # 调用服务层创建分类
        category = goods_service.create_category(category_data, db)
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "创建成功",
            "data": category
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建分类失败: {str(e)}"
        )


@router.get("/categories/{category_id}", summary="获取分类详情")
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    获取分类详情接口
    
    Args:
        category_id (int): 分类ID
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 分类不存在时返回
    
    Examples:
        GET /v1/goods/categories/1
    """
    try:
        # 调用服务层获取分类详情
        category = goods_service.get_category_by_id(category_id, db)
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "查询成功",
            "data": category
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分类详情失败: {str(e)}"
        )


@router.put("/categories/{category_id}", summary="更新分类信息")
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """
    更新分类信息接口
    
    Args:
        category_id (int): 分类ID
        category_data (CategoryUpdate): 分类更新数据
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 分类不存在或更新失败时返回
    
    Examples:
        PUT /v1/goods/categories/1
        {
            "category_name": "新分类名称",
            "description": "更新后的描述",
            "sort_order": 2,
            "is_active": 1
        }
    """
    try:
        # 调用服务层更新分类信息
        category = goods_service.update_category(category_id, category_data, db)
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "更新成功",
            "data": category
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新分类信息失败: {str(e)}"
        )


@router.delete("/categories/{category_id}", summary="删除分类")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    删除分类接口
    
    注意：删除分类前会检查是否有子分类或关联的物品
    
    Args:
        category_id (int): 分类ID
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 分类不存在或删除失败时返回
    
    Examples:
        DELETE /v1/goods/categories/1
    """
    try:
        # 调用服务层删除分类
        goods_service.delete_category(category_id, db)
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "删除成功",
            "data": {"category_id": category_id}
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除分类失败: {str(e)}"
        )


# ==================== 物品信息管理 ====================

@router.get("", summary="查询物品列表")
def get_goods_list(
    page: int = 1,
    page_size: int = 20,
    search: str = None,
    category_id: int = None,
    status: int = None,
    db: Session = Depends(get_db)
):
    """
    查询物品列表接口
    
    支持分页、搜索和多条件筛选。
    
    Args:
        page (int): 页码（默认1）
        page_size (int): 每页数量（默认20，最大100）
        search (str): 搜索关键词（物品名称、编码）
        category_id (int): 按分类筛选
        status (int): 按状态筛选（1正常/2报废/3维修中）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 查询失败时返回
    
    Examples:
        GET /v1/goods/?page=1&page_size=20&search=笔记本
        
        GET /v1/goods/?category_id=1&status=1
    """
    try:
        # 构建查询参数
        query = GoodsQuery(
            page=page,
            page_size=page_size,
            search=search,
            category_id=category_id,
            status=status
        )
        
        # 调用服务层查询物品列表
        result = goods_service.get_goods_list(query, db)
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "查询成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询物品列表失败: {str(e)}"
        )


@router.post("", summary="创建新物品")
def create_goods(
    goods_data: GoodsCreate,
    db: Session = Depends(get_db)
):
    """
    创建新物品接口
    
    Args:
        goods_data (GoodsCreate): 物品创建数据
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 创建失败时返回
    
    Examples:
        POST /v1/goods/
        {
            "goods_name": "笔记本电脑",
            "goods_code": "NB_001",
            "category_id": 1,
            "specification": "ThinkPad X1 Carbon",
            "unit": "台",
            "purchase_price": 8000.00,
            "retail_price": 10000.00,
            "description": "高性能商务笔记本",
            "status": 1
        }
    """
    try:
        # 调用服务层创建物品
        goods = goods_service.create_goods(goods_data, db)
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "创建成功",
            "data": goods
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建物品失败: {str(e)}"
        )


@router.get("/{goods_id}", summary="获取物品详情")
def get_goods(
    goods_id: int,
    db: Session = Depends(get_db)
):
    """
    获取物品详情接口
    
    Args:
        goods_id (int): 物品ID
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 物品不存在时返回
    
    Examples:
        GET /v1/goods/1
    """
    try:
        # 调用服务层获取物品详情
        goods = goods_service.get_goods_by_id(goods_id, db)
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "查询成功",
            "data": goods
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取物品详情失败: {str(e)}"
        )


@router.put("/{goods_id}", summary="更新物品信息")
def update_goods(
    goods_id: int,
    goods_data: GoodsUpdate,
    db: Session = Depends(get_db)
):
    """
    更新物品信息接口
    
    Args:
        goods_id (int): 物品ID
        goods_data (GoodsUpdate): 物品更新数据
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 物品不存在或更新失败时返回
    
    Examples:
        PUT /v1/goods/1
        {
            "goods_name": "新物品名称",
            "specification": "更新后的规格",
            "purchase_price": 9000.00,
            "status": 1
        }
    """
    try:
        # 调用服务层更新物品信息
        goods = goods_service.update_goods(goods_id, goods_data, db)
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "更新成功",
            "data": goods
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新物品信息失败: {str(e)}"
        )


@router.delete("/{goods_id}", summary="删除物品")
def delete_goods(
    goods_id: int,
    db: Session = Depends(get_db)
):
    """
    删除物品接口（软删除）
    
    注意：此操作为软删除，仅将物品的 status 字段设置为 2（报废）
    
    Args:
        goods_id (int): 物品ID
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 物品不存在或删除失败时返回
    
    Examples:
        DELETE /v1/goods/1
    """
    try:
        # 调用服务层删除物品（软删除）
        goods_service.delete_goods(goods_id, db)
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "删除成功",
            "data": {"goods_id": goods_id}
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除物品失败: {str(e)}"
        )