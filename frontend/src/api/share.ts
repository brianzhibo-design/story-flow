/**
 * 分享协作 API 模块
 * 
 * 适配后端 RESTful API
 */
import api from '@/utils/request'

// ==================== 类型定义 ====================

export interface Share {
  id: string
  share_code: string
  share_type: 'view' | 'comment' | 'edit'
  title: string | null
  has_password: boolean
  expires_at: string | null
  max_views: number | null
  view_count: number
  is_active: boolean
  created_at: string
}

export interface CreateShareParams {
  project_id: string
  share_type?: 'view' | 'comment' | 'edit'
  password?: string
  expires_days?: number
  max_views?: number
  allow_download?: boolean
  title?: string
}

export interface SharedProject {
  project: {
    id: string
    title: string
    style: string
  }
  permissions: {
    type: string
    can_view: boolean
    can_comment: boolean
    can_edit: boolean
    can_download: boolean
  }
}

export interface Collaborator {
  id: string
  user: {
    id: string
    username: string
    email: string
    avatar_url: string | null
  }
  role: string
  is_accepted: boolean
  invited_at: string | null
}

export interface AddCollaboratorParams {
  project_id: string
  email: string
  role?: 'viewer' | 'commenter' | 'editor' | 'admin'
}

export interface Comment {
  id: string
  content: string
  user: {
    id: string
    username: string
    avatar_url: string | null
  }
  scene_id: string | null
  timestamp: number | null
  position_x: number | null
  position_y: number | null
  is_resolved: boolean
  created_at: string
  replies: Comment[]
}

export interface CreateCommentParams {
  content: string
  scene_id?: string
  parent_id?: string
  timestamp?: number
  position_x?: number
  position_y?: number
}

// ==================== API 方法 ====================

export const shareApi = {
  /**
   * 创建分享链接
   * POST /share/create
   */
  create(params: CreateShareParams) {
    return api.post<{
      share_code: string
      share_url: string
      share_type: string
      expires_at: string | null
      has_password: boolean
    }>('/share/create', params)
  },

  /**
   * 获取项目的分享列表
   * GET /share/list/{projectId}
   */
  list(projectId: string) {
    return api.get<{ shares: Share[] }>(`/share/list/${projectId}`)
      .then(res => res.shares || [])
  },

  /**
   * 删除分享
   * DELETE /share/{shareCode}
   */
  delete(shareCode: string) {
    return api.delete<void>(`/share/${shareCode}`)
  },

  /**
   * 访问分享项目
   * GET /share/access/{shareCode}
   */
  access(shareCode: string, password?: string) {
    return api.get<SharedProject>(`/share/access/${shareCode}`, { password })
  },

  // ==================== 协作者 ====================

  /**
   * 添加协作者
   * POST /share/collaborators/add
   */
  addCollaborator(params: AddCollaboratorParams) {
    return api.post<{
      collaborator_id: string
      user_email: string
      role: string
    }>('/share/collaborators/add', params)
  },

  /**
   * 获取协作者列表
   * GET /share/collaborators/{projectId}
   */
  getCollaborators(projectId: string) {
    return api.get<{ collaborators: Collaborator[] }>(`/share/collaborators/${projectId}`)
      .then(res => res.collaborators || [])
  },

  /**
   * 更新协作者权限
   * PUT /share/collaborators/{collaboratorId}
   */
  updateCollaborator(collaboratorId: string, role: string) {
    return api.put<void>(`/share/collaborators/${collaboratorId}`, null, {
      params: { role }
    })
  },

  /**
   * 移除协作者
   * DELETE /share/collaborators/{collaboratorId}
   */
  removeCollaborator(collaboratorId: string) {
    return api.delete<void>(`/share/collaborators/${collaboratorId}`)
  },

  // ==================== 评论 ====================

  /**
   * 创建评论
   * POST /share/comments/{projectId}
   */
  createComment(projectId: string, params: CreateCommentParams) {
    return api.post<{ comment_id: string }>(`/share/comments/${projectId}`, params)
  },

  /**
   * 获取评论列表
   * GET /share/comments/{projectId}
   */
  getComments(projectId: string, sceneId?: string) {
    return api.get<{ comments: Comment[] }>(`/share/comments/${projectId}`, { scene_id: sceneId })
      .then(res => res.comments || [])
  },

  /**
   * 标记评论为已解决
   * PUT /share/comments/{commentId}/resolve
   */
  resolveComment(commentId: string) {
    return api.put<void>(`/share/comments/${commentId}/resolve`)
  },

  /**
   * 删除评论
   * DELETE /share/comments/{commentId}
   */
  deleteComment(commentId: string) {
    return api.delete<void>(`/share/comments/${commentId}`)
  },
}

// 默认导出
export default shareApi
