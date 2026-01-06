"""
CampusAssetManager/backend/app/models/sys_config.py
系统配置表ORM模型

功能说明：
- 定义系统配置数据结构
- 管理系统的各项配置参数

设计原则：
- 声明式：使用SQLAlchemy ORM声明式定义表结构
- 键值对：配置以config_key和config_value的形式存储

作者：CampusAssetManager开发团队
日期：2025-01-05
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..database.config import Base


class Config(Base):
    """
    系统配置表
    
    存储系统的各项配置参数。
    使用键值对（config_key和config_value）的方式存储配置信息。
    """
    __tablename__ = "sys_config"

    # 主键
    config_id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="配置ID"
    )

    # 配置键
    config_key = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="配置键"
    )

    # 配置值
    config_value = Column(
        Text,
        nullable=True,
        comment="配置值"
    )

    # 配置信息
    config_name = Column(
        String(100),
        nullable=False,
        comment="配置名称"
    )

    config_type = Column(
        String(20),
        nullable=False,
        comment="配置类型（string/number/boolean/json）"
    )

    category = Column(
        String(50),
        nullable=False,
        comment="配置分类（system/stock/notification等）"
    )

    description = Column(
        Text,
        nullable=True,
        comment="配置说明"
    )

    is_public = Column(
        Integer,
        default=0,
        comment="是否公开（1公开/0私有）"
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
        """返回配置对象的字符串表示"""
        return f"<Config(config_id={self.config_id}, config_key='{self.config_key}')>"