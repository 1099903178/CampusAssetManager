"""
CampusAssetManager/backend/app/api/v1/stock.py
库存管理API端点

功能说明：
- 入库操作（创建入库记录）
- 查询入库记录列表（支持分页、搜索）
- 获取入库详情
- 出库操作（创建出库记录）
- 查询出库记录列表（支持分页、搜索）
- 获取出库详情

设计原则：
- 依赖注入：使用FastAPI的依赖注入系统
- 声明式：使用Pydantic定义请求和响应模型
- RESTful：遵循REST API设计规范
- 权限控制：管理员创建入库，所有登录用户可创建出库

作者：CampusAssetManager开发团队
日期：2026-01-07
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ...database.config import get_db
from ...schemas.stock import (
    StockInCreate,
    StockInResponse,
    StockInListResponse,
    StockInQuery,
    StockOutCreate,
    StockOutResponse,
    StockOutListResponse,
    StockOutQuery
)
from ...services.stock_service import StockService
from .auth import get_current_user
from ...schemas.user import UserResponse

# 创建路由器
router = APIRouter(prefix="/stock", tags=["库存管理"])

# 创建库存服务实例
stock_service = StockService()


# ==================== 入库管理 ====================

@router.post("/in", summary="创建入库记录")
def create_stock_in(
    stock_in_data: StockInCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建入库记录接口
    
    创建入库记录并更新库存。
    
    权限要求：
    - 仅管理员可创建入库记录
    
    Args:
        stock_in_data (StockInCreate): 入库数据
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 权限不足或创建失败时返回
    
    Examples:
        POST /v1/stock/in
        {
            "goods_id": 1,
            "in_quantity": 10,
            "unit_price": 100.00,
            "total_amount": 1000.00,
            "batch_no": "BATCH-001",
            "supplier": "供应商A",
            "remark": "第一批入库"
        }
    """
    try:
        # 权限验证：仅管理员可创建入库记录
        if current_user.role not in ["admin", "super_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，仅管理员可创建入库记录"
            )
        
        # 调用服务层创建入库记录
        result = stock_service.create_stock_in(
            stock_in_data=stock_in_data,
            operator_id=current_user.user_id,
            db=db
        )
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "入库成功",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建入库记录失败: {str(e)}"
        )


@router.get("/in", summary="查询入库记录列表")
def get_stock_in_list(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    goods_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询入库记录列表接口
    
    支持分页、搜索、按物品筛选、按日期范围筛选。
    
    权限要求：
    - 所有登录用户可查看
    
    Args:
        page (int): 页码
        page_size (int): 每页数量
        search (str): 搜索关键词（入库单号、物品名称）
        goods_id (int): 按物品ID筛选
        start_date (str): 开始日期（YYYY-MM-DD）
        end_date (str): 结束日期（YYYY-MM-DD）
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 查询失败时返回
    
    Examples:
        GET /v1/stock/in?page=1&page_size=20
        
        GET /v1/stock/in?search=IN-20240107
        
        GET /v1/stock/in?goods_id=1&start_date=2024-01-01&end_date=2024-01-31
    """
    try:
        # 构建查询参数
        from datetime import datetime
        query = StockInQuery(
            page=page,
            page_size=page_size,
            search=search,
            goods_id=goods_id,
            start_date=datetime.strptime(start_date, "%Y-%m-%d") if start_date else None,
            end_date=datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        )
        
        # 调用服务层查询入库记录列表
        result = stock_service.get_stock_in_list(query, db)
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "查询成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询入库记录列表失败: {str(e)}"
        )


@router.get("/in/{in_id}", summary="获取入库详情")
def get_stock_in_detail(
    in_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取入库详情接口
    
    权限要求：
    - 所有登录用户可查看
    
    Args:
        in_id (int): 入库记录ID
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 查询失败时返回
    
    Examples:
        GET /v1/stock/in/1
    """
    try:
        # 调用服务层获取入库详情
        result = stock_service.get_stock_in_by_id(in_id, db)
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "查询成功",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取入库详情失败: {str(e)}"
        )


# ==================== 出库管理 ====================

@router.post("/out", summary="创建出库记录")
def create_stock_out(
    stock_out_data: StockOutCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建出库记录接口
    
    创建出库记录并扣减库存，检查库存是否充足。
    
    权限要求：
    - 所有登录用户可创建出库记录
    
    Args:
        stock_out_data (StockOutCreate): 出库数据
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 库存不足或创建失败时返回
    
    Examples:
        POST /v1/stock/out
        {
            "goods_id": 1,
            "out_quantity": 5,
            "unit_price": 100.00,
            "total_amount": 500.00,
            "receiver": "张三",
            "department": "技术部",
            "purpose": "办公使用",
            "remark": "紧急出库"
        }
    """
    try:
        # 调用服务层创建出库记录
        result = stock_service.create_stock_out(
            stock_out_data=stock_out_data,
            operator_id=current_user.user_id,
            db=db
        )
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "出库成功",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建出库记录失败: {str(e)}"
        )


@router.get("/out", summary="查询出库记录列表")
def get_stock_out_list(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    goods_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询出库记录列表接口
    
    支持分页、搜索、按物品筛选、按日期范围筛选。
    
    权限要求：
    - 所有登录用户可查看
    
    Args:
        page (int): 页码
        page_size (int): 每页数量
        search (str): 搜索关键词（出库单号、物品名称）
        goods_id (int): 按物品ID筛选
        start_date (str): 开始日期（YYYY-MM-DD）
        end_date (str): 结束日期（YYYY-MM-DD）
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 查询失败时返回
    
    Examples:
        GET /v1/stock/out?page=1&page_size=20
        
        GET /v1/stock/out?search=OUT-20240107
        
        GET /v1/stock/out?goods_id=1&start_date=2024-01-01&end_date=2024-01-31
    """
    try:
        # 构建查询参数
        from datetime import datetime
        query = StockOutQuery(
            page=page,
            page_size=page_size,
            search=search,
            goods_id=goods_id,
            start_date=datetime.strptime(start_date, "%Y-%m-%d") if start_date else None,
            end_date=datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        )
        
        # 调用服务层查询出库记录列表
        result = stock_service.get_stock_out_list(query, db)
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "查询成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询出库记录列表失败: {str(e)}"
        )


@router.get("/out/{out_id}", summary="获取出库详情")
def get_stock_out_detail(
    out_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取出库详情接口
    
    权限要求：
    - 所有登录用户可查看
    
    Args:
        out_id (int): 出库记录ID
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 查询失败时返回
    
    Examples:
        GET /v1/stock/out/1
    """
    try:
        # 调用服务层获取出库详情
        result = stock_service.get_stock_out_by_id(out_id, db)
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "查询成功",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取出库详情失败: {str(e)}"
        )


# ==================== 库存管理 ====================

@router.get("/list", summary="查询库存列表")
def get_stock_list(
    page: int = 1,
    page_size: int = 20,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询库存列表接口
    
    支持分页查询，显示所有物品的当前库存。
    
    权限要求：
    - 所有登录用户可查看
    
    Args:
        page (int): 页码
        page_size (int): 每页数量
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 查询失败时返回
    
    Examples:
        GET /v1/stock?page=1&page_size=20
    """
    try:
        # 调用服务层查询库存列表
        result = stock_service.get_stock_list(
            page=page,
            page_size=page_size,
            db=db
        )
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "查询成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询库存列表失败: {str(e)}"
        )