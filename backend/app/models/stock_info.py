"""
CampusAssetManager/backend/app/models/stock_info.py
库存表ORM模型

功能说明：
- 定义物品库存数据结构
- 管理物品的当前库存量

设计原则：
- 声明式：使用SQLAlchemy ORM声明式定义表结构
- 外键关系：关联物品信息表

作者：CampusAssetManager开发团队
日期：2025-01-05
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database.config import Base


class Stock(Base):
    """
    库存表
    
    存储物品的实时库存信息。
    通过goods_id关联到物品信息表，每个物品有且仅有一条库存记录。
    """
    __tablename__ = "stock_info"

    # 主键
    stock_id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="库存ID"
    )

    # 关联物品
    goods_id = Column(
        Integer,
        ForeignKey("goods_info.goods_id"),
        unique=True,
        nullable=False,
        index=True,
        comment="物品ID"
    )

    # 库存数量
    current_stock = Column(
        Integer,
        nullable=False,
        default=0,
        comment="当前库存数量"
    )

    # 库存金额
    total_value = Column(
        Float,
        nullable=False,
        default=0.0,
        comment="库存总金额（采购单价 × 当前库存）"
    )

    # 阈值设置
    min_stock = Column(
        Integer,
        nullable=False,
        default=0,
        comment="最小库存阈值（低于此值预警）"
    )

    max_stock = Column(
        Integer,
        nullable=True,
        comment="最大库存阈值（高于此值预警）"
    )

    # 时间戳
    create_time = Column(
        DateTime,
        server_default=func.now(),
        comment="创建时间"
    )

    update_time = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    def __repr__(self):
        """返回库存对象的字符串表示"""
        return f"<Stock(stock_id={self.stock_id}, goods_id={self.goods_id}, current_stock={self.current_stock})>"