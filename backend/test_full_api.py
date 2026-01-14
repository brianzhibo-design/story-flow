#!/usr/bin/env python3
"""
StoryFlow API 全面测试脚本
"""
import httpx
import asyncio
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.project_id = None
        self.share_code = None
        self.test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        self.test_username = f"testuser_{uuid.uuid4().hex[:8]}"
        self.test_password = "Test123456!"
        
    async def run_all_tests(self):
        """运行所有测试"""
        results = []
        
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=30) as client:
            self.client = client
            
            # 1. 基础健康检查
            results.append(await self.test_health())
            results.append(await self.test_ai_health())
            
            # 2. 认证测试
            results.append(await self.test_register())
            results.append(await self.test_login())
            results.append(await self.test_me())
            
            # 3. 订阅测试
            results.append(await self.test_get_plans())
            results.append(await self.test_get_current_subscription())
            results.append(await self.test_get_usage())
            results.append(await self.test_check_quota())
            
            # 4. 项目测试
            results.append(await self.test_create_project())
            results.append(await self.test_list_projects())
            results.append(await self.test_get_project())
            results.append(await self.test_update_project())
            
            # 5. AI 服务测试 (Mock 模式)
            results.append(await self.test_generate_storyboard())
            results.append(await self.test_generate_image())
            results.append(await self.test_generate_video())
            results.append(await self.test_tts())
            results.append(await self.test_get_voices())
            
            # 6. 支付测试
            results.append(await self.test_get_price())
            results.append(await self.test_create_order())
            
            # 7. 分享测试
            results.append(await self.test_create_share())
            results.append(await self.test_list_shares())
            results.append(await self.test_access_share())
            
            # 8. 清理
            results.append(await self.test_delete_share())
            results.append(await self.test_delete_project())
        
        return results
    
    def _headers(self):
        """获取认证头"""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    # ==================== 基础测试 ====================
    
    async def test_health(self):
        """健康检查"""
        try:
            r = await self.client.get("/health")
            success = r.status_code == 200
            return {"name": "健康检查 /health", "success": success, "message": r.text[:100] if success else f"Status: {r.status_code}"}
        except Exception as e:
            return {"name": "健康检查 /health", "success": False, "message": str(e)}
    
    async def test_ai_health(self):
        """AI 服务健康检查"""
        try:
            r = await self.client.get("/api/v1/ai/health")
            success = r.status_code == 200
            return {"name": "AI 健康检查", "success": success, "message": "OK" if success else f"Status: {r.status_code}"}
        except Exception as e:
            return {"name": "AI 健康检查", "success": False, "message": str(e)}
    
    # ==================== 认证测试 ====================
    
    async def test_register(self):
        """用户注册"""
        try:
            data = {
                "username": self.test_username,
                "email": self.test_email,
                "password": self.test_password
            }
            r = await self.client.post("/api/v1/auth/register", json=data)
            success = r.status_code == 200
            if success:
                self.user_id = r.json().get("data", {}).get("id")
            return {"name": "用户注册", "success": success, "message": f"User: {self.test_username}" if success else r.text[:100]}
        except Exception as e:
            return {"name": "用户注册", "success": False, "message": str(e)}
    
    async def test_login(self):
        """用户登录"""
        try:
            data = {
                "username": self.test_username,
                "password": self.test_password
            }
            r = await self.client.post("/api/v1/auth/login", data=data)
            success = r.status_code == 200
            if success:
                self.token = r.json().get("access_token")
            return {"name": "用户登录", "success": success, "message": "Token 获取成功" if success else r.text[:100]}
        except Exception as e:
            return {"name": "用户登录", "success": False, "message": str(e)}
    
    async def test_me(self):
        """获取当前用户"""
        try:
            r = await self.client.get("/api/v1/auth/me", headers=self._headers())
            success = r.status_code == 200
            return {"name": "获取当前用户", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "获取当前用户", "success": False, "message": str(e)}
    
    # ==================== 订阅测试 ====================
    
    async def test_get_plans(self):
        """获取订阅计划"""
        try:
            r = await self.client.get("/api/v1/subscription/plans")
            success = r.status_code == 200
            count = len(r.json().get("data", [])) if success else 0
            return {"name": "获取订阅计划", "success": success, "message": f"{count} 个计划" if success else r.text[:100]}
        except Exception as e:
            return {"name": "获取订阅计划", "success": False, "message": str(e)}
    
    async def test_get_current_subscription(self):
        """获取当前订阅"""
        try:
            r = await self.client.get("/api/v1/subscription/current", headers=self._headers())
            success = r.status_code == 200
            return {"name": "获取当前订阅", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "获取当前订阅", "success": False, "message": str(e)}
    
    async def test_get_usage(self):
        """获取使用量"""
        try:
            r = await self.client.get("/api/v1/subscription/usage", headers=self._headers())
            success = r.status_code == 200
            return {"name": "获取使用量", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "获取使用量", "success": False, "message": str(e)}
    
    async def test_check_quota(self):
        """检查配额"""
        try:
            r = await self.client.get("/api/v1/subscription/check/image", headers=self._headers())
            success = r.status_code == 200
            return {"name": "检查配额", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "检查配额", "success": False, "message": str(e)}
    
    # ==================== 项目测试 ====================
    
    async def test_create_project(self):
        """创建项目"""
        try:
            data = {
                "title": f"测试项目 {datetime.now().strftime('%H:%M:%S')}",
                "description": "API 测试创建的项目",
                "story_text": "从前有座山，山上有座庙。庙里有个老和尚在给小和尚讲故事。"
            }
            r = await self.client.post("/api/v1/projects", json=data, headers=self._headers())
            success = r.status_code == 200
            if success:
                self.project_id = r.json().get("data", {}).get("id")
            return {"name": "创建项目", "success": success, "message": f"ID: {self.project_id}" if success else r.text[:100]}
        except Exception as e:
            return {"name": "创建项目", "success": False, "message": str(e)}
    
    async def test_list_projects(self):
        """获取项目列表"""
        try:
            r = await self.client.get("/api/v1/projects", headers=self._headers())
            success = r.status_code == 200
            count = len(r.json().get("data", [])) if success else 0
            return {"name": "获取项目列表", "success": success, "message": f"{count} 个项目" if success else r.text[:100]}
        except Exception as e:
            return {"name": "获取项目列表", "success": False, "message": str(e)}
    
    async def test_get_project(self):
        """获取项目详情"""
        try:
            if not self.project_id:
                return {"name": "获取项目详情", "success": False, "message": "无项目 ID"}
            r = await self.client.get(f"/api/v1/projects/{self.project_id}", headers=self._headers())
            success = r.status_code == 200
            return {"name": "获取项目详情", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "获取项目详情", "success": False, "message": str(e)}
    
    async def test_update_project(self):
        """更新项目"""
        try:
            if not self.project_id:
                return {"name": "更新项目", "success": False, "message": "无项目 ID"}
            data = {"title": "更新后的标题"}
            r = await self.client.put(f"/api/v1/projects/{self.project_id}", json=data, headers=self._headers())
            success = r.status_code == 200
            return {"name": "更新项目", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "更新项目", "success": False, "message": str(e)}
    
    # ==================== AI 服务测试 ====================
    
    async def test_generate_storyboard(self):
        """生成分镜"""
        try:
            data = {
                "story_text": "小明去上学，路上遇到了小红。",
                "style": "anime"
            }
            r = await self.client.post("/api/v1/ai/storyboard", json=data, headers=self._headers())
            success = r.status_code == 200
            return {"name": "生成分镜", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "生成分镜", "success": False, "message": str(e)}
    
    async def test_generate_image(self):
        """生成图片"""
        try:
            data = {
                "prompt": "一个小男孩在阳光下奔跑",
                "style": "anime"
            }
            r = await self.client.post("/api/v1/ai/image", json=data, headers=self._headers())
            success = r.status_code == 200
            return {"name": "生成图片", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "生成图片", "success": False, "message": str(e)}
    
    async def test_generate_video(self):
        """生成视频"""
        try:
            data = {
                "image_url": "https://example.com/image.png",
                "prompt": "角色向前走动"
            }
            r = await self.client.post("/api/v1/ai/video", json=data, headers=self._headers())
            # 视频生成可能返回 202 (异步任务) 或 200
            success = r.status_code in [200, 202]
            return {"name": "生成视频", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "生成视频", "success": False, "message": str(e)}
    
    async def test_tts(self):
        """语音合成"""
        try:
            data = {
                "text": "你好，这是一段测试语音。",
                "voice_id": "zh-CN-XiaoxiaoNeural"
            }
            r = await self.client.post("/api/v1/ai/tts", json=data, headers=self._headers())
            success = r.status_code == 200
            return {"name": "语音合成", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "语音合成", "success": False, "message": str(e)}
    
    async def test_get_voices(self):
        """获取音色列表"""
        try:
            r = await self.client.get("/api/v1/ai/voices", headers=self._headers())
            success = r.status_code == 200
            return {"name": "获取音色列表", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "获取音色列表", "success": False, "message": str(e)}
    
    # ==================== 支付测试 ====================
    
    async def test_get_price(self):
        """获取价格"""
        try:
            r = await self.client.get("/api/v1/payment/price", params={"plan_type": "basic", "billing_cycle": "monthly"})
            success = r.status_code == 200
            return {"name": "获取价格", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "获取价格", "success": False, "message": str(e)}
    
    async def test_create_order(self):
        """创建支付订单"""
        try:
            data = {
                "plan_type": "basic",
                "billing_cycle": "monthly",
                "payment_method": "alipay"
            }
            r = await self.client.post("/api/v1/payment/create-order", json=data, headers=self._headers())
            success = r.status_code == 200
            return {"name": "创建支付订单", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "创建支付订单", "success": False, "message": str(e)}
    
    # ==================== 分享测试 ====================
    
    async def test_create_share(self):
        """创建分享"""
        try:
            if not self.project_id:
                return {"name": "创建分享", "success": False, "message": "无项目 ID"}
            data = {
                "project_id": self.project_id,
                "share_type": "view"
            }
            r = await self.client.post("/api/v1/share/create", json=data, headers=self._headers())
            success = r.status_code == 200
            if success:
                self.share_code = r.json().get("data", {}).get("share_code")
            return {"name": "创建分享", "success": success, "message": f"Code: {self.share_code}" if success else r.text[:100]}
        except Exception as e:
            return {"name": "创建分享", "success": False, "message": str(e)}
    
    async def test_list_shares(self):
        """获取分享列表"""
        try:
            if not self.project_id:
                return {"name": "获取分享列表", "success": False, "message": "无项目 ID"}
            r = await self.client.get(f"/api/v1/share/list/{self.project_id}", headers=self._headers())
            success = r.status_code == 200
            return {"name": "获取分享列表", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "获取分享列表", "success": False, "message": str(e)}
    
    async def test_access_share(self):
        """访问分享"""
        try:
            if not self.share_code:
                return {"name": "访问分享", "success": False, "message": "无分享码"}
            r = await self.client.get(f"/api/v1/share/access/{self.share_code}")
            success = r.status_code == 200
            return {"name": "访问分享", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "访问分享", "success": False, "message": str(e)}
    
    async def test_delete_share(self):
        """删除分享"""
        try:
            if not self.share_code:
                return {"name": "删除分享", "success": False, "message": "无分享码"}
            r = await self.client.delete(f"/api/v1/share/{self.share_code}", headers=self._headers())
            success = r.status_code == 200
            return {"name": "删除分享", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "删除分享", "success": False, "message": str(e)}
    
    # ==================== 清理 ====================
    
    async def test_delete_project(self):
        """删除项目"""
        try:
            if not self.project_id:
                return {"name": "删除项目", "success": False, "message": "无项目 ID"}
            r = await self.client.delete(f"/api/v1/projects/{self.project_id}", headers=self._headers())
            success = r.status_code == 200
            return {"name": "删除项目", "success": success, "message": "OK" if success else r.text[:100]}
        except Exception as e:
            return {"name": "删除项目", "success": False, "message": str(e)}


async def main():
    print("=" * 60)
    print("🧪 StoryFlow API 全面测试")
    print("=" * 60)
    print()
    
    tester = APITester()
    results = await tester.run_all_tests()
    
    # 统计结果
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    
    print()
    print("=" * 60)
    print(f"📊 测试结果: {passed}/{len(results)} 通过 ({passed/len(results)*100:.1f}%)")
    print("=" * 60)
    print()
    
    # 输出详细结果
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"{status} {r['name']}: {r.get('message', '')}")
    
    print()
    
    # 输出失败的测试
    failed_tests = [r for r in results if not r['success']]
    if failed_tests:
        print("❌ 失败的测试:")
        for r in failed_tests:
            print(f"   - {r['name']}: {r.get('message', '')}")
    else:
        print("🎉 所有测试通过！")


if __name__ == "__main__":
    asyncio.run(main())

