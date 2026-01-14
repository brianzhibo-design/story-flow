/**
 * WebSocket 连接管理
 * 
 * 功能:
 * - 自动连接/重连
 * - 指数退避重连策略
 * - 心跳保活
 * - 页面可见性检测
 * - 消息处理
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useEventListener } from '@vueuse/core'
import { ElMessage } from 'element-plus'
import { storage } from '@/utils/storage'
import { useProjectStore } from '@/stores'
import type { TaskProgressMessage } from '@/types'

// ==================== 配置 ====================

const MAX_RECONNECT_ATTEMPTS = 5
const BASE_RECONNECT_DELAY = 1000  // 1秒
const MAX_RECONNECT_DELAY = 30000  // 30秒
const HEARTBEAT_INTERVAL = 30000   // 30秒

// ==================== 类型 ====================

interface WebSocketOptions {
  /** 是否自动连接 */
  autoConnect?: boolean
  /** 连接成功回调 */
  onOpen?: () => void
  /** 连接关闭回调 */
  onClose?: () => void
  /** 消息回调 */
  onMessage?: (message: TaskProgressMessage) => void
  /** 错误回调 */
  onError?: (error: Event) => void
}

// ==================== 主函数 ====================

export function useWebSocket(projectId: string, options: WebSocketOptions = {}) {
  const {
    autoConnect = true,
    onOpen,
    onClose,
    onMessage,
    onError,
  } = options
  
  const projectStore = useProjectStore()
  
  // ==================== 状态 ====================
  
  const socket = ref<WebSocket | null>(null)
  const connected = ref(false)
  const connecting = ref(false)
  const lastMessage = ref<TaskProgressMessage | null>(null)
  const reconnectAttempts = ref(0)
  const error = ref<string | null>(null)
  
  let heartbeatTimer: ReturnType<typeof setInterval> | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  
  // ==================== 方法 ====================
  
  /**
   * 获取 WebSocket URL
   */
  function getWebSocketUrl(): string {
    const token = storage.getToken()
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    return `${protocol}//${host}/api/v1/ws/tasks/${projectId}?token=${token}`
  }
  
  /**
   * 计算重连延迟（指数退避）
   */
  function getReconnectDelay(): number {
    const delay = BASE_RECONNECT_DELAY * Math.pow(2, reconnectAttempts.value)
    return Math.min(delay, MAX_RECONNECT_DELAY)
  }
  
  /**
   * 开始心跳
   */
  function startHeartbeat() {
    stopHeartbeat()
    heartbeatTimer = setInterval(() => {
      if (socket.value?.readyState === WebSocket.OPEN) {
        socket.value.send(JSON.stringify({ type: 'ping' }))
      }
    }, HEARTBEAT_INTERVAL)
  }
  
  /**
   * 停止心跳
   */
  function stopHeartbeat() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }
  
  /**
   * 取消重连定时器
   */
  function cancelReconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }
  
  /**
   * 处理消息
   */
  function handleMessage(message: TaskProgressMessage) {
    lastMessage.value = message
    
    // 调用用户回调
    onMessage?.(message)
    
    // 更新任务状态
    projectStore.updateTask(message.task_id, {
      id: message.task_id,
      type: message.type as 'storyboard' | 'image' | 'video' | 'compose',
      status: message.status as 'pending' | 'queued' | 'running' | 'completed' | 'failed',
      progress: message.progress,
      progress_message: message.message,
      error_message: message.error,
    })
    
    // 任务完成时更新分镜
    if (message.status === 'completed' && message.result) {
      const result = message.result
      
      if (message.type === 'image' && result.scene_id) {
        projectStore.updateScene(result.scene_id as string, {
          image_url: result.image_url as string,
          status: 'completed',
        })
      }
      
      if (message.type === 'video' && result.scene_id) {
        projectStore.updateScene(result.scene_id as string, {
          video_url: result.video_url as string,
          status: 'completed',
        })
      }
    }
    
    // 任务失败时更新分镜
    if (message.status === 'failed' && message.result?.scene_id) {
      projectStore.updateScene(message.result.scene_id as string, {
        status: 'failed',
      })
    }
  }
  
  /**
   * 连接 WebSocket
   */
  function connect() {
    const token = storage.getToken()
    if (!token) {
      error.value = '未登录'
      return
    }
    
    if (socket.value?.readyState === WebSocket.OPEN) {
      return // 已连接
    }
    
    if (connecting.value) {
      return // 正在连接
    }
    
    connecting.value = true
    error.value = null
    
    try {
      const wsUrl = getWebSocketUrl()
      const ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        connected.value = true
        connecting.value = false
        reconnectAttempts.value = 0
        error.value = null
        
        console.log('[WebSocket] Connected')
        startHeartbeat()
        onOpen?.()
      }
      
      ws.onmessage = (event) => {
        try {
          const message: TaskProgressMessage = JSON.parse(event.data)
          
          // 忽略 pong 消息
          if ((message as unknown as { type: string }).type === 'pong') {
            return
          }
          
          handleMessage(message)
        } catch (e) {
          console.error('[WebSocket] Failed to parse message:', e)
        }
      }
      
      ws.onclose = (event) => {
        connected.value = false
        connecting.value = false
        stopHeartbeat()
        
        console.log('[WebSocket] Disconnected:', event.code, event.reason)
        onClose?.()
        
        // 非正常关闭且未达到最大重试次数，尝试重连
        if (!event.wasClean && reconnectAttempts.value < MAX_RECONNECT_ATTEMPTS) {
          scheduleReconnect()
        } else if (reconnectAttempts.value >= MAX_RECONNECT_ATTEMPTS) {
          error.value = '连接失败，请刷新页面重试'
          ElMessage.error('实时连接失败，请刷新页面')
        }
      }
      
      ws.onerror = (event) => {
        console.error('[WebSocket] Error:', event)
        error.value = '连接错误'
        onError?.(event)
        ws.close()
      }
      
      socket.value = ws
    } catch (e) {
      connecting.value = false
      error.value = '连接失败'
      console.error('[WebSocket] Connection failed:', e)
    }
  }
  
  /**
   * 安排重连
   */
  function scheduleReconnect() {
    cancelReconnect()
    
    const delay = getReconnectDelay()
    reconnectAttempts.value++
    
    console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${reconnectAttempts.value}/${MAX_RECONNECT_ATTEMPTS})`)
    
    reconnectTimer = setTimeout(() => {
      connect()
    }, delay)
  }
  
  /**
   * 断开连接
   */
  function disconnect() {
    cancelReconnect()
    stopHeartbeat()
    
    if (socket.value) {
      socket.value.close(1000, 'Client disconnect')
      socket.value = null
    }
    
    connected.value = false
    connecting.value = false
    reconnectAttempts.value = 0
  }
  
  /**
   * 发送消息
   */
  function send(data: unknown) {
    if (socket.value?.readyState === WebSocket.OPEN) {
      socket.value.send(JSON.stringify(data))
      return true
    }
    return false
  }
  
  /**
   * 重置重连计数
   */
  function resetReconnect() {
    reconnectAttempts.value = 0
    error.value = null
  }
  
  // ==================== 页面可见性检测 ====================
  
  useEventListener(document, 'visibilitychange', () => {
    if (document.visibilityState === 'visible') {
      // 页面变为可见时，检查连接状态
      if (!connected.value && !connecting.value) {
        resetReconnect()
        connect()
      }
    }
  })
  
  // ==================== 生命周期 ====================
  
  onMounted(() => {
    if (autoConnect) {
      connect()
    }
  })
  
  onUnmounted(() => {
    disconnect()
  })
  
  // 监听 projectId 变化
  watch(() => projectId, (newId, oldId) => {
    if (newId !== oldId) {
      disconnect()
      if (autoConnect) {
        connect()
      }
    }
  })
  
  return {
    // 状态
    connected,
    connecting,
    lastMessage,
    error,
    reconnectAttempts,
    
    // 方法
    connect,
    disconnect,
    send,
    resetReconnect,
  }
}
