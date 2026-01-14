# backend/app/core/security.py
from datetime import datetime, timedelta
from typing import Optional, Any
from uuid import UUID

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings
from app.core.exceptions import TokenExpiredError, TokenInvalidError


# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str | UUID,
    expires_delta: Optional[timedelta] = None,
    extra_data: Optional[dict] = None,
) -> str:
    """
    创建访问令牌。
    
    Args:
        subject: 主题（通常是用户ID）
        expires_delta: 过期时间增量
        extra_data: 额外数据
        
    Returns:
        JWT token字符串
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "access",
    }
    
    if extra_data:
        to_encode.update(extra_data)
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm="HS256"
    )


def create_refresh_token(
    subject: str | UUID,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    创建刷新令牌。
    
    Args:
        subject: 主题（通常是用户ID）
        expires_delta: 过期时间增量
        
    Returns:
        JWT token字符串
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
    }
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm="HS256"
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    解码令牌。
    
    Args:
        token: JWT token字符串
        
    Returns:
        解码后的payload
        
    Raises:
        TokenExpiredError: Token已过期
        TokenInvalidError: Token无效
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError:
        raise TokenInvalidError()


def verify_access_token(token: str) -> str:
    """
    验证访问令牌。
    
    Args:
        token: JWT token字符串
        
    Returns:
        用户ID
        
    Raises:
        TokenExpiredError: Token已过期
        TokenInvalidError: Token无效
    """
    payload = decode_token(token)
    
    if payload.get("type") != "access":
        raise TokenInvalidError("Invalid token type")
    
    user_id = payload.get("sub")
    if not user_id:
        raise TokenInvalidError("Invalid token payload")
    
    return user_id


def verify_refresh_token(token: str) -> str:
    """
    验证刷新令牌。
    
    Args:
        token: JWT token字符串
        
    Returns:
        用户ID
        
    Raises:
        TokenExpiredError: Token已过期
        TokenInvalidError: Token无效
    """
    payload = decode_token(token)
    
    if payload.get("type") != "refresh":
        raise TokenInvalidError("Invalid token type")
    
    user_id = payload.get("sub")
    if not user_id:
        raise TokenInvalidError("Invalid token payload")
    
    return user_id
