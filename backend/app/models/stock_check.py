"""
CampusAssetManager/backend/app/models/stock_check.py
盘点记录表ORM模型

功能说明：
- 定义物品盘点记录数据结构
- 管理库存盘点操作的历史记录

设计原则：
- 声明式：使用SQLAlchemy ORM声明式定义表结构
- 外键关系：关联物品表和用户表

作者：CampusAssetManager开发团队
日期：2025-01-05
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from ..database.config import Base


class StockCheck(Base):
    """
    盘点记录表
    
    存储物品库存盘点的详细记录。
    通过goods_id关联到物品信息表，通过checker_id关联到用户表。
    """
    __tablename__ = "stock_check"

    # 主键
    check_id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="盘点记录ID"
    )

    # 盘点单号
    check_no = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="盘点单号"
    )

    # 关联物品和盘点人
    goods_id = Column(
        Integer,
        ForeignKey("goods_info.goods_id"),
        nullable=False,
        index=True,
        comment="物品ID"
    )

    checker_id = Column(
        Integer,
        ForeignKey("sys_user.user_id"),
        nullable=False,
        comment="盘点人ID"
    )

    # 盘点数量
    book_stock = Column(
        Integer,
        nullable=False,
        comment="账面库存数量"
    )

    actual_stock = Column(
        Integer,
        nullable=False,
        comment="实际库存数量"
    )

    diff_quantity = Column(
        Integer,
        nullable=False,
        comment="差异数量（实际库存 - 账面库存）"
    )

    # 盘点结果
    check_result = Column(
        String(20),
        nullable=False,
        comment="盘点结果（normal/over/short）"
    )

    # 盘点详情
    remark = Column(
        Text,
        nullable=True,
        comment="备注说明"
    )

    # 时间戳
    check_time = Column(
        DateTime,
        server_default=func.now(),
        comment="盘点时间"
    )

    def __repr__(self):
        """返回盘点记录对象的字符串表示"""
        return f"<StockCheck(check_id={self.check_id}, check_no='{self.check_no}', goods_id={self.goods_id})>"