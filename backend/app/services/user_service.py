"""
CampusAssetManager/backend/app/services/user_service.py
用户管理服务类

功能说明：
- 用户列表查询（支持分页、搜索）
- 创建新用户
- 获取用户详情
- 更新用户信息
- 删除用户（软删除）
- 修改密码

设计原则：
- 面向对象：使用 UserService 类封装用户管理逻辑
- 声明式：使用 Pydantic 定义数据模型
- 封装清晰：提供简洁的公共方法

作者：CampusAssetManager开发团队
日期：2026-01-06
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..models.sys_user import User
from ..schemas.user import (
    UserCreate,
    UserUpdate,
    PasswordUpdate,
    UserQuery,
    UserResponse,
    UserListResponse
)
from ..core.security import get_password_hash, verify_password


class UserService:
    """
    用户管理服务类
    
    负责处理用户相关的所有业务逻辑
    """
    
    def get_user_list(
        self,
        query: UserQuery,
        db: Session
    ) -> UserListResponse:
        """
        查询用户列表
        
        Args:
            query (UserQuery): 查询参数（分页、搜索、筛选）
            db (Session): 数据库会话
        
        Returns:
            UserListResponse: 用户列表响应
        
        Examples:
            >>> service = UserService()
            >>> query = UserQuery(page=1, page_size=20)
            >>> result = service.get_user_list(query, db)
        """
        # 构建基础查询
        db_query = db.query(User)
        
        # 搜索过滤
        if query.search:
            search_pattern = f"%{query.search}%"
            db_query = db_query.filter(
                or_(
                    User.username.like(search_pattern),
                    User.real_name.like(search_pattern),
                    User.phone.like(search_pattern)
                )
            )
        
        # 角色过滤
        if query.role:
            db_query = db_query.filter(User.role == query.role)
        
        # 激活状态过滤
        if query.is_active is not None:
            db_query = db_query.filter(User.is_active == query.is_active)
        
        # 计算总数
        total = db_query.count()
        
        # 分页
        offset = (query.page - 1) * query.page_size
        users = db_query.offset(offset).limit(query.page_size).all()
        
        # 转换为响应模型
        items = [UserResponse.model_validate(user) for user in users]
        
        return UserListResponse(
            items=items,
            total=total,
            page=query.page,
            page_size=query.page_size
        )
    
    def create_user(
        self,
        user_data: UserCreate,
        db: Session
    ) -> UserResponse:
        """
        创建新用户
        
        Args:
            user_data (UserCreate): 用户创建数据
            db (Session): 数据库会话
        
        Returns:
            UserResponse: 创建的用户信息
        
        Raises:
            ValueError: 用户名已存在
            Exception: 创建失败
        
        Examples:
            >>> service = UserService()
            >>> user_data = UserCreate(
            ...     username="testuser",
            ...     password="password123",
            ...     real_name="测试用户",
            ...     role="user"
            ... )
            >>> user = service.create_user(user_data, db)
        """
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(
            User.username == user_data.username
        ).first()
        
        if existing_user:
            raise ValueError("用户名已存在")
        
        # 加密密码
        password_hash = get_password_hash(user_data.password)
        
        # 创建用户对象
        new_user = User(
            username=user_data.username,
            password_hash=password_hash,
            real_name=user_data.real_name,
            phone=user_data.phone,
            email=user_data.email,
            role=user_data.role,
            is_active=True
        )
        
        # 保存到数据库
        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return UserResponse.model_validate(new_user)
        except Exception as e:
            db.rollback()
            raise Exception(f"创建用户失败: {str(e)}")
    
    def get_user_by_id(
        self,
        user_id: int,
        db: Session
    ) -> UserResponse:
        """
        根据ID获取用户详情
        
        Args:
            user_id (int): 用户ID
            db (Session): 数据库会话
        
        Returns:
            UserResponse: 用户信息
        
        Raises:
            ValueError: 用户不存在
        
        Examples:
            >>> service = UserService()
            >>> user = service.get_user_by_id(1, db)
        """
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise ValueError("用户不存在")
        
        return UserResponse.model_validate(user)
    
    def update_user(
        self,
        user_id: int,
        user_data: UserUpdate,
        db: Session
    ) -> UserResponse:
        """
        更新用户信息
        
        Args:
            user_id (int): 用户ID
            user_data (UserUpdate): 用户更新数据
            db (Session): 数据库会话
        
        Returns:
            UserResponse: 更新后的用户信息
        
        Raises:
            ValueError: 用户不存在
        
        Examples:
            >>> service = UserService()
            >>> user_data = UserUpdate(real_name="新姓名", phone="13900139000")
            >>> user = service.update_user(1, user_data, db)
        """
        # 查询用户
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise ValueError("用户不存在")
        
        # 更新字段
        update_dict = user_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        # 保存到数据库
        try:
            db.commit()
            db.refresh(user)
            return UserResponse.model_validate(user)
        except Exception as e:
            db.rollback()
            raise Exception(f"更新用户失败: {str(e)}")
    
    def delete_user(
        self,
        user_id: int,
        db: Session
    ) -> None:
        """
        删除用户（软删除）
        
        Args:
            user_id (int): 用户ID
            db (Session): 数据库会话
        
        Raises:
            ValueError: 用户不存在
            Exception: 删除失败
        
        Examples:
            >>> service = UserService()
            >>> service.delete_user(1, db)
        """
        # 查询用户
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise ValueError("用户不存在")
        
        # 软删除：设置 is_active 为 False
        user.is_active = False
        
        # 保存到数据库
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"删除用户失败: {str(e)}")
    
    def update_password(
        self,
        user_id: int,
        password_data: PasswordUpdate,
        db: Session
    ) -> None:
        """
        修改用户密码
        
        Args:
            user_id (int): 用户ID
            password_data (PasswordUpdate): 密码修改数据
            db (Session): 数据库会话
        
        Raises:
            ValueError: 用户不存在或旧密码错误
            Exception: 修改失败
        
        Examples:
            >>> service = UserService()
            >>> password_data = PasswordUpdate(
            ...     old_password="old123",
            ...     new_password="new123"
            ... )
            >>> service.update_password(1, password_data, db)
        """
        # 查询用户
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise ValueError("用户不存在")
        
        # 验证旧密码
        if not verify_password(password_data.old_password, user.password_hash):
            raise ValueError("旧密码错误")
        
        # 更新密码
        user.password_hash = get_password_hash(password_data.new_password)
        
        # 保存到数据库
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"修改密码失败: {str(e)}")