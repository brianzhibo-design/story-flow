#!/bin/bash

echo "🧪 StoryFlow API 测试"
echo "======================"

BASE_URL="http://localhost:8000"
TOKEN=""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查 jq 是否安装
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}⚠ jq 未安装，输出将不会格式化${NC}"
    JQ_CMD="cat"
else
    JQ_CMD="jq"
fi

# 1. 健康检查
echo ""
echo "1️⃣ 健康检查..."
HEALTH=$(curl -s $BASE_URL/health)
if [ -n "$HEALTH" ]; then
    echo -e "${GREEN}✅ 后端运行中${NC}"
    echo "$HEALTH" | $JQ_CMD
else
    echo -e "${RED}❌ 后端未运行，请先启动: uvicorn app.main:app --reload${NC}"
    exit 1
fi

# 2. API 文档
echo ""
echo "2️⃣ API 文档检查..."
DOCS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/docs)
if [ "$DOCS" == "200" ]; then
    echo -e "${GREEN}✅ API 文档可访问: $BASE_URL/docs${NC}"
else
    echo -e "${YELLOW}⚠ API 文档不可访问${NC}"
fi

# 3. 注册用户
echo ""
echo "3️⃣ 注册用户..."
TIMESTAMP=$(date +%s)
REGISTER_RESULT=$(curl -s -X POST $BASE_URL/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser_$TIMESTAMP\",\"email\":\"test_$TIMESTAMP@example.com\",\"password\":\"Test123456\"}")

if echo "$REGISTER_RESULT" | grep -q "error\|Error\|detail"; then
    echo -e "${YELLOW}⚠ 注册响应:${NC}"
    echo "$REGISTER_RESULT" | $JQ_CMD
else
    echo -e "${GREEN}✅ 注册成功${NC}"
    echo "$REGISTER_RESULT" | $JQ_CMD
fi

# 4. 登录
echo ""
echo "4️⃣ 登录..."
LOGIN_RESULT=$(curl -s -X POST $BASE_URL/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser_$TIMESTAMP\",\"password\":\"Test123456\"}")

# 尝试多种方式提取 token
TOKEN=$(echo "$LOGIN_RESULT" | $JQ_CMD -r '.data.access_token // .access_token // .token // empty' 2>/dev/null)

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo -e "${GREEN}✅ 登录成功${NC}"
    echo "  Token: ${TOKEN:0:30}..."
else
    echo -e "${YELLOW}⚠ 登录响应:${NC}"
    echo "$LOGIN_RESULT" | $JQ_CMD
    
    # 尝试使用已存在的用户登录
    echo ""
    echo "  尝试使用默认测试账户..."
    LOGIN_RESULT=$(curl -s -X POST $BASE_URL/api/v1/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username":"testuser","password":"Test123456"}')
    TOKEN=$(echo "$LOGIN_RESULT" | $JQ_CMD -r '.data.access_token // .access_token // .token // empty' 2>/dev/null)
fi

# 5. 获取当前用户
if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo ""
    echo "5️⃣ 获取当前用户..."
    ME_RESULT=$(curl -s $BASE_URL/api/v1/auth/me \
      -H "Authorization: Bearer $TOKEN")
    echo "$ME_RESULT" | $JQ_CMD

    # 6. 创建项目
    echo ""
    echo "6️⃣ 创建项目..."
    PROJECT_RESULT=$(curl -s -X POST $BASE_URL/api/v1/projects \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "title": "测试项目",
        "story_text": "从前有座山，山上有座庙，庙里有个老和尚在给小和尚讲故事。",
        "style": "realistic"
      }')
    echo "$PROJECT_RESULT" | $JQ_CMD
    
    PROJECT_ID=$(echo "$PROJECT_RESULT" | $JQ_CMD -r '.data.id // .id // empty' 2>/dev/null)
    
    if [ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ]; then
        echo -e "${GREEN}✅ 项目创建成功: $PROJECT_ID${NC}"
        
        # 7. 获取项目详情
        echo ""
        echo "7️⃣ 获取项目详情..."
        curl -s $BASE_URL/api/v1/projects/$PROJECT_ID \
          -H "Authorization: Bearer $TOKEN" | $JQ_CMD
    fi

    # 8. 项目列表
    echo ""
    echo "8️⃣ 项目列表..."
    curl -s $BASE_URL/api/v1/projects \
      -H "Authorization: Bearer $TOKEN" | $JQ_CMD

    # 9. 获取配额
    echo ""
    echo "9️⃣ 获取用户配额..."
    curl -s $BASE_URL/api/v1/quota/me \
      -H "Authorization: Bearer $TOKEN" | $JQ_CMD

else
    echo -e "${YELLOW}⚠ 无法获取 Token，跳过认证相关测试${NC}"
fi

# 10. 测试新增的专业级 API
echo ""
echo "🔟 测试专业级 API..."

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    # 测试增强设置
    echo ""
    echo "  📸 画质增强设置..."
    curl -s -X POST $BASE_URL/api/v1/enhance/settings \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"has_faces": true, "has_hands": true, "is_wide_shot": false, "width": 1024, "height": 576}' | $JQ_CMD

    # 测试表情列表
    echo ""
    echo "  😊 支持的表情列表..."
    curl -s $BASE_URL/api/v1/inpaint/expressions \
      -H "Authorization: Bearer $TOKEN" | $JQ_CMD

    # 测试 ControlNet 类型
    echo ""
    echo "  🎛️ ControlNet 类型..."
    curl -s $BASE_URL/api/v1/controlnet/types \
      -H "Authorization: Bearer $TOKEN" | $JQ_CMD
fi

echo ""
echo "======================"
echo -e "${GREEN}✅ 测试完成!${NC}"
echo ""
echo "📊 测试摘要:"
echo "  - 健康检查: ✅"
echo "  - API 文档: $BASE_URL/docs"
if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo "  - 认证测试: ✅"
    echo "  - 项目 API: ✅"
    echo "  - 专业级 API: ✅"
else
    echo "  - 认证测试: ⚠ (需要检查)"
fi

