"""
CampusAssetManager/backend/app/models/sys_user.py
用户表ORM模型

功能说明：
- 定义系统用户数据结构
- 管理用户基本信息和认证信息

设计原则：
- 声明式：使用SQLAlchemy ORM声明式定义表结构
- 关系映射：定义与其他表的外键关系

作者：系统开发团队
日期：2025-01-05
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from ..database.config import Base


class User(Base):
    """
    用户表
    
    存储系统用户的基本信息、认证信息和角色权限。
    支持普通用户、管理员和超级管理员三种角色。
    """
    __tablename__ = "sys_user"

    # 主键
    user_id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="用户ID"
    )

    # 用户基本信息
    username = Column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment="用户名"
    )

    password_hash = Column(
        String(255),
        nullable=False,
        comment="密码哈希值（bcrypt加密）"
    )

    real_name = Column(
        String(50),
        nullable=False,
        comment="真实姓名"
    )

    phone = Column(
        String(20),
        nullable=True,
        comment="联系电话"
    )

    email = Column(
        String(100),
        nullable=True,
        comment="电子邮箱"
    )

    # 用户角色和状态
    role = Column(
        String(20),
        nullable=False,
        default="user",
        comment="角色（user/admin/super_admin）"
    )

    is_active = Column(
        Boolean,
        default=True,
        comment="是否激活"
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
        """返回用户对象的字符串表示"""
        return f"<User(user_id={self.user_id}, username='{self.username}', role='{self.role}')>"