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
    StockOutQuery,
    StockCheckCreate,
    StockCheckResponse,
    StockCheckListResponse,
    StockCheckQuery,
    StockAdjustCreate,
    StockAdjustResponse,
    StockLedgerListResponse,
    StockLedgerQuery,
    StockQueryEnriched,
    StockResponseEnhanced,
    StockListResponseEnhanced,
    StockThresholdUpdate,
    StockThresholdBatchUpdate
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


# ==================== 盘点管理 ====================

@router.post("/check", summary="创建盘点记录")
def create_stock_check(
    check_data: StockCheckCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建盘点记录接口
    
    创建盘点记录并计算账面与实盘差异，生成盘点单号。
    
    权限要求：
    - 所有登录用户可创建盘点记录
    
    Args:
        check_data (StockCheckCreate): 盘点数据
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 物品不存在或创建失败时返回
    
    Examples:
        POST /v1/stock/check
        {
            "goods_id": 1,
            "actual_stock": 100,
            "remark": "物品完好无损"
        }
    """
    try:
        # 调用服务层创建盘点记录
        result = stock_service.create_stock_check(
            check_data=check_data,
            checker_id=current_user.user_id,
            db=db
        )
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "盘点成功",
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
            detail=f"创建盘点记录失败: {str(e)}"
        )


@router.get("/check", summary="查询盘点记录列表")
def get_stock_check_list(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    goods_id: Optional[int] = None,
    check_result: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询盘点记录列表接口
    
    支持分页、搜索、按物品筛选、按盘点结果筛选、按日期范围筛选。
    
    权限要求：
    - 所有登录用户可查看
    
    Args:
        page (int): 页码
        page_size (int): 每页数量
        search (str): 搜索关键词（盘点单号、物品名称）
        goods_id (int): 按物品ID筛选
        check_result (str): 按盘点结果筛选（normal/over/short）
        start_date (str): 开始日期（YYYY-MM-DD）
        end_date (str): 结束日期（YYYY-MM-DD）
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 查询失败时返回
    
    Examples:
        GET /v1/stock/check?page=1&page_size=20
        
        GET /v1/stock/check?search=CHK-20240113
        
        GET /v1/stock/check?goods_id=1&check_result=short
    """
    try:
        # 构建查询参数
        from datetime import datetime
        query = StockCheckQuery(
            page=page,
            page_size=page_size,
            search=search,
            goods_id=goods_id,
            check_result=check_result,
            start_date=datetime.strptime(start_date, "%Y-%m-%d") if start_date else None,
            end_date=datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        )
        
        # 调用服务层查询盘点记录列表
        result = stock_service.get_stock_check_list(query, db)
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "查询成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询盘点记录列表失败: {str(e)}"
        )


@router.get("/check/{check_id}", summary="获取盘点详情")
def get_stock_check_detail(
    check_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取盘点详情接口
    
    权限要求：
    - 所有登录用户可查看
    
    Args:
        check_id (int): 盘点记录ID
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 查询失败时返回
    
    Examples:
        GET /v1/stock/check/1
    """
    try:
        # 调用服务层获取盘点详情
        result = stock_service.get_stock_check_by_id(check_id, db)
        
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
            detail=f"获取盘点详情失败: {str(e)}"
        )


# ==================== 库存调整 ====================

@router.put("/adjust", summary="手动调整库存")
def adjust_stock(
    adjust_data: StockAdjustCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    手动调整库存接口
    
    手动调整库存数量，记录调整原因。
    
    权限要求：
    - 仅超级管理员可调整库存
    
    Args:
        adjust_data (StockAdjustCreate): 调整数据
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 权限不足或调整失败时返回
    
    Examples:
        PUT /v1/stock/adjust
        {
            "goods_id": 1,
            "adjust_quantity": 10,
            "adjust_reason": "盘亏调整"
        }
    """
    try:
        # 权限验证：仅超级管理员可调整库存
        if current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，仅超级管理员可调整库存"
            )
        
        # 调用服务层调整库存
        result = stock_service.adjust_stock(
            adjust_data=adjust_data,
            operator_id=current_user.user_id,
            db=db
        )
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "库存调整成功",
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
            detail=f"库存调整失败: {str(e)}"
        )


# ==================== 台账查询 ====================

