#!/bin/bash

echo "🔍 StoryFlow 服务状态检查"
echo "=========================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查 PostgreSQL
echo ""
echo "📦 PostgreSQL..."
if docker exec storyflow-postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ 运行中${NC}"
    # 显示数据库列表
    docker exec storyflow-postgres psql -U postgres -c "\l" 2>/dev/null | grep storyflow || true
else
    echo -e "  ${RED}❌ 未运行${NC}"
fi

# 检查 Redis
echo ""
echo "📦 Redis..."
if docker exec storyflow-redis redis-cli ping > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ 运行中${NC}"
    # 显示连接信息
    echo "  $(docker exec storyflow-redis redis-cli info server 2>/dev/null | grep redis_version)"
else
    echo -e "  ${RED}❌ 未运行${NC}"
fi

# 检查 RabbitMQ
echo ""
echo "📦 RabbitMQ..."
if curl -s http://guest:guest@localhost:15672/api/overview > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ 运行中${NC}"
    RABBIT_INFO=$(curl -s http://guest:guest@localhost:15672/api/overview 2>/dev/null)
    echo "  Node: $(echo $RABBIT_INFO | python3 -c 'import sys,json; print(json.load(sys.stdin).get("node","unknown"))' 2>/dev/null || echo 'unknown')"
else
    echo -e "  ${RED}❌ 未运行${NC}"
fi

# 检查 MinIO
echo ""
echo "📦 MinIO..."
if curl -s http://localhost:9000/minio/health/live > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ 运行中${NC}"
    echo "  Console: http://localhost:9001"
else
    echo -e "  ${RED}❌ 未运行${NC}"
fi

# 检查后端 API
echo ""
echo "🌐 后端 API..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health 2>/dev/null)
if [ -n "$HEALTH_RESPONSE" ]; then
    echo -e "  ${GREEN}✅ 运行中${NC}"
    echo "  $HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "  $HEALTH_RESPONSE"
else
    echo -e "  ${YELLOW}⚠ 未运行 (需要手动启动: uvicorn app.main:app --reload)${NC}"
fi

# 检查前端
echo ""
echo "🌐 前端..."
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ 运行中${NC}"
    echo "  URL: http://localhost:5173"
else
    echo -e "  ${YELLOW}⚠ 未运行 (需要手动启动: cd frontend && npm run dev)${NC}"
fi

echo ""
echo "=========================="
echo "📊 Docker 容器状态:"
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null | grep -E "(NAMES|storyflow)" || echo "没有运行中的 storyflow 容器"

echo ""
echo "💡 快速命令:"
echo "  启动基础设施: cd infrastructure/docker && docker-compose up -d"
echo "  停止基础设施: cd infrastructure/docker && docker-compose down"
echo "  查看日志:     cd infrastructure/docker && docker-compose logs -f"

