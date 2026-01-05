"""
CampusAssetManager/backend/app/models/goods_category.py
物品分类表ORM模型

功能说明：
- 定义物品分类数据结构
- 管理物品分类信息

设计原则：
- 声明式：使用SQLAlchemy ORM声明式定义表结构
- 层级关系：支持分类层级结构

作者：系统开发团队
日期：2025-01-05
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from ..database.config import Base


class GoodsCategory(Base):
    """
    物品分类表
    
    存储物品分类的层级结构信息。
    支持多级分类，通过parent_id实现父子关系。
    """
    __tablename__ = "goods_category"

    # 主键
    category_id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="分类ID"
    )

    # 分类基本信息
    category_name = Column(
        String(50),
        nullable=False,
        index=True,
        comment="分类名称"
    )

    category_code = Column(
        String(20),
        unique=True,
        nullable=False,
        comment="分类编码"
    )

    # 分类层级关系
    parent_id = Column(
        Integer,
        nullable=True,
        comment="父分类ID（顶级分类为NULL）"
    )

    level = Column(
        Integer,
        nullable=False,
        default=1,
        comment="分类层级（1/2/3...）"
    )

    # 分类描述
    description = Column(
        Text,
        nullable=True,
        comment="分类描述"
    )

    # 排序和状态
    sort_order = Column(
        Integer,
        default=0,
        comment="排序号"
    )

    is_active = Column(
        Integer,
        default=1,
        comment="是否启用（1启用/0禁用）"
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
        """返回分类对象的字符串表示"""
        return f"<GoodsCategory(category_id={self.category_id}, category_name='{self.category_name}')>"