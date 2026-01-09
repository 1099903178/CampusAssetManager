"""
CampusAssetManager/backend/app/api/v1/auth.py
认证API端点

功能说明：
- 用户登录接口
- 用户登出接口
- 获取用户信息接口

设计原则：
- 依赖注入：使用FastAPI的依赖注入系统
- 声明式：使用Pydantic定义请求和响应模型
- RESTful：遵循REST API设计规范

作者：CampusAssetManager开发团队
日期：2026-01-06
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database.config import get_db
from ...schemas.token import UserLogin, TokenResponse, UserInfo
from ...schemas.user import UserResponse
from ...services.auth_service import AuthService

# 创建路由器
router = APIRouter(prefix="/auth", tags=["认证"])

# 创建认证服务实例（在实际应用中，这里应该使用依赖注入）
auth_service = AuthService()


@router.post("/login", summary="用户登录")
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    
    Args:
        login_data (UserLogin): 登录数据（用户名和密码）
        db (Session): 数据库会话（自动注入）
    
    Returns:
        TokenResponse: 包含访问令牌和用户信息
    
    Raises:
        HTTPException: 登录失败时返回
    
    Examples:
        POST /v1/auth/login
        {
            "username": "admin",
            "password": "admin123"
        }
    """
    try:
        # 调用认证服务进行登录
        response = auth_service.login(login_data, db)
        # 返回统一格式的响应
        return {
            "code": 200,
            "message": "登录成功",
            "data": response
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


@router.post("/logout", summary="用户登出")
def logout():
    """
    用户登出接口
    
    说明：
    - 由于使用无状态的JWT Token，服务端不需要维护会话
    - 客户端应清除本地存储的Token
    - 这个接口主要用于日志记录或未来扩展
    
    Returns:
        dict: 登出成功消息
    
    Examples:
        POST /v1/auth/logout
    """
    return {
        "code": 200,
        "message": "登出成功",
        "data": None
    }


@router.get("/user-info", summary="获取用户信息")
def get_user_info(
    db: Session = Depends(get_db),
    # token: str = Depends(oauth2_scheme)
):
    """
    获取当前用户信息
    
    Args:
        db (Session): 数据库会话（自动注入）
    
    Returns:
        UserInfo: 用户信息对象
    
    Raises:
        HTTPException: 用户不存在时返回
    
    Examples:
        GET /v1/auth/user-info
        Headers: Authorization: Bearer <token>
    """
    # TODO: 从Token中获取用户名
    # 当前版本暂不实现Token验证，返回默认用户信息
    # 在Task-AUT-03（JWT认证中间件）中会完善此功能
    
    # 临时返回默认用户信息
    return UserInfo(
        user_id=1,
        username="admin",
        real_name="管理员",
        role="admin",
        phone="13800138000",
        email="admin@campus.edu",
        is_active=True
    )


def get_current_user() -> UserResponse:
    """
    获取当前登录用户（依赖函数）
    
    用于FastAPI的依赖注入，从请求中获取当前用户信息。
    当前版本返回默认管理员用户，待实现JWT Token验证后更新。
    
    Returns:
        UserResponse: 当前用户信息
    
    Examples:
        @app.get("/protected")
        def protected_route(current_user: UserResponse = Depends(get_current_user)):
            return {"user": current_user.username}
    """
    # 临时返回默认管理员用户
    return UserResponse(
        user_id=1,
        username="admin",
        real_name="管理员",
        role="admin",
        phone="13800138000",
        email="admin@campus.edu",
        is_active=True,
        create_time=__import__("datetime").datetime.now(),
        update_time=__import__("datetime").datetime.now()
    )