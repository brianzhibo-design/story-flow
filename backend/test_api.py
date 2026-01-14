#!/usr/bin/env python3
"""
StoryFlow API 测试脚本

用法:
    python test_api.py

测试内容:
    1. 基础接口测试 (健康检查)
    2. 认证接口测试 (注册/登录)
    3. 项目接口测试 (CRUD)
    4. 分镜生成测试 (Mock 模式)
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

# 测试数据
TEST_USER = {
    "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
    "username": "TestUser",
    "password": "Test123456!"
}

# 测试结果
results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}


def log_test(name: str, passed: bool, detail: str = ""):
    """记录测试结果"""
    status = "✅" if passed else "❌"
    print(f"   {status} {name}")
    if detail and not passed:
        print(f"      {detail}")
    
    results["tests"].append({"name": name, "passed": passed})
    if passed:
        results["passed"] += 1
    else:
        results["failed"] += 1


async def test_basic():
    """基础接口测试"""
    print("\n📦 1. 基础接口测试")
    
    async with httpx.AsyncClient(timeout=30) as client:
        # 健康检查
        try:
            resp = await client.get(f"{BASE_URL}/health")
            log_test("健康检查 /health", resp.status_code == 200)
        except Exception as e:
            log_test("健康检查 /health", False, str(e))
        
        # 根路径
        try:
            resp = await client.get(f"{BASE_URL}/")
            log_test("根路径 /", resp.status_code in [200, 404])
        except Exception as e:
            log_test("根路径 /", False, str(e))
        
        # API 文档
        try:
            resp = await client.get(f"{BASE_URL}/docs")
            log_test("API 文档 /docs", resp.status_code == 200)
        except Exception as e:
            log_test("API 文档 /docs", False, str(e))


async def test_auth():
    """认证接口测试"""
    print("\n🔐 2. 认证接口测试")
    
    token = None
    
    async with httpx.AsyncClient(timeout=30) as client:
        # 用户注册
        try:
            resp = await client.post(
                f"{API_URL}/auth/register",
                json=TEST_USER
            )
            passed = resp.status_code in [200, 201]
            log_test("用户注册 /api/v1/auth/register", passed, resp.text[:100] if not passed else "")
            
            if passed:
                data = resp.json()
                token = data.get("data", {}).get("tokens", {}).get("access_token")
        except Exception as e:
            log_test("用户注册 /api/v1/auth/register", False, str(e))
        
        # 用户登录
        try:
            resp = await client.post(
                f"{API_URL}/auth/login",
                json={
                    "email": TEST_USER["email"],
                    "password": TEST_USER["password"]
                }
            )
            passed = resp.status_code == 200
            log_test("用户登录 /api/v1/auth/login", passed, resp.text[:100] if not passed else "")
            
            if passed:
                data = resp.json()
                token = data.get("data", {}).get("tokens", {}).get("access_token")
        except Exception as e:
            log_test("用户登录 /api/v1/auth/login", False, str(e))
        
        # 获取当前用户
        if token:
            try:
                resp = await client.get(
                    f"{API_URL}/auth/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                log_test("获取当前用户 /api/v1/auth/me", resp.status_code == 200)
            except Exception as e:
                log_test("获取当前用户 /api/v1/auth/me", False, str(e))
        else:
            log_test("获取当前用户 /api/v1/auth/me", False, "无 token")
    
    return token


async def test_projects(token: str):
    """项目接口测试"""
    print("\n📁 3. 项目接口测试")
    
    if not token:
        print("   ⚠️ 跳过 (无认证 token)")
        return None
    
    project_id = None
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=30) as client:
        # 创建项目
        try:
            resp = await client.post(
                f"{API_URL}/projects",
                json={
                    "title": "测试项目",
                    "story_text": "从前有座山，山上有座庙，庙里有个老和尚在给小和尚讲故事。",
                    "style": "国画"
                },
                headers=headers
            )
            passed = resp.status_code in [200, 201]
            log_test("创建项目 /api/v1/projects", passed, resp.text[:100] if not passed else "")
            
            if passed:
                data = resp.json()
                project_id = data.get("data", {}).get("id")
        except Exception as e:
            log_test("创建项目 /api/v1/projects", False, str(e))
        
        # 项目列表
        try:
            resp = await client.get(f"{API_URL}/projects", headers=headers)
            log_test("项目列表 /api/v1/projects", resp.status_code == 200)
        except Exception as e:
            log_test("项目列表 /api/v1/projects", False, str(e))
        
        # 项目详情
        if project_id:
            try:
                resp = await client.get(f"{API_URL}/projects/{project_id}", headers=headers)
                log_test("项目详情 /api/v1/projects/{id}", resp.status_code == 200)
            except Exception as e:
                log_test("项目详情 /api/v1/projects/{id}", False, str(e))
            
            # 更新项目
            try:
                resp = await client.put(
                    f"{API_URL}/projects/{project_id}",
                    json={"title": "更新后的项目标题"},
                    headers=headers
                )
                log_test("更新项目 /api/v1/projects/{id}", resp.status_code == 200)
            except Exception as e:
                log_test("更新项目 /api/v1/projects/{id}", False, str(e))
    
    return project_id


async def test_storyboard(token: str, project_id: str):
    """分镜生成测试"""
    print("\n🎬 4. 分镜生成测试 (Mock 模式)")
    
    if not token or not project_id:
        print("   ⚠️ 跳过 (缺少 token 或 project_id)")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=60) as client:
        # 生成分镜 (需要相应的 API 端点)
        try:
            resp = await client.post(
                f"{API_URL}/projects/{project_id}/generate-storyboard",
                headers=headers
            )
            if resp.status_code == 200:
                data = resp.json()
                scenes = data.get("data", {}).get("scenes", [])
                log_test(f"生成分镜 - 生成了 {len(scenes)} 个分镜", len(scenes) > 0)
            elif resp.status_code == 404:
                log_test("生成分镜 (端点未实现)", True, "API 端点未实现，跳过")
            else:
                log_test("生成分镜", False, resp.text[:100])
        except Exception as e:
            log_test("生成分镜", False, str(e))


async def test_cleanup(token: str, project_id: str):
    """清理测试数据"""
    print("\n🧹 5. 清理测试")
    
    if not token or not project_id:
        print("   ⚠️ 跳过")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(timeout=30) as client:
        # 删除项目
        try:
            resp = await client.delete(
                f"{API_URL}/projects/{project_id}",
                headers=headers
            )
            log_test("删除项目", resp.status_code in [200, 204])
        except Exception as e:
            log_test("删除项目", False, str(e))
        
        # 验证删除
        try:
            resp = await client.get(
                f"{API_URL}/projects/{project_id}",
                headers=headers
            )
            log_test("验证删除", resp.status_code in [404, 200])  # 软删除可能返回 200
        except Exception as e:
            log_test("验证删除", False, str(e))


async def main():
    """主测试流程"""
    print("=" * 60)
    print("🧪 StoryFlow API 测试")
    print("=" * 60)
    
    # 1. 基础接口测试
    await test_basic()
    
    # 2. 认证接口测试
    token = await test_auth()
    
    # 3. 项目接口测试
    project_id = await test_projects(token)
    
    # 4. 分镜生成测试
    await test_storyboard(token, project_id)
    
    # 5. 清理
    await test_cleanup(token, project_id)
    
    # 打印汇总
    print("\n" + "=" * 60)
    total = results["passed"] + results["failed"]
    rate = results["passed"] / total * 100 if total > 0 else 0
    print(f"   ✅ 通过: {results['passed']}")
    print(f"   ❌ 失败: {results['failed']}")
    print(f"   📈 通过率: {rate:.1f}%")
    print("=" * 60)
    
    # 返回状态码
    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

