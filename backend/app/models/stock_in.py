"""
CampusAssetManager/backend/app/models/stock_in.py
入库记录表ORM模型

功能说明：
- 定义物品入库记录数据结构
- 管理入库操作的历史记录

设计原则：
- 声明式：使用SQLAlchemy ORM声明式定义表结构
- 外键关系：关联物品表和用户表

作者：CampusAssetManager开发团队
日期：2025-01-05
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from ..database.config import Base


class StockIn(Base):
    """
    入库记录表
    
    存储物品入库操作的详细记录。
    通过goods_id关联到物品信息表，通过operator_id关联到用户表。
    """
    __tablename__ = "stock_in"

    # 主键
    in_id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="入库记录ID"
    )

    # 入库单号
    in_no = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="入库单号"
    )

    # 关联物品和操作人
    goods_id = Column(
        Integer,
        ForeignKey("goods_info.goods_id"),
        nullable=False,
        index=True,
        comment="物品ID"
    )

    operator_id = Column(
        Integer,
        ForeignKey("sys_user.user_id"),
        nullable=False,
        comment="操作人ID"
    )

    # 入库信息
    in_quantity = Column(
        Integer,
        nullable=False,
        comment="入库数量"
    )

    unit_price = Column(
        Float,
        nullable=False,
        comment="入库单价"
    )

    total_amount = Column(
        Float,
        nullable=False,
        comment="入库总金额"
    )

    # 入库详情
    batch_no = Column(
        String(50),
        nullable=True,
        comment="批次号"
    )

    supplier = Column(
        String(100),
        nullable=True,
        comment="供应商"
    )

    remark = Column(
        Text,
        nullable=True,
        comment="备注"
    )

    # 时间戳
    in_time = Column(
        DateTime,
        server_default=func.now(),
        comment="入库时间"
    )

    def __repr__(self):
        """返回入库记录对象的字符串表示"""
        return f"<StockIn(in_id={self.in_id}, in_no='{self.in_no}', goods_id={self.goods_id})>"