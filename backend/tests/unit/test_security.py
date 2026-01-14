"""
安全模块单元测试
"""

import pytest
from datetime import timedelta

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
)
from app.core.exceptions import TokenExpiredError, TokenInvalidError


class TestPasswordHashing:
    """密码哈希测试"""
    
    def test_hash_password(self):
        """测试密码哈希"""
        password = "my_secure_password"
        hashed = hash_password(password)
        
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt 格式
    
    def test_verify_password_correct(self):
        """测试正确密码验证"""
        password = "my_secure_password"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """测试错误密码验证"""
        password = "my_secure_password"
        hashed = hash_password(password)
        
        assert verify_password("wrong_password", hashed) is False
    
    def test_different_passwords_different_hashes(self):
        """测试不同密码生成不同哈希"""
        hash1 = hash_password("password1")
        hash2 = hash_password("password2")
        
        assert hash1 != hash2
    
    def test_same_password_different_hashes(self):
        """测试相同密码生成不同哈希（因为 salt）"""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """JWT Token 测试"""
    
    def test_create_access_token(self):
        """测试创建访问 Token"""
        user_id = "test-user-id"
        token = create_access_token(subject=user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self):
        """测试创建刷新 Token"""
        user_id = "test-user-id"
        token = create_refresh_token(subject=user_id)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_verify_access_token(self):
        """测试验证访问 Token"""
        user_id = "test-user-id"
        token = create_access_token(subject=user_id)
        
        payload = verify_access_token(token)
        
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
    
    def test_verify_refresh_token(self):
        """测试验证刷新 Token"""
        user_id = "test-user-id"
        token = create_refresh_token(subject=user_id)
        
        payload = verify_refresh_token(token)
        
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
    
    def test_access_token_with_extra_data(self):
        """测试带额外数据的 Token"""
        user_id = "test-user-id"
        extra = {"role": "admin", "email": "test@example.com"}
        token = create_access_token(subject=user_id, extra_data=extra)
        
        payload = verify_access_token(token)
        
        assert payload["sub"] == user_id
        assert payload["role"] == "admin"
        assert payload["email"] == "test@example.com"
    
    def test_invalid_token(self):
        """测试无效 Token"""
        with pytest.raises(TokenInvalidError):
            verify_access_token("invalid.token.here")
    
    def test_expired_token(self):
        """测试过期 Token"""
        user_id = "test-user-id"
        # 创建一个已过期的 token
        token = create_access_token(
            subject=user_id,
            expires_delta=timedelta(seconds=-1)  # 已过期
        )
        
        with pytest.raises(TokenExpiredError):
            verify_access_token(token)
    
    def test_wrong_token_type(self):
        """测试错误的 Token 类型"""
        user_id = "test-user-id"
        access_token = create_access_token(subject=user_id)
        
        # 用访问 Token 验证刷新 Token 应该失败
        with pytest.raises(TokenInvalidError):
            verify_refresh_token(access_token)

