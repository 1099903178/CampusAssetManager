"""
CampusAssetManager/backend/app/api/v1/system.py
系统管理API端点

功能说明：
- 查询操作日志列表（支持分页、搜索、筛选）
- 获取系统配置
- 修改系统配置
- 系统配置初始化

设计原则：
- 依赖注入：使用FastAPI的依赖注入系统
- 声明式：使用Pydantic定义请求和响应模型
- RESTful：遵循REST API设计规范
- 权限控制：超级管理员修改配置，所有登录用户查看日志

作者：CampusAssetManager开发团队
日期：2026-01-10
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional

from ...database.config import get_db
from ...schemas.system import (
    OperationLogResponse,
    OperationLogListResponse,
    OperationLogQuery,
    ConfigResponse,
    ConfigUpdate,
    ConfigBatchUpdate,
    SystemConfigResponse,
    SystemResetRequest,
    BackupListResponse,
    BackupCreateResponse,
    RestoreResponse,
    RestoreRequest
)
from ...services.system_service import (
    operation_log_service,
    config_service,
    backup_restore_service
)
from .auth import get_current_user
from ...schemas.user import UserResponse

# 创建路由器
router = APIRouter(prefix="/system", tags=["系统管理"])


@router.post("/reset", summary="系统重置")
def reset_system(
    reset_data: SystemResetRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    系统完全重置接口
    
    清空所有业务数据、操作日志和系统配置，并重新初始化默认配置
    
    权限要求：
    - 仅超级管理员可执行
    
    重置内容包括：
    - 物品分类和物品信息
    - 库存数据
    - 出入库记录
    - 盘点记录
    - 操作日志
    - 系统配置（恢复默认配置）
    
    Args:
        reset_data (SystemResetRequest): 重置请求数据
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 权限不足或重置失败时返回
    
    Examples:
        POST /v1/system/reset
        {
            "password": "admin123"
        }
    """
    try:
        # 权限验证：仅超级管理员可重置系统
        if current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，仅超级管理员可重置系统"
            )
        
        # 调用服务层执行系统重置
        config_service.reset_system(reset_data, db)
        
        # 返回成功响应
        return {
            "code": 200,
            "message": "系统重置成功",
            "data": {}
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"系统重置失败: {str(e)}"
        )




# ==================== 操作日志管理 ====================

@router.get("/operation-logs", summary="查询操作日志列表")
def get_operation_logs(
    page: int = 1,
    page_size: int = 20,
    username: Optional[str] = None,
    operation: Optional[str] = None,
    module: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    result: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询操作日志列表接口
    
    支持分页、搜索、按用户/时间范围/操作类型/模块/结果筛选。
    
    权限要求：
    - 所有登录用户可查看
    
    Args:
        page (int): 页码
        page_size (int): 每页数量
        username (str): 按用户名筛选
        operation (str): 按操作类型筛选（login/create/update/delete等）
        module (str): 按模块筛选（auth/goods/stock等）
        start_date (str): 开始日期（YYYY-MM-DD）
        end_date (str): 结束日期（YYYY-MM-DD）
        result (str): 按结果筛选（success/failed）
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 查询失败时返回
    
    Examples:
        GET /v1/system/operation-logs?page=1&page_size=20
        
        GET /v1/system/operation-logs?username=admin&operation=login
        
        GET /v1/system/operation-logs?start_date=2024-01-01&end_date=2024-01-31
    """
    try:
        # 构建查询参数
        from datetime import datetime
        
        # 处理日期参数
        parsed_start_date = None
        parsed_end_date = None
        if start_date and start_date.strip():
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                pass
        if end_date and end_date.strip():
            try:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                pass
        
        query = OperationLogQuery(
            page=page,
            page_size=page_size,
            username=username,
            operation=operation,
            module=module,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            result=result
        )
        
        # 调用服务层查询操作日志列表
        result = operation_log_service.get_logs(query, db)
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "查询成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询操作日志列表失败: {str(e)}"
        )


# ==================== 系统配置管理 ====================

@router.get("/config", summary="获取系统配置")
def get_system_config(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取系统配置接口
    
    返回所有系统配置，按分类分组。
    
    权限要求：
    - 所有登录用户查看公开配置
    - 超级管理员可查看所有配置
    
    Args:
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 查询失败时返回
    
    Examples:
        GET /v1/system/config
    """
    try:
        # 调用服务层获取所有配置
        result = config_service.get_all_configs(db)
        
        # 如果不是超级管理员，过滤私有配置
        if current_user.role != "super_admin":
            # 过滤掉私有配置（is_public=0）
            filtered_groups = []
            for group in result["configs"]:
                filtered_configs = [
                    config for config in group["configs"]
                    if config.is_public == 1
                ]
                if filtered_configs:
                    filtered_groups.append({
                        "category": group["category"],
                        "category_name": group["category_name"],
                        "configs": filtered_configs
                    })
            result["configs"] = filtered_groups
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "查询成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统配置失败: {str(e)}"
        )


