"""
CampusAssetManager/backend/app/schemas/common.py
通用响应模型

功能说明：
- 定义统一的API响应格式
- 提供数据包装器

设计原则：
- 声明式：使用Pydantic声明式定义数据结构
- 类型安全：使用泛型支持不同数据类型

作者：CampusAssetManager开发团队
日期：2026-01-09
"""

from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

"""
定义数据类型变量，用于泛型
"""
T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """
    统一响应包装模型
    
    所有API响应都使用此格式：
    {
        "code": 200,
        "message": "成功",
        "data": {...}
    }
    
    Attributes:
        code (int): 响应状态码（200表示成功）
        message (str): 响应消息
        data (T): 响应数据
    """
    code: int = Field(
        ...,
        description="响应状态码",
        example=200
    )
    
    message: str = Field(
        ...,
        description="响应消息",
        example="成功"
    )
    
    data: T = Field(
        ...,
        description="响应数据"
    )
    
    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "成功",
                "data": {}
            }
        }