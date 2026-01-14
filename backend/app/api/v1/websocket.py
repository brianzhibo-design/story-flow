"""
WebSocket 接口

实时推送任务进度
"""

import asyncio
import json
from typing import Dict, Set

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.config import settings
from app.core.redis import redis_client
from app.core.security import decode_token
from app.core.exceptions import TokenInvalidError

logger = structlog.get_logger()

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # project_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, project_id: str):
        """建立连接"""
        await websocket.accept()
        
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        self.active_connections[project_id].add(websocket)
        
        logger.info("websocket_connected", project_id=project_id)
    
    def disconnect(self, websocket: WebSocket, project_id: str):
        """断开连接"""
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        
        logger.info("websocket_disconnected", project_id=project_id)
    
    async def broadcast(self, project_id: str, message: dict):
        """广播消息到项目的所有连接"""
        if project_id not in self.active_connections:
            return
        
        dead_connections = set()
        
        for websocket in self.active_connections[project_id]:
            try:
                await websocket.send_json(message)
            except Exception:
                dead_connections.add(websocket)
        
        # 清理断开的连接
        for websocket in dead_connections:
            self.disconnect(websocket, project_id)


# 全局连接管理器
manager = ConnectionManager()


async def verify_token(token: str) -> str | None:
    """验证 WebSocket Token"""
    try:
        payload = decode_token(token)
        return payload.get("sub")
    except (TokenInvalidError, Exception):
        return None


@router.websocket("/ws/tasks/{project_id}")
async def task_progress_websocket(
    websocket: WebSocket,
    project_id: str,
    token: str = Query(...)
):
    """
    任务进度 WebSocket
    
    连接: ws://host/api/v1/ws/tasks/{project_id}?token={jwt_token}
    
    接收消息格式:
    {
        "task_id": "xxx",
        "type": "image",
        "status": "running",
        "progress": 50,
        "message": "生成中..."
    }
    """
    # 验证 Token
    user_id = await verify_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    # TODO: 验证用户是否有权访问该项目
    
    # 建立连接
    await manager.connect(websocket, project_id)
    
    redis_task = None
    try:
        # 启动 Redis 订阅任务
        redis_task = asyncio.create_task(
            subscribe_redis(project_id, websocket)
        )
        
        # 保持连接，接收客户端消息（心跳等）
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30
                )
                
                # 处理客户端消息
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except asyncio.TimeoutError:
                # 发送心跳
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except Exception:
                    break
                    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, project_id)
        if redis_task:
            redis_task.cancel()


async def subscribe_redis(project_id: str, websocket: WebSocket):
    """订阅 Redis 频道，转发消息到 WebSocket"""
    if not redis_client.client:
        return
    
    pubsub = redis_client.client.pubsub()
    channel = f"task:progress:{project_id}"
    
    try:
        await pubsub.subscribe(channel)
        
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    await websocket.send_json(data)
                except Exception as e:
                    logger.error("redis_message_error", error=str(e))
    except asyncio.CancelledError:
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()


# 用于从其他地方推送消息
async def push_task_progress(
    project_id: str,
    task_id: str,
    task_type: str,
    status: str,
    progress: int,
    message: str = "",
    result: dict = None,
    error: str = None
):
    """推送任务进度（供 Worker 调用）"""
    channel = f"task:progress:{project_id}"
    
    data = {
        "task_id": task_id,
        "type": task_type,
        "status": status,
        "progress": progress,
        "message": message,
    }
    
    if result:
        data["result"] = result
    if error:
        data["error"] = error
    
    await redis_client.publish(channel, json.dumps(data))

