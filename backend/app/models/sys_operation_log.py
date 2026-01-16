"""
CampusAssetManager/backend/app/models/sys_operation_log.py
操作日志表ORM模型

功能说明：
- 定义系统操作日志数据结构
- 记录用户的所有操作行为

设计原则：
- 声明式：使用SQLAlchemy ORM声明式定义表结构
- 外键关系：关联用户表

作者：CampusAssetManager开发团队
日期：2025-01-05
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..database.config import Base


class OperationLog(Base):
    """
    操作日志表
    
    存储系统用户的操作日志记录。
    通过user_id关联到用户表，记录用户的所有操作行为。
    """
    __tablename__ = "sys_operation_log"

    # 主键
    log_id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="日志ID"
    )

    # 关联用户
    user_id = Column(
        Integer,
        ForeignKey("sys_user.user_id"),
        nullable=False,
        index=True,
        comment="操作人ID"
    )

    # 操作信息
    username = Column(
        String(50),
        nullable=False,
        comment="操作人用户名"
    )

    operation = Column(
        String(100),
        nullable=False,
        comment="操作类型（login/create/update/delete等）"
    )

    module = Column(
        String(50),
        nullable=False,
        comment="操作模块（user/goods/stock等）"
    )

    # 操作详情
    method = Column(
        String(10),
        nullable=False,
        comment="请求方法（GET/POST/PUT/DELETE）"
    )

    url = Column(
        String(200),
        nullable=True,
        comment="请求URL"
    )

    params = Column(
        Text,
        nullable=True,
        comment="请求参数"
    )

    result = Column(
        String(20),
        nullable=False,
        comment="操作结果（success/failed）"
    )

    error_message = Column(
        Text,
        nullable=True,
        comment="错误信息"
    )

    # 客户端信息
    ip_address = Column(
        String(50),
        nullable=True,
        comment="IP地址"
    )

    user_agent = Column(
        String(500),
        nullable=True,
        comment="用户代理"
    )

    # 时间戳
    create_time = Column(
        DateTime,
        server_default=func.now(),
        index=True,
        comment="操作时间"
    )

    def __repr__(self):
        """返回操作日志对象的字符串表示"""
        return f"<OperationLog(log_id={self.log_id}, username='{self.username}', operation='{self.operation}')>"