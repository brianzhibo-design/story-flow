"""
测试配置和 Fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# 设置测试环境变量
import os
os.environ["AI_MOCK_MODE"] = "true"
os.environ["DEBUG"] = "true"

from app.main import app
from app.core.database import Base, get_db
from app.config import settings


# 测试数据库 URL
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/storyflow", "/storyflow_test")

# 创建测试引擎
test_engine = create_async_engine(
    TEST_DATABASE_URL, 
    echo=False,
    pool_pre_ping=True
)

TestSessionLocal = async_sessionmaker(
    test_engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database():
    """创建测试数据库表"""
    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
    finally:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await test_engine.dispose()


@pytest.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """获取测试客户端"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user_data():
    """模拟用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123456"
    }


@pytest.fixture
def mock_project_data():
    """模拟项目数据"""
    return {
        "title": "测试项目",
        "story_text": "从前有座山，山上有座庙，庙里有个老和尚在给小和尚讲故事。",
        "style": "realistic"
    }


@pytest.fixture
def mock_element_data():
    """模拟视觉元素数据"""
    return {
        "name": "主角",
        "element_type": "character",
        "attributes": {
            "gender": "female",
            "age_range": "young_adult",
            "hair_color": "black",
            "eye_color": "brown"
        }
    }