@router.put("/config", summary="修改系统配置")
def update_system_config(
    update_data: ConfigBatchUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改系统配置接口
    
    支持批量修改系统配置。
    
    权限要求：
    - 仅超级管理员可修改
    
    Args:
        update_data (ConfigBatchUpdate): 批量更新数据
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 权限不足或更新失败时返回
    
    Examples:
        PUT /v1/system/config
        {
            "configs": [
                {"config_key": "system_name", "config_value": "新系统名称"},
                {"config_key": "min_stock_alert", "config_value": "5"}
            ]
        }
    """
    try:
        # 权限验证：仅超级管理员可修改配置
        if current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，仅超级管理员可修改系统配置"
            )
        
        # 调用服务层批量更新配置
        result = config_service.batch_update_configs(update_data, db)
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "配置更新成功",
            "data": {
                "updated_configs": result,
                "count": len(result)
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"修改系统配置失败: {str(e)}"
        )


@router.post("/config/initialize", summary="初始化系统配置")
def initialize_system_config(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    初始化系统配置接口
    
    创建预定义的系统配置项。
    
    权限要求：
    - 仅超级管理员可初始化
    
    Args:
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 权限不足或初始化失败时返回
    
    Examples:
        POST /v1/system/config/initialize
    """
    try:
        # 权限验证：仅超级管理员可初始化配置
        if current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，仅超级管理员可初始化系统配置"
            )
        
        # 调用服务层初始化配置
        result = config_service.initialize_configs(db)
        
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "系统配置初始化成功",
            "data": {
                "success": result
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"初始化系统配置失败: {str(e)}"
        )


# ==================== 数据备份恢复管理 ====================

