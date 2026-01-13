"""
CampusAssetManager/backend/app/schemas/stock.py
库存管理相关的Pydantic数据模型

功能说明：
- 定义入库操作的请求和响应数据结构
- 定义出库操作的请求和响应数据结构
- 提供数据验证功能
- 支持API文档自动生成

设计原则：
- 声明式：使用Pydantic BaseModel声明数据结构
- 类型安全：提供完整的类型提示
- 自动验证：Pydantic自动进行数据验证

作者：CampusAssetManager开发团队
日期：2026-01-07
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime


# ==================== 入库相关模型 ====================

class StockInBase(BaseModel):
    """
    入库基础模型
    
    包含入库的基本信息字段
    """
    goods_id: int = Field(
        ...,
        description="物品ID",
        examples=[1]
    )
    in_quantity: int = Field(
        ...,
        gt=0,
        description="入库数量",
        examples=[10]
    )
    unit_price: float = Field(
        ...,
        ge=0,
        description="入库单价",
        examples=[100.00]
    )
    total_amount: float = Field(
        ...,
        ge=0,
        description="入库总金额",
        examples=[1000.00]
    )
    batch_no: Optional[str] = Field(
        default=None,
        max_length=50,
        description="批次号",
        examples=["BATCH-001"]
    )
    supplier: Optional[str] = Field(
        default=None,
        max_length=100,
        description="供应商",
        examples=["供应商A"]
    )
    remark: Optional[str] = Field(
        default=None,
        description="备注",
        examples=["第一批入库"]
    )
    
    @validator('in_quantity')
    def validate_quantity(cls, v):
        """
        验证入库数量
        
        Args:
            v: 入库数量
        
        Returns:
            验证后的数量
        
        Raises:
            ValueError: 数量不合法
        """
        if v <= 0:
            raise ValueError('入库数量必须大于0')
        return v
    
    @validator('unit_price', 'total_amount')
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
        if v < 0:
            raise ValueError('价格不能为负数')
        return v


class StockInCreate(StockInBase):
    """
    入库创建请求模型
    
    用于创建入库记录时的数据验证
    """
    pass


class StockInResponse(StockInBase):
    """
    入库响应模型
    
    用于返回入库记录信息
    """
    in_id: int = Field(..., description="入库记录ID", examples=[1])
    in_no: str = Field(..., description="入库单号", examples=["IN-20240107-001"])
    operator_id: int = Field(..., description="操作人ID", examples=[1])
    in_time: datetime = Field(..., description="入库时间")
    
    # 物品相关字段
    goods_name: str = Field(..., description="物品名称", examples=["笔记本电脑"])
    goods_code: str = Field(..., description="物品编码", examples=["LAPTOP-001"])
    category_name: str = Field(..., description="分类名称", examples=["电子设备"])
    
    class Config:
        """
        Pydantic配置
        
        启用ORM模式，支持直接从SQLAlchemy模型转换
        """
        from_attributes = True


class StockInListResponse(BaseModel):
    """
    入库记录列表响应模型
    
    用于返回入库记录列表信息
    """
    items: List[StockInResponse] = Field(..., description="入库记录列表")
    total: int = Field(..., description="总数量", examples=[100])
    page: int = Field(..., description="当前页码", examples=[1])
    page_size: int = Field(..., description="每页数量", examples=[20])


class StockInQuery(BaseModel):
    """
    入库查询参数模型
    
    用于查询入库记录列表时的参数验证
    """
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(default=None, description="搜索关键词（入库单号、物品名称）")
    goods_id: Optional[int] = Field(default=None, description="按物品ID筛选")
    start_date: Optional[datetime] = Field(default=None, description="开始日期")
    end_date: Optional[datetime] = Field(default=None, description="结束日期")


# ==================== 出库相关模型 ====================

class StockOutBase(BaseModel):
    """
    出库基础模型
    
    包含出库的基本信息字段
    """
    goods_id: int = Field(
        ...,
        description="物品ID",
        examples=[1]
    )
    out_quantity: int = Field(
        ...,
        gt=0,
        description="出库数量",
        examples=[5]
    )
    unit_price: float = Field(
        ...,
        ge=0,
        description="出库单价",
        examples=[100.00]
    )
    total_amount: float = Field(
        ...,
        ge=0,
        description="出库总金额",
        examples=[500.00]
    )
    receiver: Optional[str] = Field(
        default=None,
        max_length=100,
        description="接收人",
        examples=["张三"]
    )
    department: Optional[str] = Field(
        default=None,
        max_length=100,
        description="接收部门",
        examples=["技术部"]
    )
    purpose: Optional[str] = Field(
        default=None,
        max_length=200,
        description="用途说明",
        examples=["办公使用"]
    )
    remark: Optional[str] = Field(
        default=None,
        description="备注",
        examples=["紧急出库"]
    )
    
    @validator('out_quantity')
    def validate_quantity(cls, v):
        """
        验证出库数量
        
        Args:
            v: 出库数量
        
        Returns:
            验证后的数量
        
        Raises:
            ValueError: 数量不合法
        """
        if v <= 0:
            raise ValueError('出库数量必须大于0')
        return v
    
    @validator('unit_price', 'total_amount')
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
        if v < 0:
            raise ValueError('价格不能为负数')
        return v


class StockOutCreate(StockOutBase):
    """
    出库创建请求模型
    
    用于创建出库记录时的数据验证
    """
    pass


class StockOutResponse(StockOutBase):
    """
    出库响应模型
    
    用于返回出库记录信息
    """
    out_id: int = Field(..., description="出库记录ID", examples=[1])
    out_no: str = Field(..., description="出库单号", examples=["OUT-20240107-001"])
    operator_id: int = Field(..., description="操作人ID", examples=[1])
    out_time: datetime = Field(..., description="出库时间")
    
    # 物品相关字段
    goods_name: str = Field(..., description="物品名称", examples=["笔记本电脑"])
    goods_code: str = Field(..., description="物品编码", examples=["LAPTOP-001"])
    category_name: str = Field(..., description="分类名称", examples=["电子设备"])
    
    class Config:
        """
        Pydantic配置
        
        启用ORM模式，支持直接从SQLAlchemy模型转换
        """
        from_attributes = True


class StockOutListResponse(BaseModel):
    """
    出库记录列表响应模型
    
    用于返回出库记录列表信息
    """
    items: List[StockOutResponse] = Field(..., description="出库记录列表")
    total: int = Field(..., description="总数量", examples=[100])
    page: int = Field(..., description="当前页码", examples=[1])
    page_size: int = Field(..., description="每页数量", examples=[20])


class StockOutQuery(BaseModel):
    """
    出库查询参数模型
    
    用于查询出库记录列表时的参数验证
    """
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(default=None, description="搜索关键词（出库单号、物品名称）")
    goods_id: Optional[int] = Field(default=None, description="按物品ID筛选")
    start_date: Optional[datetime] = Field(default=None, description="开始日期")
    end_date: Optional[datetime] = Field(default=None, description="结束日期")


# ==================== 库存相关模型 ====================

class StockResponse(BaseModel):
    """
    库存响应模型
    
    用于返回库存信息
    """
    stock_id: int = Field(..., description="库存ID", examples=[1])
    goods_id: int = Field(..., description="物品ID", examples=[1])
    goods_name: str = Field(..., description="物品名称", examples=["笔记本电脑"])
    goods_code: str = Field(..., description="物品编码", examples=["LAPTOP-001"])
    category_name: str = Field(..., description="分类名称", examples=["电子设备"])
    current_stock: int = Field(..., description="当前库存数量", examples=[50])
    total_value: float = Field(..., description="库存总金额", examples=[5000.00])
    min_stock: int = Field(..., description="最小库存阈值", examples=[10])
    max_stock: Optional[int] = Field(default=None, description="最大库存阈值", examples=[100])
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")
    
    # Goods相关字段
    purchase_price: float = Field(..., description="采购单价", examples=[100.00])
    retail_price: Optional[float] = Field(default=None, description="零售单价", examples=[150.00])
    status: int = Field(..., description="状态（1正常/2报废/3维修中）", examples=[1])
    
    class Config:
        """
        Pydantic配置
        
        启用ORM模式，支持直接从SQLAlchemy模型转换
        """
        from_attributes = True


class StockListResponse(BaseModel):
    """
    库存列表响应模型
    
    用于返回库存列表信息
    """
    items: List[StockResponse] = Field(..., description="库存列表")
    total: int = Field(..., description="总数量", examples=[100])
    page: int = Field(..., description="当前页码", examples=[1])
    page_size: int = Field(..., description="每页数量", examples=[20])


# ==================== 盘点相关模型 ====================

class StockCheckBase(BaseModel):
    """
    盘点基础模型
    
    包含盘点的基本信息字段
    """
    goods_id: int = Field(
        ...,
        description="物品ID",
        examples=[1]
    )
    actual_stock: int = Field(
        ...,
        ge=0,
        description="实际库存数量",
        examples=[100]
    )
    remark: Optional[str] = Field(
        default=None,
        description="备注说明",
        examples=["物品完好无损"]
    )
    
    @validator('actual_stock')
    def validate_quantity(cls, v):
        """
        验证实际库存数量
        
        Args:
            v: 实际库存数量
        
        Returns:
            验证后的数量
        
        Raises:
            ValueError: 数量不合法
        """
        if v < 0:
            raise ValueError('实际库存数量不能为负数')
        return v


class StockCheckCreate(StockCheckBase):
    """
    盘点创建请求模型
    
    用于创建盘点记录时的数据验证
    """
    pass


class StockCheckResponse(StockCheckBase):
    """
    盘点响应模型
    
    用于返回盘点记录信息
    """
    check_id: int = Field(..., description="盘点记录ID", examples=[1])
    check_no: str = Field(..., description="盘点单号", examples=["CHK-20240113-001"])
    checker_id: int = Field(..., description="盘点人ID", examples=[1])
    book_stock: int = Field(..., description="账面库存数量", examples=[100])
    diff_quantity: int = Field(..., description="差异数量（实际库存 - 账面库存）", examples=[0])
    check_result: str = Field(..., description="盘点结果（normal/over/short）", examples=["normal"])
    check_time: datetime = Field(..., description="盘点时间")
    
    # 物品相关字段
    goods_name: str = Field(..., description="物品名称", examples=["笔记本电脑"])
    goods_code: str = Field(..., description="物品编码", examples=["LAPTOP-001"])
    checker_name: str = Field(..., description="盘点人姓名", examples=["张三"])
    
    class Config:
        """
        Pydantic配置
        
        启用ORM模式，支持直接从SQLAlchemy模型转换
        """
        from_attributes = True


class StockCheckListResponse(BaseModel):
    """
    盘点记录列表响应模型
    
    用于返回盘点记录列表信息
    """
    items: List[StockCheckResponse] = Field(..., description="盘点记录列表")
    total: int = Field(..., description="总数量", examples=[100])
    page: int = Field(..., description="当前页码", examples=[1])
    page_size: int = Field(..., description="每页数量", examples=[20])


class StockCheckQuery(BaseModel):
    """
    盘点查询参数模型
    
    用于查询盘点记录列表时的参数验证
    """
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(default=None, description="搜索关键词（盘点单号、物品名称）")
    goods_id: Optional[int] = Field(default=None, description="按物品ID筛选")
    check_result: Optional[str] = Field(default=None, description="按盘点结果筛选（normal/over/short）")
    start_date: Optional[datetime] = Field(default=None, description="开始日期")
    end_date: Optional[datetime] = Field(default=None, description="结束日期")


# ==================== 库存调整相关模型 ====================

class StockAdjustBase(BaseModel):
    """
    库存调整基础模型
    
    包含库存调整的基本信息字段
    """
    goods_id: int = Field(
        ...,
        description="物品ID",
        examples=[1]
    )
    adjust_quantity: int = Field(
        ...,
        description="调整数量（正数为增加，负数为减少）",
        examples=[10]
    )
    adjust_reason: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="调整原因",
        examples=["盘亏调整"]
    )
    
    @validator('adjust_quantity')
    def validate_quantity(cls, v):
        """
        验证调整数量
        
        Args:
            v: 调整数量
        
        Returns:
            验证后的数量
        
        Raises:
            ValueError: 数量不合法
        """
        if v == 0:
            raise ValueError('调整数量不能为0')
        return v


class StockAdjustCreate(StockAdjustBase):
    """
    库存调整创建请求模型
    
    用于创建库存调整记录时的数据验证
    """
    pass


class StockAdjustResponse(BaseModel):
    """
    库存调整响应模型
    
    用于返回库存调整结果
    """
    stock_id: int = Field(..., description="库存ID", examples=[1])
    goods_id: int = Field(..., description="物品ID", examples=[1])
    goods_name: str = Field(..., description="物品名称", examples=["笔记本电脑"])
    goods_code: str = Field(..., description="物品编码", examples=["LAPTOP-001"])
    before_stock: int = Field(..., description="调整前库存", examples=[100])
    adjust_quantity: int = Field(..., description="调整数量", examples=[10])
    after_stock: int = Field(..., description="调整后库存", examples=[110])
    adjust_reason: str = Field(..., description="调整原因", examples=["盘亏调整"])
    adjust_time: datetime = Field(..., description="调整时间")
    
    class Config:
        """
        Pydantic配置
        
        启用ORM模式，支持直接从SQLAlchemy模型转换
        """
        from_attributes = True


# ==================== 台账查询相关模型 ====================

class StockLedgerResponse(BaseModel):
    """
    库存台账响应模型
    
    用于返回库存台账记录信息
    """
    record_id: int = Field(..., description="记录ID", examples=[1])
    operation_type: str = Field(..., description="操作类型（in/out/check/adjust）", examples=["in"])
    operation_no: str = Field(..., description="操作单号", examples=["IN-20240113-001"])
    goods_id: int = Field(..., description="物品ID", examples=[1])
    goods_name: str = Field(..., description="物品名称", examples=["笔记本电脑"])
    goods_code: str = Field(..., description="物品编码", examples=["LAPTOP-001"])
    category_name: str = Field(..., description="分类名称", examples=["电子设备"])
    quantity: int = Field(..., description="数量", examples=[10])
    stock_before: int = Field(..., description="操作前库存", examples=[100])
    stock_after: int = Field(..., description="操作后库存", examples=[110])
    operator_id: int = Field(..., description="操作人ID", examples=[1])
    operator_name: str = Field(..., description="操作人姓名", examples=["张三"])
    operation_time: datetime = Field(..., description="操作时间")
    remark: Optional[str] = Field(default=None, description="备注")
    
    class Config:
        """
        Pydantic配置
        
        启用ORM模式，支持直接从SQLAlchemy模型转换
        """
        from_attributes = True


class StockLedgerListResponse(BaseModel):
    """
    库存台账列表响应模型
    
    用于返回库存台账列表信息
    """
    items: List[StockLedgerResponse] = Field(..., description="库存台账列表")
    total: int = Field(..., description="总数量", examples=[100])
    page: int = Field(..., description="当前页码", examples=[1])
    page_size: int = Field(..., description="每页数量", examples=[20])


class StockLedgerQuery(BaseModel):
    """
    库存台账查询参数模型
    
    用于查询库存台账列表时的参数验证
    """
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(default=None, description="搜索关键词（操作单号、物品名称）")
    goods_id: Optional[int] = Field(default=None, description="按物品ID筛选")
    operation_type: Optional[str] = Field(default=None, description="按操作类型筛选（in/out/check/adjust）")
    start_date: Optional[datetime] = Field(default=None, description="开始日期")
    end_date: Optional[datetime] = Field(default=None, description="结束日期")


# ==================== 库存查询增强相关模型 ====================

class StockQueryEnriched(BaseModel):
    """
    库存查询增强参数模型
    
    用于查询库存列表时的增强参数验证
    """
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(default=None, description="搜索关键词（物品名称、编码）")
    category_id: Optional[int] = Field(default=None, description="按分类ID筛选")
    stock_status: Optional[str] = Field(default=None, description="按库存状态筛选（normal/low/over）")
    min_stock_only: bool = Field(default=False, description="只显示低于最小库存的物品")


class StockResponseEnhanced(StockResponse):
    """
    库存响应增强模型
    
    在原有库存响应模型基础上增加库存状态标识
    """
    stock_status: str = Field(..., description="库存状态（normal/low/over）", examples=["normal"])
    status_text: str = Field(..., description="状态文本（正常/低库存/库存过高）", examples=["正常"])


class StockListResponseEnhanced(BaseModel):
    """
    库存列表增强响应模型
    
    用于返回增强库存列表信息（包含库存状态）
    """
    items: List[StockResponseEnhanced] = Field(..., description="库存列表")
    total: int = Field(..., description="总数量", examples=[100])
    page: int = Field(..., description="当前页码", examples=[1])
    page_size: int = Field(..., description="每页数量", examples=[20])


# ==================== 库存阈值更新相关模型 ====================

class StockThresholdUpdate(BaseModel):
    """
    库存阈值更新模型
    
    用于更新单个物品的库存阈值
    """
    goods_id: int = Field(..., description="物品ID", examples=[1])
    min_stock: int = Field(..., ge=0, description="最小库存阈值", examples=[10])
    max_stock: Optional[int] = Field(default=None, ge=0, description="最大库存阈值", examples=[100])


class StockThresholdBatchUpdate(BaseModel):
    """
    库存阈值批量更新模型
    
    用于批量更新所有物品的库存阈值
    """
    min_stock: int = Field(..., ge=0, description="最小库存阈值", examples=[10])
    max_stock: Optional[int] = Field(default=None, ge=0, description="最大库存阈值", examples=[100])