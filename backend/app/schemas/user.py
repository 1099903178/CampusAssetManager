"""
CampusAssetManager/backend/app/schemas/user.py
用户管理相关的Pydantic数据模型

功能说明：
- 定义用户CRUD操作的请求和响应数据结构
- 提供数据验证功能
- 支持API文档自动生成

设计原则：
- 声明式：使用Pydantic BaseModel声明数据结构
- 类型安全：提供完整的类型提示
- 自动验证：Pydantic自动进行数据验证

作者：CampusAssetManager开发团队
日期：2026-01-06
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime


class UserBase(BaseModel):
    """
    用户基础模型
    
    包含用户的基本信息字段
    """
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="用户名",
        examples=["admin"]
    )
    real_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="真实姓名",
        examples=["张三"]
    )
    phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="联系电话",
        examples=["13800138000"]
    )
    email: Optional[str] = Field(
        default=None,
        max_length=100,
        description="电子邮箱",
        examples=["user@example.com"]
    )
    
    @validator('phone')
    def validate_phone(cls, v):
        """
        验证手机号格式
        
 Args:
            v: 手机号字符串
        
 Returns:
            验证后的手机号
        
 Raises:
            ValueError: 手机号格式不正确
        """
        if v is not None and not v.isdigit():
            raise ValueError('手机号必须为数字')
        return v


class UserCreate(UserBase):
    """
    用户创建请求模型
    
    用于创建新用户时的数据验证
    """
    password: str = Field(
        ...,
        min_length=6,
        max_length=20,
        description="密码",
        examples=["password123"]
    )
    role: str = Field(
        default="user",
        description="角色（user/admin/super_admin）",
        examples=["user"]
    )
    
    @validator('role')
    def validate_role(cls, v):
        """
        验证角色是否合法
        
 Args:
            v: 角色字符串
        
 Returns:
            验证后的角色
        
 Raises:
            ValueError: 角色不合法
        """
        if v not in ["user", "admin", "super_admin"]:
            raise ValueError('角色必须是 user、admin 或 super_admin')
        return v


class UserUpdate(BaseModel):
    """
    用户更新请求模型
    
    用于更新用户信息时的数据验证
    """
    real_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="真实姓名"
    )
    phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="联系电话"
    )
    email: Optional[str] = Field(
        default=None,
        max_length=100,
        description="电子邮箱"
    )
    role: Optional[str] = Field(
        default=None,
        description="角色（user/admin/super_admin）"
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="是否激活"
    )
    
    @validator('role')
    def validate_role(cls, v):
        """
        验证角色是否合法
        
 Args:
            v: 角色字符串
        
 Returns:
            验证后的角色
        
 Raises:
            ValueError: 角色不合法
        """
        if v is not None and v not in ["user", "admin", "super_admin"]:
            raise ValueError('角色必须是 user、admin 或 super_admin')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """
        验证手机号格式
        
 Args:
            v: 手机号字符串
        
 Returns:
            验证后的手机号
        
 Raises:
            ValueError: 手机号格式不正确
        """
        if v is not None and not v.isdigit():
            raise ValueError('手机号必须为数字')
        return v


class PasswordUpdate(BaseModel):
    """
    密码修改请求模型
    
    用于修改用户密码时的数据验证
    """
    old_password: str = Field(
        ...,
        min_length=6,
        max_length=20,
        description="旧密码"
    )
    new_password: str = Field(
        ...,
        min_length=6,
        max_length=20,
        description="新密码"
    )


class UserResponse(BaseModel):
    """
    用户响应模型
    
    用于返回用户信息
    """
    user_id: int = Field(..., description="用户ID", examples=[1])
    username: str = Field(..., description="用户名", examples=["admin"])
    real_name: str = Field(..., description="真实姓名", examples=["张三"])
    phone: Optional[str] = Field(default=None, description="联系电话", examples=["13800138000"])
    email: Optional[str] = Field(default=None, description="电子邮箱", examples=["user@example.com"])
    role: str = Field(..., description="角色（user/admin/super_admin）", examples=["user"])
    is_active: bool = Field(..., description="是否激活", examples=[True])
    create_time: datetime = Field(..., description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    
    class Config:
        """
        Pydantic配置
        
        启用ORM模式，支持直接从SQLAlchemy模型转换
        """
        from_attributes = True


class UserListResponse(BaseModel):
    """
    用户列表响应模型
    
    用于返回用户列表信息
    """
    items: List[UserResponse] = Field(..., description="用户列表")
    total: int = Field(..., description="总数量", examples=[100])
    page: int = Field(..., description="当前页码", examples=[1])
    page_size: int = Field(..., description="每页数量", examples=[20])


class UserQuery(BaseModel):
    """
    用户查询参数模型
    
    用于查询用户列表时的参数验证
    """
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(default=None, description="搜索关键词（用户名、真实姓名、手机号）")
    role: Optional[str] = Field(default=None, description="按角色筛选")
    is_active: Optional[bool] = Field(default=None, description="按激活状态筛选")