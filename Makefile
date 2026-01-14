# Makefile
.PHONY: help dev-up dev-down dev-logs install migrate test lint format

help:
	@echo "StoryFlow Development Commands"
	@echo "=============================="
	@echo "make dev-up      - 启动开发环境基础服务"
	@echo "make dev-down    - 停止开发环境"
	@echo "make dev-logs    - 查看服务日志"
	@echo "make install     - 安装Python依赖"
	@echo "make migrate     - 运行数据库迁移"
	@echo "make test        - 运行测试"
	@echo "make lint        - 代码检查"
	@echo "make format      - 代码格式化"
	@echo "make run         - 启动后端服务"

# Docker 开发环境
dev-up:
	docker-compose -f infrastructure/docker/docker-compose.yml up -d
	@echo "等待服务启动..."
	@sleep 5
	@echo "服务已启动!"
	@echo "PostgreSQL: localhost:5432"
	@echo "Redis: localhost:6379"
	@echo "RabbitMQ: localhost:5672 (管理界面: http://localhost:15672)"
	@echo "MinIO: localhost:9000 (控制台: http://localhost:9001)"

dev-down:
	docker-compose -f infrastructure/docker/docker-compose.yml down

dev-logs:
	docker-compose -f infrastructure/docker/docker-compose.yml logs -f

# Python 开发
install:
	cd backend && pip install -r requirements.txt -r requirements-dev.txt

migrate:
	cd backend && alembic upgrade head

migrate-new:
	cd backend && alembic revision --autogenerate -m "$(msg)"

test:
	cd backend && pytest -v

lint:
	cd backend && ruff check app/
	cd backend && mypy app/

format:
	cd backend && ruff format app/
	cd backend && ruff check --fix app/

run:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-worker:
	cd backend && celery -A app.workers.celery_app worker --loglevel=info

