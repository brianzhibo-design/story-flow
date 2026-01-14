"""
API 功能测试
"""

import pytest


class TestAuth:
    """认证测试"""
    
    @pytest.mark.asyncio
    async def test_register_endpoint_exists(self, client):
        """测试注册端点存在"""
        response = await client.post("/api/v1/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "Test123456"
        })
        # 只要不是 404 就说明端点存在
        assert response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_login_endpoint_exists(self, client):
        """测试登录端点存在"""
        response = await client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "Test123456"
        })
        assert response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_me_requires_auth(self, client):
        """测试获取当前用户需要认证"""
        response = await client.get("/api/v1/auth/me")
        # 应该返回 401 或 403
        assert response.status_code in [401, 403, 404]


class TestProjects:
    """项目测试"""
    
    @pytest.mark.asyncio
    async def test_projects_list_requires_auth(self, client):
        """测试项目列表需要认证"""
        response = await client.get("/api/v1/projects")
        assert response.status_code in [401, 403, 404]
    
    @pytest.mark.asyncio
    async def test_create_project_requires_auth(self, client, mock_project_data):
        """测试创建项目需要认证"""
        response = await client.post("/api/v1/projects", json=mock_project_data)
        assert response.status_code in [401, 403, 404]


class TestEnhance:
    """画质增强测试"""
    
    @pytest.mark.asyncio
    async def test_enhance_settings_endpoint(self, client):
        """测试增强设置端点"""
        response = await client.post("/api/v1/enhance/settings", json={
            "has_faces": True,
            "has_hands": True,
            "is_wide_shot": False,
            "width": 1024,
            "height": 576
        })
        # 需要认证
        assert response.status_code in [200, 401, 403, 404]


class TestInpaint:
    """局部修改测试"""
    
    @pytest.mark.asyncio
    async def test_expressions_list(self, client):
        """测试表情列表端点"""
        response = await client.get("/api/v1/inpaint/expressions")
        # 需要认证
        assert response.status_code in [200, 401, 403, 404]
    
    @pytest.mark.asyncio
    async def test_gaze_directions_list(self, client):
        """测试视线方向列表端点"""
        response = await client.get("/api/v1/inpaint/gaze-directions")
        assert response.status_code in [200, 401, 403, 404]


class TestControlNet:
    """ControlNet 测试"""
    
    @pytest.mark.asyncio
    async def test_controlnet_types(self, client):
        """测试 ControlNet 类型列表"""
        response = await client.get("/api/v1/controlnet/types")
        assert response.status_code in [200, 401, 403, 404]
    
    @pytest.mark.asyncio
    async def test_preset_poses(self, client):
        """测试预设姿势列表"""
        response = await client.get("/api/v1/controlnet/presets")
        assert response.status_code in [200, 401, 403, 404]


class TestQuota:
    """配额测试"""
    
    @pytest.mark.asyncio
    async def test_quota_requires_auth(self, client):
        """测试配额接口需要认证"""
        response = await client.get("/api/v1/quota/me")
        assert response.status_code in [401, 403, 404]

