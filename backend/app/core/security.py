"""
CampusAssetManager/backend/app/core/security.py
安全认证工具类

功能说明：
- 密码加密与验证（bcrypt）
- JWT Token生成与验证
- 认证相关辅助函数

设计原则：
- 声明式：通过配置类属性定义密钥
- 封装清晰：提供简洁的公共方法
- 安全优先：使用业界标准加密算法

作者：CampusAssetManager开发团队
日期：2026-01-06
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

# ==================== 密码加密配置 ====================

# 密码加密上下文
# 使用bcrypt算法，这是目前最安全的密码哈希算法之一
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password (str): 明文密码
        hashed_password (str): 加密后的密码哈希值
    
    Returns:
        bool: 验证结果（True 表示密码正确）
    
    Examples:
        >>> verify_password("admin123", "$2b$12$...")
        True
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    
    Args:
        password (str): 明文密码
    
    Returns:
        str: 加密后的密码哈希值
    
    Examples:
        >>> get_password_hash("admin123")
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYn9qXwCqKKa'
    """
    return pwd_context.hash(password)


# ==================== JWT Token配置 ====================

# JWT密钥配置
# 生产环境应该从环境变量中读取
SECRET_KEY = "campus-asset-manager-secret-key-2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24小时过期


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data (dict): 要编码到Token中的数据
        expires_delta (timedelta, optional): 令牌过期时间
    
    Returns:
        str: JWT访问令牌字符串
    
    Raises:
        ValueError: 数据编码失败
    
    Examples:
        >>> token = create_access_token({"sub": "admin"})
        >>> token
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    """
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 添加过期时间声明
    to_encode.update({"exp": expire})
    
    # 生成JWT Token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    解码JWT访问令牌
    
    Args:
        token (str): JWT访问令牌字符串
    
    Returns:
        dict: 解码后的数据字典
    
    Raises:
        HTTPException: Token无效或已过期
    
    Examples:
        >>> data = decode_access_token("eyJhbGciOiJIUzI1NiIs...")
        >>> data
        {'sub': 'admin', 'exp': 1735689600}
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token(token: str) -> bool:
    """
    验证Token是否有效
    
    Args:
        token (str): JWT访问令牌字符串
    
    Returns:
        bool: 验证结果
    
    Examples:
        >>> verify_token("eyJhbGciOiJIUzI1NiIs...")
        True
    """
    try:
        decode_access_token(token)
        return True
    except HTTPException:
        return False