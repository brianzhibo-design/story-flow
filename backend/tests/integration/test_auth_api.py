"""
认证 API 集成测试
"""

import pytest
from httpx import AsyncClient


class TestAuthAPI:
    """认证 API 测试"""
    
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """测试注册成功"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "nickname": "New User"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """测试重复邮箱注册失败"""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,  # 已存在的邮箱
                "password": "SecurePass123!",
                "nickname": "Another User"
            }
        )
        
        assert response.status_code in [400, 409]
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user):
        """测试登录成功"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """测试密码错误登录失败"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "wrong_password"
            }
        )
        
        assert response.status_code in [400, 401]
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """测试不存在用户登录失败"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code in [400, 401, 404]
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, auth_headers):
        """测试获取当前用户信息"""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "email" in data["data"]
    
    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """测试未认证获取用户信息失败"""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient, test_user):
        """测试刷新 Token"""
        # 先登录获取 refresh_token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "password123"
            }
        )
        
        refresh_token = login_response.json()["data"]["refresh_token"]
        
        # 刷新 Token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]

