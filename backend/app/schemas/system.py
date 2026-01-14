"""
CampusAssetManager/backend/app/schemas/system.py
系统管理相关的Pydantic数据模型

功能说明：
- 定义操作日志的请求和响应数据结构
- 定义系统配置的请求和响应数据结构
- 提供数据验证功能
- 支持API文档自动生成

设计原则：
- 声明式：使用Pydantic BaseModel声明数据结构
- 类型安全：提供完整的类型提示
- 自动验证：Pydantic自动进行数据验证

作者：CampusAssetManager开发团队
日期：2026-01-10
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


# ==================== 操作日志相关模型 ====================

class OperationLogResponse(BaseModel):
    """
    操作日志响应模型
    
    用于返回操作日志记录信息
    """
    log_id: int = Field(..., description="日志ID", examples=[1])
    user_id: int = Field(..., description="操作人ID", examples=[1])
    username: str = Field(..., description="操作人用户名", examples=["admin"])
    operation: str = Field(..., description="操作类型", examples=["login"])
    module: str = Field(..., description="操作模块", examples=["auth"])
    method: str = Field(..., description="请求方法", examples=["POST"])
    url: Optional[str] = Field(default=None, description="请求URL", examples=["/v1/auth/login"])
    params: Optional[str] = Field(default=None, description="请求参数")
    result: str = Field(..., description="操作结果", examples=["success"])
    error_message: Optional[str] = Field(default=None, description="错误信息")
    ip_address: Optional[str] = Field(default=None, description="IP地址", examples=["127.0.0.1"])
    user_agent: Optional[str] = Field(default=None, description="用户代理")
    create_time: datetime = Field(..., description="操作时间")
    
    class Config:
        """
        Pydantic配置
        
        启用ORM模式，支持直接从SQLAlchemy模型转换
        """
        from_attributes = True


class OperationLogListResponse(BaseModel):
    """
    操作日志列表响应模型
    
    用于返回操作日志列表信息
    """
    items: List[OperationLogResponse] = Field(..., description="操作日志列表")
    total: int = Field(..., description="总数量", examples=[100])
    page: int = Field(..., description="当前页码", examples=[1])
    page_size: int = Field(..., description="每页数量", examples=[20])


class OperationLogQuery(BaseModel):
    """
    操作日志查询参数模型
    
    用于查询操作日志列表时的参数验证
    """
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    username: Optional[str] = Field(default=None, description="按用户名筛选")
    operation: Optional[str] = Field(default=None, description="按操作类型筛选")
    module: Optional[str] = Field(default=None, description="按模块筛选")
    start_date: Optional[datetime] = Field(default=None, description="开始日期")
    end_date: Optional[datetime] = Field(default=None, description="结束日期")
    result: Optional[str] = Field(default=None, description="按结果筛选")


# ==================== 系统配置相关模型 ====================

class ConfigBase(BaseModel):
    """
    系统配置基础模型
    
    包含系统配置的基本信息字段
    """
    config_key: str = Field(
        ...,
        max_length=100,
        description="配置键",
        examples=["system_name"]
    )
    config_name: str = Field(
        ...,
        max_length=100,
        description="配置名称",
        examples=["系统名称"]
    )
    config_value: str = Field(
        ...,
        description="配置值",
        examples=["校物通校园物品管理系统"]
    )
    config_type: str = Field(
        ...,
        max_length=20,
        description="配置类型",
        examples=["string"]
    )
    category: str = Field(
        ...,
        max_length=50,
        description="配置分类",
        examples=["system"]
    )
    description: Optional[str] = Field(default=None, description="配置说明")
    is_public: int = Field(default=0, description="是否公开（1公开/0私有）")
    
    @validator('config_type')
    def validate_config_type(cls, v):
        """
        验证配置类型
        
        Args:
            v: 配置类型
        
        Returns:
            验证后的配置类型
        
        Raises:
            ValueError: 配置类型不合法
        """
        valid_types = ['string', 'number', 'boolean', 'json']
        if v not in valid_types:
            raise ValueError(f'配置类型必须是以下之一: {", ".join(valid_types)}')
        return v
    
    @validator('is_public')
    def validate_is_public(cls, v):
        """
        验证是否公开标识
        
        Args:
            v: 是否公开标识
        
        Returns:
            验证后的标识
        
        Raises:
            ValueError: 标识不合法
        """
        if v not in [0, 1]:
            raise ValueError('is_public必须为0或1')
        return v


class ConfigResponse(ConfigBase):
    """
    系统配置响应模型
    
    用于返回系统配置信息
    """
    config_id: int = Field(..., description="配置ID", examples=[1])
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")
    
    class Config:
        """
        Pydantic配置
        
        启用ORM模式，支持直接从SQLAlchemy模型转换
        """
        from_attributes = True


class ConfigUpdate(BaseModel):
    """
    系统配置更新请求模型
    
    用于更新系统配置时的数据验证
    """
    config_key: str = Field(..., description="配置键")
    config_value: str = Field(..., description="配置值")


class ConfigBatchUpdate(BaseModel):
    """
    系统配置批量更新请求模型
    
    用于批量更新系统配置
    """
    configs: List[ConfigUpdate] = Field(..., description="配置列表")


class SystemConfigGroup(BaseModel):
    """
    系统配置分组响应模型
    
    用于按分类返回配置
    """
    category: str = Field(..., description="配置分类", examples=["system"])
    category_name: str = Field(..., description="分类名称", examples=["系统配置"])
    configs: List[ConfigResponse] = Field(..., description="配置列表")


class SystemConfigResponse(BaseModel):
    """
    系统配置完整响应模型
    
    用于返回所有系统配置，按分类分组
    """
    configs: List[SystemConfigGroup] = Field(..., description="配置分组列表")


class SystemResetRequest(BaseModel):
    """
    系统重置请求模型
    
    用于系统重置时的数据验证
    """
    password: str = Field(..., min_length=1, description="管理员密码")


# ==================== 预定义系统配置项 ====================

PREDEFINED_CONFIGS = [
    {
        "config_key": "system_name",
        "config_name": "系统名称",
        "config_value": "校物通校园物品管理系统",
        "config_type": "string",
        "category": "system",
        "description": "系统显示名称",
        "is_public": 1
    },
    {
        "config_key": "check_period",
        "config_name": "盘点周期",
        "config_value": "monthly",
        "config_type": "string",
        "category": "stock",
        "description": "定期盘点周期（daily/weekly/monthly）",
        "is_public": 1
    },
    {
        "config_key": "backup_enabled",
        "config_name": "启用数据备份",
        "config_value": "true",
        "config_type": "boolean",
        "category": "backup",
        "description": "是否启用自动数据备份",
        "is_public": 0
    },
    {
        "config_key": "backup_period",
        "config_name": "备份周期",
        "config_value": "daily",
        "config_type": "string",
        "category": "backup",
        "description": "自动备份周期（daily/weekly）",
        "is_public": 0
    },
]