@router.post("/backup", summary="创建数据库备份")
def create_backup(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    创建数据库备份接口
    
    生成数据库备份文件，文件格式为：campus_asset_backup_YYYYMMDD_HHMMSS.db
    备份文件存储在backend/backups/目录
    
    权限要求：
    - 仅超级管理员可执行
    
    Args:
        current_user (UserResponse): 当前登录用户（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 权限不足或备份失败时返回
    
    Examples:
        POST /v1/system/backup
    """
    try:
        # 权限验证：仅超级管理员可创建备份
        if current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，仅超级管理员可创建备份"
            )
        
        # 调用服务层创建备份
        result = backup_restore_service.create_backup()
        
        # 返回成功响应
        return {
            "code": 200,
            "message": "备份创建成功",
            "data": {
                "filename": result.filename,
                "create_time": result.create_time,
                "size": result.size,
                "size_human": result.size_human
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建备份失败: {str(e)}"
        )


@router.get("/backups", summary="获取备份文件列表")
def get_backup_list(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    获取备份文件列表接口
    
    返回所有备份文件信息，包括文件名、创建时间、文件大小
    按创建时间倒序排列
    
    权限要求：
    - 仅超级管理员可查看
    
    Args:
        current_user (UserResponse): 当前登录用户（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 权限不足或查询失败时返回
    
    Examples:
        GET /v1/system/backups
    """
    try:
        # 权限验证：仅超级管理员可查看备份列表
        if current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，仅超级管理员可查看备份列表"
            )
        
        # 调用服务层获取备份列表
        result = backup_restore_service.get_backup_list()
        
        # 返回成功响应
        return {
            "code": 200,
            "message": "查询成功",
            "data": {
                "backups": [
                    {
                        "filename": backup.filename,
                        "create_time": backup.create_time,
                        "size": backup.size,
                        "size_human": backup.size_human
                    }
                    for backup in result.backups
                ],
                "total": result.total
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取备份列表失败: {str(e)}"
        )


@router.get("/backup/{filename}", summary="下载备份文件")
def download_backup(
    filename: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    下载备份文件接口
    
    通过文件名下载对应的备份文件
    
    权限要求：
    - 仅超级管理员可下载
    
    Args:
        filename (str): 备份文件名
        current_user (UserResponse): 当前登录用户（自动注入）
    
    Returns:
        FileResponse: 备份文件
    
    Raises:
        HTTPException: 权限不足或文件不存在时返回
    
    Examples:
        GET /v1/system/backup/campus_asset_backup_20240114_143000.db
    """
    try:
        # 权限验证：仅超级管理员可下载备份
        if current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，仅超级管理员可下载备份"
            )
        
        # 调用服务层获取备份文件路径
        file_path = backup_restore_service.download_backup(filename)
        
        # 返回文件下载响应
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/x-sqlite3"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载备份文件失败: {str(e)}"
        )


@router.delete("/backup/{filename}", summary="删除备份文件")
def delete_backup(
    filename: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除备份文件接口
    
    通过文件名删除对应的备份文件
    
    权限要求：
    - 仅超级管理员可删除
    
    Args:
        filename (str): 备份文件名
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 权限不足或删除失败时返回
    
    Examples:
        DELETE /v1/system/backup/campus_asset_backup_20240114_143000.db
    """
    try:
        # 权限验证：仅超级管理员可删除备份
        if current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，仅超级管理员可删除备份"
            )
        
        # 调用服务层删除备份
        backup_restore_service.delete_backup(filename)
        
        # 返回成功响应
        return {
            "code": 200,
            "message": "删除成功",
            "data": {}
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除备份文件失败: {str(e)}"
        )


@router.post("/restore", summary="从备份文件恢复数据")
def restore_database(
    restore_data: RestoreRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    从备份文件恢复数据接口
    
    从指定的备份文件恢复数据库数据
    恢复前会自动创建当前数据库的备份
    
    权限要求：
    - 仅超级管理员可执行
    
    Args:
        restore_data (RestoreRequest): 恢复请求数据
        current_user (UserResponse): 当前登录用户（自动注入）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 统一格式的响应 {code, message, data}
    
    Raises:
        HTTPException: 权限不足或恢复失败时返回
    
    Examples:
        POST /v1/system/restore
        {
            "filename": "campus_asset_backup_20240114_143000.db",
            "password": "admin123"
        }
    """
    try:
        # 权限验证：仅超级管理员可恢复数据
        if current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，仅超级管理员可恢复数据"
            )
        
        # 获取当前用户的密码哈希
        from ...models.sys_user import User
        user = db.query(User).filter(
            User.username == current_user.username
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 调用服务层恢复数据
        result = backup_restore_service.restore_database(restore_data, user.password_hash)
        
        # 返回成功响应
        return {
            "code": 200,
            "message": "数据恢复成功",
            "data": {
                "success": result.success,
                "message": result.message,
                "restore_time": result.restore_time,
                "backup_filename": result.backup_filename,
                "pre_backup_filename": result.pre_backup_filename
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据恢复失败: {str(e)}"
        )