"""
CampusAssetManager/backend/app/schemas/goods.py
物品管理相关的Pydantic数据模型

功能说明：
- 定义物品分类CRUD操作的请求和响应数据结构
- 定义物品信息CRUD操作的请求和响应数据结构
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


# ==================== 物品分类相关模型 ====================

class CategoryBase(BaseModel):
    """
    物品分类基础模型
    
    包含分类的基本信息字段
    """
    category_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="分类名称",
        examples=["办公设备"]
    )
    category_code: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="分类编码",
        examples=["BG_SB"]
    )
    parent_id: Optional[int] = Field(
        default=None,
        description="父分类ID（顶级分类为None）",
        examples=[None]
    )
    description: Optional[str] = Field(
        default=None,
        description="分类描述",
        examples=["办公室使用的各类设备"]
    )
    sort_order: int = Field(
        default=0,
        ge=0,
        description="排序号",
        examples=[1]
    )
    is_active: int = Field(
        default=1,
        ge=0,
        le=1,
        description="是否启用（1启用/0禁用）",
        examples=[1]
    )


class CategoryCreate(CategoryBase):
    """
    物品分类创建请求模型
    
    用于创建新分类时的数据验证
    """
    pass


class CategoryUpdate(BaseModel):
    """
    物品分类更新请求模型
    
    用于更新分类信息时的数据验证
    """
    category_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="分类名称"
    )
    description: Optional[str] = Field(
        default=None,
        description="分类描述"
    )
    sort_order: Optional[int] = Field(
        default=None,
        ge=0,
        description="排序号"
    )
    is_active: Optional[int] = Field(
        default=None,
        ge=0,
        le=1,
        description="是否启用（1启用/0禁用）"
    )


class CategoryResponse(CategoryBase):
    """
    物品分类响应模型
    
    用于返回分类信息
    """
    category_id: int = Field(..., description="分类ID", examples=[1])
    level: int = Field(..., description="分类层级", examples=[1])
    create_time: datetime = Field(..., description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    
    class Config:
        """
        Pydantic配置
        
        启用ORM模式，支持直接从SQLAlchemy模型转换
        """
        from_attributes = True


class CategoryListResponse(BaseModel):
    """
    物品分类列表响应模型
    
    用于返回分类列表信息
    """
    items: List[CategoryResponse] = Field(..., description="分类列表")
    total: int = Field(..., description="总数量", examples=[100])


# ==================== 物品信息相关模型 ====================

class GoodsBase(BaseModel):
    """
    物品信息基础模型
    
    包含物品的基本信息字段
    """
    goods_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="物品名称",
        examples=["笔记本电脑"]
    )
    goods_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="物品编码",
        examples=["NB_001"]
    )
    category_id: int = Field(
        ...,
        description="分类ID",
        examples=[1]
    )
    specification: Optional[str] = Field(
        default=None,
        max_length=200,
        description="规格型号",
        examples=["ThinkPad X1 Carbon"]
    )
    unit: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="计量单位（个/台/箱等）",
        examples=["台"]
    )
    purchase_price: float = Field(
        ...,
        ge=0,
        description="采购单价",
        examples=[8000.00]
    )
    retail_price: Optional[float] = Field(
        default=None,
        ge=0,
        description="零售单价",
        examples=[10000.00]
    )
    description: Optional[str] = Field(
        default=None,
        description="物品描述",
        examples=["高性能商务笔记本"]
    )
    status: int = Field(
        default=1,
        ge=1,
        le=3,
        description="状态（1正常/2报废/3维修中）",
        examples=[1]
    )
    
    @validator('purchase_price', 'retail_price')
    def validate_price(cls, v):
        """
        验证价格格式
        
        Args:
            v: 价格数值
        
        Returns:
            验证后的价格
        
        Raises:
            ValueError: 价格格式不正确
        """
        if v is not None and v < 0:
            raise ValueError('价格不能为负数')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """
        验证状态是否合法
        
        Args:
            v: 状态数值
        
        Returns:
            验证后的状态
        
        Raises:
            ValueError: 状态不合法
        """
        if v not in [1, 2, 3]:
            raise ValueError('状态必须是 1（正常）、2（报废）或 3（维修中）')
        return v


class GoodsCreate(GoodsBase):
    """
    物品创建请求模型
    
    用于创建新物品时的数据验证
    """
    pass


class GoodsUpdate(BaseModel):
    """
    物品更新请求模型
    
    用于更新物品信息时的数据验证
    """
    goods_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="物品名称"
    )
    category_id: Optional[int] = Field(
        default=None,
        description="分类ID"
    )
    specification: Optional[str] = Field(
        default=None,
        max_length=200,
        description="规格型号"
    )
    unit: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=20,
        description="计量单位"
    )
    purchase_price: Optional[float] = Field(
        default=None,
        ge=0,
        description="采购单价"
    )
    retail_price: Optional[float] = Field(
        default=None,
        ge=0,
        description="零售单价"
    )
    description: Optional[str] = Field(
        default=None,
        description="物品描述"
    )
    status: Optional[int] = Field(
        default=None,
        ge=1,
        le=3,
        description="状态（1正常/2报废/3维修中）"
    )
    
    @validator('status')
    def validate_status(cls, v):
        """
        验证状态是否合法
        
        Args:
            v: 状态数值
        
        Returns:
            验证后的状态
        
        Raises:
            ValueError: 状态不合法
        """
        if v is not None and v not in [1, 2, 3]:
            raise ValueError('状态必须是 1（正常）、2（报废）或 3（维修中）')
        return v
    
    @validator('purchase_price', 'retail_price')
    def validate_price(cls, v):
        """
        验证价格格式
        
        Args:
            v: 价格数值
        
        Returns:
            验证后的价格
        
        Raises:
            ValueError: 价格格式不正确
        """
        if v is not None and v < 0:
            raise ValueError('价格不能为负数')
        return v


class GoodsResponse(GoodsBase):
    """
    物品信息响应模型
    
    用于返回物品信息
    """
    goods_id: int = Field(..., description="物品ID", examples=[1])
    create_time: datetime = Field(..., description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    
    # 包含分类信息（可选，用于查询时包含分类详情）
    category_name: Optional[str] = Field(
        default=None,
        description="分类名称",
        examples=["办公设备"]
    )
    
    class Config:
        """
        Pydantic配置
        
        启用ORM模式，支持直接从SQLAlchemy模型转换
        """
        from_attributes = True


class GoodsListResponse(BaseModel):
    """
    物品列表响应模型
    
    用于返回物品列表信息
    """
    items: List[GoodsResponse] = Field(..., description="物品列表")
    total: int = Field(..., description="总数量", examples=[100])
    page: int = Field(..., description="当前页码", examples=[1])
    page_size: int = Field(..., description="每页数量", examples=[20])


class GoodsQuery(BaseModel):
    """
    物品查询参数模型
    
    用于查询物品列表时的参数验证
    """
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(default=None, description="搜索关键词（物品名称、编码）")
    category_id: Optional[int] = Field(default=None, description="按分类筛选")
    status: Optional[int] = Field(default=None, ge=1, le=3, description="按状态筛选")


# ==================== 物品导入导出相关模型 ====================

class GoodsImportItem(BaseModel):
    """
    物品导入项模型
    
    用于Excel导入时的单个物品数据验证
    """
    goods_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="物品名称",
        examples=["笔记本电脑"]
    )
    goods_code: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="物品编码",
        examples=["NB_001"]
    )
    category_code: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="分类编码",
        examples=["BG_SB"]
    )
    specification: Optional[str] = Field(
        default=None,
        max_length=200,
        description="规格型号",
        examples=["ThinkPad X1 Carbon"]
    )
    unit: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="计量单位（个/台/箱等）",
        examples=["台"]
    )
    purchase_price: float = Field(
        ...,
        ge=0,
        description="采购单价",
        examples=[8000.00]
    )
    retail_price: Optional[float] = Field(
        default=None,
        ge=0,
        description="零售单价",
        examples=[10000.00]
    )
    description: Optional[str] = Field(
        default=None,
        description="物品描述",
        examples=["高性能商务笔记本"]
    )
    status: int = Field(
        default=1,
        ge=1,
        le=3,
        description="状态（1正常/2报废/3维修中）",
        examples=[1]
    )
    
    @validator('purchase_price', 'retail_price')
    def validate_price(cls, v):
        """
        验证价格格式
        
        Args:
            v: 价格数值
        
        Returns:
            验证后的价格
        
        Raises:
            ValueError: 价格格式不正确
        """
        if v is not None and v < 0:
            raise ValueError('价格不能为负数')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """
        验证状态是否合法
        
        Args:
            v: 状态数值
        
        Returns:
            验证后的状态
        
        Raises:
            ValueError: 状态不合法
        """
        if v not in [1, 2, 3]:
            raise ValueError('状态必须是 1（正常）、2（报废）或 3（维修中）')
        return v


class GoodsImportError(BaseModel):
    """
    物品导入错误信息模型
    
    用于记录导入失败的错误详情
    """
    row: int = Field(..., description="行号", examples=[1])
    goods_code: str = Field(..., description="物品编码", examples=["NB_001"])
    error_message: str = Field(..., description="错误信息", examples=["分类编码不存在"])


class GoodsImportResponse(BaseModel):
    """
    物品导入响应模型
    
    用于返回导入结果统计和错误详情
    """
    total_count: int = Field(..., description="总记录数", examples=[100])
    success_count: int = Field(..., description="成功导入数量", examples=[95])
    failed_count: int = Field(..., description="失败数量", examples=[5])
    errors: List[GoodsImportError] = Field(..., description="错误详情列表")


class GoodsExportQuery(BaseModel):
    """
    物品导出查询参数模型
    
    用于导出物品时的参数验证
    """
    search: Optional[str] = Field(default=None, description="搜索关键词（物品名称、编码）")
    category_id: Optional[int] = Field(default=None, description="按分类筛选")
    status: Optional[int] = Field(default=None, ge=1, le=3, description="按状态筛选")