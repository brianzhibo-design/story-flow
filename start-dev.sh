#!/bin/bash

echo "🚀 StoryFlow 开发环境启动脚本"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker 已安装${NC}"

# 1. 启动基础设施
echo ""
echo "📦 Step 1: 启动基础设施 (PostgreSQL, Redis, RabbitMQ, MinIO)..."
cd infrastructure/docker

docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "🔍 检查服务状态..."
docker-compose ps

cd "$SCRIPT_DIR"

# 2. 创建后端环境
echo ""
echo "🐍 Step 2: 配置后端环境..."
cd backend

# 创建 .env 文件
if [ ! -f .env ]; then
    cat > .env << 'ENV_EOF'
# 应用配置
APP_NAME=StoryFlow
DEBUG=true

# 安全配置
SECRET_KEY=dev-secret-key-change-in-production-abc123xyz789

# 数据库
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/storyflow

# Redis
REDIS_URL=redis://localhost:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# 对象存储 (MinIO)
STORAGE_TYPE=minio
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=storyflow
MINIO_SECURE=false

# AI 服务 (测试模式)
AI_MOCK_MODE=true
DEEPSEEK_API_KEY=
JIMENG_API_KEY=
KLING_API_KEY=

# ComfyUI (可选)
COMFYUI_URL=

# TTS (可选)
VOLCENGINE_TTS_APP_ID=
VOLCENGINE_TTS_TOKEN=

# 日志
LOG_LEVEL=DEBUG
ENV_EOF
    echo -e "${GREEN}✓ 创建 .env 文件${NC}"
else
    echo -e "${YELLOW}⚠ .env 文件已存在，跳过${NC}"
fi

# 创建虚拟环境
if [ ! -d venv ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate

# 检查 requirements.txt
if [ -f requirements.txt ]; then
    echo "安装 Python 依赖..."
    pip install -r requirements.txt --quiet 2>/dev/null || pip install -r requirements.txt
    echo -e "${GREEN}✓ 后端依赖安装完成${NC}"
else
    echo -e "${YELLOW}⚠ requirements.txt 不存在${NC}"
fi

cd "$SCRIPT_DIR"

# 3. 前端依赖
echo ""
echo "📦 Step 3: 安装前端依赖..."
cd frontend
if [ -f package.json ]; then
    npm install --silent 2>/dev/null || npm install
    echo -e "${GREEN}✓ 前端依赖安装完成${NC}"
else
    echo -e "${YELLOW}⚠ 前端 package.json 不存在，跳过${NC}"
fi
cd "$SCRIPT_DIR"

echo ""
echo "================================"
echo -e "${GREEN}✅ 环境准备完成！${NC}"
echo ""
echo "📝 下一步操作："
echo "  1. 初始化数据库:"
echo "     cd backend && source venv/bin/activate && alembic upgrade head"
echo ""
echo "  2. 启动后端:"
echo "     uvicorn app.main:app --reload --port 8000"
echo ""
echo "  3. 启动 Worker (新终端):"
echo "     celery -A app.workers.celery_app worker -l INFO"
echo ""
echo "  4. 启动前端 (新终端):"
echo "     cd frontend && npm run dev"
echo ""
echo "📊 服务地址："
echo "  - 后端 API:  http://localhost:8000"
echo "  - API 文档:  http://localhost:8000/docs"
echo "  - 前端:      http://localhost:5173"
echo "  - MinIO:     http://localhost:9001 (minioadmin/minioadmin)"
echo "  - RabbitMQ:  http://localhost:15672 (guest/guest)"

