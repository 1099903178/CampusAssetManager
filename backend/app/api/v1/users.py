"""
CampusAssetManager/backend/app/api/v1/users.py
用户管理API端点

功能说明：
- 用户列表查询（支持分页、搜索）
- 创建新用户
- 获取用户详情
- 更新用户信息
- 删除用户（软删除）
- 修改用户密码

设计原则：
- 依赖注入：使用FastAPI的依赖注入系统
- 声明式：使用Pydantic定义请求和响应模型
- RESTful：遵循REST API设计规范
- 权限控制：仅超级管理员可访问

作者：CampusAssetManager开发团队
日期：2026-01-06
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database.config import get_db
from ...schemas.user import (
    UserCreate,
    UserUpdate,
    PasswordUpdate,
    UserQuery,
    UserResponse,
    UserListResponse
)
from ...services.user_service import UserService

# 创建路由器
router = APIRouter(prefix="/users", tags=["用户管理"])

# 创建用户服务实例
user_service = UserService()


@router.get("", response_model=UserListResponse, summary="查询用户列表")
def get_users(
    page: int = 1,
    page_size: int = 20,
    search: str = None,
    role: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """
    查询用户列表接口
    
    支持分页、搜索和多条件筛选。
    
    Args:
        page (int): 页码（默认1）
        page_size (int): 每页数量（默认20，最大100）
        search (str): 搜索关键词（用户名、真实姓名、手机号）
        role (str): 按角色筛选（user/admin/super_admin）
        is_active (bool): 按激活状态筛选
        db (Session): 数据库会话（自动注入）
    
    Returns:
        UserListResponse: 用户列表响应
    
    Raises:
        HTTPException: 查询失败时返回
    
    Examples:
        GET /v1/users/?page=1&page_size=20&search=admin
        
        GET /v1/users/?role=admin&is_active=true
    """
    try:
        # 构建查询参数
        query = UserQuery(
            page=page,
            page_size=page_size,
            search=search,
            role=role,
            is_active=is_active
        )
        
        # 调用服务层查询用户列表
        result = user_service.get_user_list(query, db)
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询用户列表失败: {str(e)}"
        )


@router.post("", response_model=UserResponse, summary="创建新用户")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    创建新用户接口
    
    Args:
        user_data (UserCreate): 用户创建数据
        db (Session): 数据库会话（自动注入）
    
    Returns:
        UserResponse: 创建的用户信息
    
    Raises:
        HTTPException: 创建失败时返回
    
    Examples:
        POST /v1/users/
        {
            "username": "newuser",
            "password": "password123",
            "real_name": "新用户",
            "phone": "13800138000",
            "email": "newuser@example.com",
            "role": "user"
        }
    """
    try:
        # 调用服务层创建用户
        user = user_service.create_user(user_data, db)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建用户失败: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserResponse, summary="获取用户详情")
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户详情接口
    
    Args:
        user_id (int): 用户ID
        db (Session): 数据库会话（自动注入）
    
    Returns:
        UserResponse: 用户信息
    
    Raises:
        HTTPException: 用户不存在时返回
    
    Examples:
        GET /v1/users/1
    """
    try:
        # 调用服务层获取用户详情
        user = user_service.get_user_by_id(user_id, db)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户详情失败: {str(e)}"
        )


@router.put("/{user_id}", response_model=UserResponse, summary="更新用户信息")
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    更新用户信息接口
    
    Args:
        user_id (int): 用户ID
        user_data (UserUpdate): 用户更新数据
        db (Session): 数据库会话（自动注入）
    
    Returns:
        UserResponse: 更新后的用户信息
    
    Raises:
        HTTPException: 用户不存在或更新失败时返回
    
    Examples:
        PUT /v1/users/1
        {
            "real_name": "新姓名",
            "phone": "13900139000",
            "email": "newemail@example.com",
            "role": "admin",
            "is_active": true
        }
    """
    try:
        # 调用服务层更新用户信息
        user = user_service.update_user(user_id, user_data, db)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户信息失败: {str(e)}"
        )


@router.delete("/{user_id}", summary="删除用户")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    删除用户接口（软删除）
    
    注意：此操作为软删除，仅将用户的 is_active 字段设置为 False
    
    Args:
        user_id (int): 用户ID
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 删除成功消息
    
    Raises:
        HTTPException: 用户不存在或删除失败时返回
    
    Examples:
        DELETE /v1/users/1
    """
    try:
        # 调用服务层删除用户（软删除）
        user_service.delete_user(user_id, db)
        
        return {
            "code": 200,
            "message": "删除成功",
            "data": None
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除用户失败: {str(e)}"
        )


@router.put("/{user_id}/password", summary="修改用户密码")
def update_password(
    user_id: int,
    password_data: PasswordUpdate,
    db: Session = Depends(get_db)
):
    """
    修改用户密码接口
    
    Args:
        user_id (int): 用户ID
        password_data (PasswordUpdate): 密码修改数据
        db (Session): 数据库会话（自动注入）
    
    Returns:
        dict: 修改成功消息
    
    Raises:
        HTTPException: 用户不存在、旧密码错误或修改失败时返回
    
    Examples:
        PUT /v1/users/1/password
        {
            "old_password": "oldpassword",
            "new_password": "newpassword"
        }
    """
    try:
        # 调用服务层修改密码
        user_service.update_password(user_id, password_data, db)
        
        return {
            "code": 200,
            "message": "密码修改成功",
            "data": None
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"修改密码失败: {str(e)}"
        )