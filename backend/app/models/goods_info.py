"""
CampusAssetManager/backend/app/models/goods_info.py
物品信息表ORM模型

功能说明：
- 定义物品基本信息结构
- 管理物品的详细属性

设计原则：
- 声明式：使用SQLAlchemy ORM声明式定义表结构
- 外键关系：关联物品分类表

作者：CampusAssetManager开发团队
日期：2025-01-05
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database.config import Base


class Goods(Base):
    """
    物品信息表
    
    存储物品的基本信息、规格参数和状态信息。
    通过category_id关联到物品分类表。
    """
    __tablename__ = "goods_info"

    # 主键
    goods_id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="物品ID"
    )

    # 物品基本信息
    goods_name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="物品名称"
    )

    goods_code = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="物品编码"
    )

    # 关联分类
    category_id = Column(
        Integer,
        ForeignKey("goods_category.category_id"),
        nullable=False,
        index=True,
        comment="分类ID"
    )

    # 物品规格
    specification = Column(
        String(200),
        nullable=True,
        comment="规格型号"
    )

    unit = Column(
        String(20),
        nullable=False,
        comment="计量单位（个/台/箱等）"
    )

    # 价格信息
    purchase_price = Column(
        Float,
        nullable=False,
        comment="采购单价"
    )

    retail_price = Column(
        Float,
        nullable=True,
        comment="零售单价"
    )

    # 物品描述
    description = Column(
        Text,
        nullable=True,
        comment="物品描述"
    )

    # 状态信息
    status = Column(
        Integer,
        default=1,
        comment="状态（1正常/2报废/3维修中）"
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
        """返回物品对象的字符串表示"""
        return f"<Goods(goods_id={self.goods_id}, goods_name='{self.goods_name}', goods_code='{self.goods_code}')>"