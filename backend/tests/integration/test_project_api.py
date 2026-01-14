"""
项目 API 集成测试
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestProjectAPI:
    """项目 API 测试"""
    
    @pytest.mark.asyncio
    async def test_create_project(self, client: AsyncClient, auth_headers):
        """测试创建项目"""
        response = await client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={
                "title": "测试项目",
                "description": "这是一个测试项目",
                "story_text": "从前有座山，山里有座庙..."
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "测试项目"
        assert "id" in data["data"]
    
    @pytest.mark.asyncio
    async def test_create_project_unauthorized(self, client: AsyncClient):
        """测试未认证创建项目失败"""
        response = await client.post(
            "/api/v1/projects",
            json={
                "title": "测试项目",
                "story_text": "故事内容"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_list_projects(self, client: AsyncClient, auth_headers):
        """测试获取项目列表"""
        # 先创建一个项目
        await client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={
                "title": "列表测试项目",
                "story_text": "故事内容"
            }
        )
        
        response = await client.get(
            "/api/v1/projects",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"]["items"], list)
    
    @pytest.mark.asyncio
    async def test_get_project_detail(self, client: AsyncClient, auth_headers):
        """测试获取项目详情"""
        # 先创建一个项目
        create_response = await client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={
                "title": "详情测试项目",
                "story_text": "故事内容"
            }
        )
        
        project_id = create_response.json()["data"]["id"]
        
        response = await client.get(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == project_id
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_project(self, client: AsyncClient, auth_headers):
        """测试获取不存在的项目"""
        fake_id = str(uuid4())
        
        response = await client.get(
            f"/api/v1/projects/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_project(self, client: AsyncClient, auth_headers):
        """测试更新项目"""
        # 先创建项目
        create_response = await client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={
                "title": "原标题",
                "story_text": "故事内容"
            }
        )
        
        project_id = create_response.json()["data"]["id"]
        
        # 更新项目
        response = await client.put(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers,
            json={
                "title": "新标题",
                "description": "添加描述"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == "新标题"
    
    @pytest.mark.asyncio
    async def test_delete_project(self, client: AsyncClient, auth_headers):
        """测试删除项目"""
        # 先创建项目
        create_response = await client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={
                "title": "待删除项目",
                "story_text": "故事内容"
            }
        )
        
        project_id = create_response.json()["data"]["id"]
        
        # 删除项目
        response = await client.delete(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # 验证已删除
        get_response = await client.get(
            f"/api/v1/projects/{project_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

