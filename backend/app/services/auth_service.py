"""
CampusAssetManager/backend/app/services/auth_service.py
认证服务层

功能说明：
- 用户登录验证
- Token生成和管理
- 用户信息查询
- 认证相关业务逻辑

设计原则：
- 面向对象：使用AuthService类封装认证逻辑
- 声明式：使用Pydantic定义数据模型
- 封装清晰：提供简洁的公共方法
- 依赖注入：通过数据库会话进行数据访问

作者：CampusAssetManager开发团队
日期：2026-01-06
"""

from typing import Optional
from sqlalchemy.orm import Session

from ..models.sys_user import User
from ..schemas.token import UserLogin, UserInfo, TokenResponse
from ..core.security import verify_password, create_access_token


class AuthService:
    """
    认证服务类
    
    提供用户认证相关的业务逻辑，包括登录、Token生成等功能。
    """
    
    def get_user_by_username(self, username: str, db: Session) -> Optional[User]:
        """
        根据用户名获取用户信息
        
        Args:
            username (str): 用户名
            db (Session): 数据库会话
        
        Returns:
            Optional[User]: 用户对象，不存在则返回None
        
        Examples:
            >>> auth_service = AuthService()
            >>> user = auth_service.get_user_by_username("admin", db)
        """
        return db.query(User).filter(User.username == username).first()
    
    def authenticate_user(
        self,
        username: str,
        password: str,
        db: Session
    ) -> Optional[User]:
        """
        验证用户身份
        
        Args:
            username (str): 用户名
            password (str): 密码
            db (Session): 数据库会话
        
        Returns:
            Optional[User]: 用户对象，验证失败则返回None
        
        Examples:
            >>> user = auth_service.authenticate_user("admin", "admin123", db)
        """
        # 查询用户
        user = self.get_user_by_username(username, db)
        
        # 验证用户是否存在
        if not user:
            return None
        
        # 验证密码是否正确
        if not verify_password(password, user.password_hash):
            return None
        
        # 验证用户是否已激活
        if not user.is_active:
            return None
        
        return user
    
    def login(self, login_data: UserLogin, db: Session) -> TokenResponse:
        """
        用户登录
        
        Args:
            login_data (UserLogin): 登录数据
            db (Session): 数据库会话
        
        Returns:
            TokenResponse: 包含Token和用户信息的响应对象
        
        Raises:
            ValueError: 用户名或密码错误
            ValueError: 用户未激活
        
        Examples:
            >>> login_data = UserLogin(username="admin", password="admin123")
            >>> response = auth_service.login(login_data, db)
            >>> response.access_token
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        """
        # 验证用户身份
        user = self.authenticate_user(login_data.username, login_data.password, db)
        
        # 验证失败
        if not user:
            raise ValueError("用户名或密码错误")
        
        # 验证用户是否激活
        if not user.is_active:
            raise ValueError("用户已被禁用")
        
        # 生成访问令牌
        access_token = create_access_token(data={"sub": user.username})
        
        # 构建用户信息
        user_info = UserInfo(
            user_id=user.user_id,
            username=user.username,
            real_name=user.real_name,
            role=user.role,
            phone=user.phone,
            email=user.email,
            is_active=user.is_active
        )
        
        # 返回响应
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_info
        )
    
    def get_user_info(self, username: str, db: Session) -> UserInfo:
        """
        获取用户信息
        
        Args:
            username (str): 用户名
            db (Session): 数据库会话
        
        Returns:
            UserInfo: 用户信息对象
        
        Raises:
            ValueError: 用户不存在
        
        Examples:
            >>> user_info = auth_service.get_user_info("admin", db)
        """
        # 查询用户
        user = self.get_user_by_username(username, db)
        
        # 验证用户是否存在
        if not user:
            raise ValueError("用户不存在")
        
        # 构建用户信息
        user_info = UserInfo(
            user_id=user.user_id,
            username=user.username,
            real_name=user.real_name,
            role=user.role,
            phone=user.phone,
            email=user.email,
            is_active=user.is_active
        )
        
        return user_info