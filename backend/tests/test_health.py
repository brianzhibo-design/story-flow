"""
健康检查测试
"""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """测试健康检查接口"""
    response = await client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data


@pytest.mark.asyncio
async def test_root(client):
    """测试根路径"""
    response = await client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "docs" in data


@pytest.mark.asyncio
async def test_docs_available(client):
    """测试 API 文档可访问"""
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_openapi_json(client):
    """测试 OpenAPI JSON"""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    
    data = response.json()
    assert "openapi" in data
    assert "info" in data