@router.get("/ledger", summary="查询库存台账")
def get_stock_ledger(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    goods_id: Optional[int] = None,
    operation_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询库存台账接口
    
    合并查询入库、出库、盘点记录，支持时间范围和操作类型筛选。
    
    权限要求：
    - 所有登录用户可查看
    
    Args:
        page (int): 页码
        page_size (int): 每页数量
        search (str): 搜索关键词（操作单号、物品名称）
        goods_id (int): 按物品ID筛选
        operation_type (str): 按操作类型筛选（in/out/check）
        start_date (str): 开始日期（YYYY-MM-DD）
        end_date (str): 结束日期（YYYY-MM-DD）
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 查询失败时返回
    
    Examples:
        GET /v1/stock/ledger?page=1&page_size=20
        
        GET /v1/stock/ledger?operation_type=in&start_date=2024-01-01&end_date=2024-01-31
    """
    try:
        # 构建查询参数
        from datetime import datetime
        query = StockLedgerQuery(
            page=page,
            page_size=page_size,
            search=search,
            goods_id=goods_id,
            operation_type=operation_type,
            start_date=datetime.strptime(start_date, "%Y-%m-%d") if start_date else None,
            end_date=datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        )
        
        # 调用服务层查询库存台账
        result = stock_service.get_stock_ledger(query, db)
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "查询成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询库存台账失败: {str(e)}"
        )


# ==================== 库存查询增强 ====================

@router.get("/list/enhanced", summary="增强库存查询")
def get_stock_list_enhanced(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    stock_status: Optional[str] = None,
    min_stock_only: bool = False,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    增强库存查询接口
    
    支持按预警状态筛选（低库存/库存过高/正常）。
    
    权限要求：
    - 所有登录用户可查看
    
    Args:
        page (int): 页码
        page_size (int): 每页数量
        search (str): 搜索关键词（物品名称、编码）
        category_id (int): 按分类ID筛选
        stock_status (str): 按库存状态筛选（normal/low/over）
        min_stock_only (bool): 只显示低于最小库存的物品
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 查询失败时返回
    
    Examples:
        GET /v1/stock/list/enhanced?page=1&page_size=20
        
        GET /v1/stock/list/enhanced?stock_status=low
        
        GET /v1/stock/list/enhanced?min_stock_only=true
    """
    try:
        # 构建查询参数
        query = StockQueryEnriched(
            page=page,
            page_size=page_size,
            search=search,
            category_id=category_id,
            stock_status=stock_status,
            min_stock_only=min_stock_only
        )
        
        # 调用服务层查询增强库存列表
        result = stock_service.get_stock_list_enhanced(query, db)
        
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


# ==================== 库存阈值同步 ====================

@router.put("/thresholds/sync", summary="同步库存阈值")
def sync_stock_thresholds(
    min_stock: int,
    max_stock: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    同步库存阈值接口
    
    将全局库存阈值批量同步到所有物品的库存记录。
    
    权限要求：
    - 超级管理员（super_admin）可以同步
    
    Args:
        min_stock (int): 最小库存阈值
        max_stock (int): 最大库存阈值
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 权限不足或同步失败时返回
    
    Examples:
        PUT /v1/stock/thresholds/sync?min_stock=10&max_stock=1000
    """
    try:
        # 权限检查：只有超级管理员可以同步
        if current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，只有超级管理员可以同步库存阈值"
            )
        
        # 调用服务层同步库存阈值
        result = stock_service.sync_stock_thresholds(min_stock, max_stock, db)
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": f"同步完成，共 {result['total']} 条记录，更新 {result['updated']} 条",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步库存阈值失败: {str(e)}"
        )


# ==================== 库存阈值管理 ====================

@router.put("/thresholds", summary="更新物品库存阈值")
def update_stock_threshold(
    threshold_data: StockThresholdUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新单个物品的库存阈值接口
    
    权限要求：
    - 超级管理员（super_admin）可以更新
    
    Args:
        threshold_data (StockThresholdUpdate): 库存阈值更新数据
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 权限不足或更新失败时返回
    
    Examples:
        PUT /v1/stock/thresholds
        Body: {
            "goods_id": 1,
            "min_stock": 10,
            "max_stock": 100
        }
    """
    try:
        # 权限检查：只有超级管理员可以更新
        if current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，只有超级管理员可以更新库存阈值"
            )
        
        # 调用服务层更新库存阈值
        result = stock_service.update_stock_threshold(threshold_data, db)
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "库存阈值更新成功",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新库存阈值失败: {str(e)}"
        )


@router.put("/thresholds/batch", summary="批量更新库存阈值")
def batch_update_stock_thresholds(
    batch_data: StockThresholdBatchUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量更新所有物品的库存阈值接口
    
    权限要求：
    - 超级管理员（super_admin）可以更新
    
    Args:
        batch_data (StockThresholdBatchUpdate): 批量更新数据
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 权限不足或更新失败时返回
    
    Examples:
        PUT /v1/stock/thresholds/batch
        Body: {
            "min_stock": 10,
            "max_stock": 100
        }
    """
    try:
        # 权限检查：只有超级管理员可以更新
        if current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，只有超级管理员可以批量更新库存阈值"
            )
        
        # 调用服务层批量更新库存阈值
        result = stock_service.batch_update_stock_thresholds(batch_data, db)
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": f"批量更新完成，共 {result['total']} 条记录，更新 {result['updated']} 条",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量更新库存阈值失败: {str(e)}"
        )