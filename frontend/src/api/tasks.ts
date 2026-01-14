/**
 * 任务 API 模块
 * 
 * 适配后端 RESTful API
 */
import api from '@/utils/request'

// ==================== 类型定义 ====================

export interface Task {
  id: string
  project_id: string
  scene_id: string | null
  type: 'storyboard' | 'image' | 'video' | 'compose'
  status: 'pending' | 'queued' | 'running' | 'completed' | 'failed'
  progress: number
  progress_message: string | null
  error_message: string | null
  created_at: string
}

// ==================== API 方法 ====================

export const tasksApi = {
  /**
   * 获取项目任务列表
   * GET /projects/{projectId}/tasks
   */
  list(projectId: string) {
    return api.get<Task[]>(`/projects/${projectId}/tasks`)
  },

  /**
   * 获取任务详情
   * GET /tasks/{taskId}
   */
  detail(taskId: string) {
    return api.get<Task>(`/tasks/${taskId}`)
  },

  /**
   * 取消任务
   * POST /tasks/{taskId}/cancel
   */
  cancel(taskId: string) {
    return api.post<void>(`/tasks/${taskId}/cancel`)
  },

  /**
   * 重试任务
   * POST /tasks/{taskId}/retry
   */
  retry(taskId: string) {
    return api.post<{ task_id: string }>(`/tasks/${taskId}/retry`)
  },
}

// 默认导出
export default tasksApi
