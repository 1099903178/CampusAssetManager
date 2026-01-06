"""
CampusAssetManager/backend/app/models/stock_out.py
出库记录表ORM模型

功能说明：
- 定义物品出库记录数据结构
- 管理出库操作的历史记录

设计原则：
- 声明式：使用SQLAlchemy ORM声明式定义表结构
- 外键关系：关联物品表和用户表

作者：CampusAssetManager开发团队
日期：2025-01-05
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from ..database.config import Base


class StockOut(Base):
    """
    出库记录表
    
    存储物品出库操作的详细记录。
    通过goods_id关联到物品信息表，通过operator_id关联到用户表。
    """
    __tablename__ = "stock_out"

    # 主键
    out_id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="出库记录ID"
    )

    # 出库单号
    out_no = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="出库单号"
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

    # 出库信息
    out_quantity = Column(
        Integer,
        nullable=False,
        comment="出库数量"
    )

    unit_price = Column(
        Float,
        nullable=False,
        comment="出库单价"
    )

    total_amount = Column(
        Float,
        nullable=False,
        comment="出库总金额"
    )

    # 出库详情
    receiver = Column(
        String(100),
        nullable=True,
        comment="接收人"
    )

    department = Column(
        String(100),
        nullable=True,
        comment="接收部门"
    )

    purpose = Column(
        String(200),
        nullable=True,
        comment="用途说明"
    )

    remark = Column(
        Text,
        nullable=True,
        comment="备注"
    )

    # 时间戳
    out_time = Column(
        DateTime,
        server_default=func.now(),
        comment="出库时间"
    )

    def __repr__(self):
        """返回出库记录对象的字符串表示"""
        return f"<StockOut(out_id={self.out_id}, out_no='{self.out_no}', goods_id={self.goods_id})>"