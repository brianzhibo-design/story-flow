/**
 * 项目 API 模块
 * 
 * 适配后端 RESTful API
 */
import api, { type PaginatedData } from '@/utils/request'

// ==================== 类型定义 ====================

export interface Project {
  id: string
  title: string
  description: string | null
  story_text: string
  status: 'draft' | 'processing' | 'completed' | 'failed'
  scene_count: number
  total_duration: number
  thumbnail_url: string | null
  final_video_url: string | null
  created_at: string
  updated_at: string
}

export interface Scene {
  id: string
  project_id: string
  scene_index: number
  text: string
  scene_description: string | null
  characters: string[]
  props: string[]
  camera_type: string | null
  mood: string | null
  image_prompt: string | null
  negative_prompt: string | null
  image_url: string | null
  video_url: string | null
  duration: number | null
  status: 'pending' | 'generating' | 'completed' | 'failed'
}

export interface CreateProjectParams {
  title: string
  story_text: string
  description?: string
}

export interface UpdateProjectParams {
  title?: string
  story_text?: string
  description?: string
}

export interface ListProjectsParams {
  page?: number
  page_size?: number
  status?: string
  keyword?: string
}

export interface UpdateSceneParams {
  text?: string
  scene_description?: string
  image_prompt?: string
  negative_prompt?: string
  camera_type?: string
  mood?: string
  duration?: number
}

// ==================== API 方法 ====================

export const projectsApi = {
  /**
   * 获取项目列表
   * GET /projects
   */
  list(params?: ListProjectsParams): Promise<PaginatedData<Project>> {
    return api.paginate<Project>('/projects', params)
  },

  /**
   * 获取项目详情
   * GET /projects/{id}
   */
  detail(id: string) {
    return api.get<Project & { scenes: Scene[] }>(`/projects/${id}`)
  },

  /**
   * 创建项目
   * POST /projects
   */
  create(params: CreateProjectParams) {
    return api.post<Project>('/projects', params)
  },

  /**
   * 更新项目
   * PUT /projects/{id}
   */
  update(id: string, params: UpdateProjectParams) {
    return api.put<Project>(`/projects/${id}`, params)
  },

  /**
   * 删除项目
   * DELETE /projects/{id}
   */
  delete(id: string) {
    return api.delete<void>(`/projects/${id}`)
  },

  /**
   * 生成项目内容
   * POST /projects/{id}/generate
   */
  generate(id: string, steps?: string[]) {
    return api.post<{ task_id: string; task_ids?: string[] }>(`/projects/${id}/generate`, { steps })
  },

  /**
   * 获取项目分镜列表
   * GET /projects/{id}/scenes (如果存在) 或从 detail 中获取
   */
  async getScenes(projectId: string): Promise<Scene[]> {
    try {
      // 尝试直接获取分镜列表
      return await api.get<Scene[]>(`/projects/${projectId}/scenes`)
    } catch {
      // 如果接口不存在，从项目详情中获取
      const project = await this.detail(projectId)
      return project.scenes || []
    }
  },

  /**
   * 更新分镜
   * PUT /scenes/{id}
   */
  updateScene(sceneId: string, params: UpdateSceneParams) {
    return api.put<Scene>(`/scenes/${sceneId}`, params)
  },

  /**
   * 重排分镜顺序
   * POST /projects/{id}/scenes/reorder
   */
  reorderScenes(projectId: string, sceneIds: string[]) {
    return api.post<void>(`/projects/${projectId}/scenes/reorder`, { scene_ids: sceneIds })
  },

  /**
   * 重新生成分镜图片
   * POST /scenes/{id}/regenerate-image
   */
  regenerateImage(sceneId: string) {
    return api.post<{ task_id: string }>(`/scenes/${sceneId}/regenerate-image`)
  },

  /**
   * 重新生成分镜视频
   * POST /scenes/{id}/regenerate-video
   */
  regenerateVideo(sceneId: string) {
    return api.post<{ task_id: string }>(`/scenes/${sceneId}/regenerate-video`)
  },
}

// 默认导出
export default projectsApi
