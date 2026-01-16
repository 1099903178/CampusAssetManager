"""
CampusAssetManager/backend/app/schemas/token.py
Token相关的Pydantic数据模型

功能说明：
- 定义Token请求和响应的数据结构
- 提供数据验证功能
- 支持API文档自动生成

设计原则：
- 声明式：使用Pydantic BaseModel声明数据结构
- 类型安全：提供完整的类型提示
- 自动验证：Pydantic自动进行数据验证

作者：CampusAssetManager开发团队
日期：2026-01-06
"""

from typing import Optional
from pydantic import BaseModel, Field


class Token(BaseModel):
    """
    Token响应模型
    
    用于返回登录成功后的Token信息
    """
    access_token: str = Field(..., description="访问令牌", examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])
    token_type: str = Field(default="bearer", description="令牌类型")


class TokenPayload(BaseModel):
    """
    Token载荷模型
    
    用于JWT Token的payload部分
    """
    sub: Optional[str] = Field(default=None, description="用户名")
    exp: Optional[str] = Field(default=None, description="过期时间")


class UserLogin(BaseModel):
    """
    用户登录请求模型
    
    用于接收用户登录时的用户名和密码
    """
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="用户名",
        examples=["admin"]
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=20,
        description="密码",
        examples=["admin123"]
    )


class UserInfo(BaseModel):
    """
    用户信息模型
    
    用于返回用户的基本信息
    """
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    real_name: str = Field(..., description="真实姓名")
    role: str = Field(..., description="角色（user/admin/super_admin）")
    phone: Optional[str] = Field(default=None, description="联系电话")
    email: Optional[str] = Field(default=None, description="电子邮箱")
    is_active: bool = Field(default=True, description="是否激活")


class TokenResponse(BaseModel):
    """
    Token完整响应模型
    
    包含Token和用户信息的完整响应
    """
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserInfo = Field(..., description="用户信息")