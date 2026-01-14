/**
 * 认证 API 模块
 * 
 * 适配后端 RESTful API
 */
import api from '@/utils/request'

// ==================== 类型定义 ====================

export interface LoginParams {
  email: string
  password: string
}

export interface RegisterParams {
  email: string
  password: string
  nickname?: string
}

export interface User {
  id: string
  email: string
  nickname: string | null
  avatar_url: string | null
  role: string
  status: string
  created_at: string
}

export interface AuthResponse {
  user: User
  tokens: {
    access_token: string
    refresh_token: string
    token_type: string
    expires_in: number
  }
}

export interface ChangePasswordParams {
  old_password: string
  new_password: string
}

export interface UpdateProfileParams {
  nickname?: string
  avatar_url?: string
}

// ==================== API 方法 ====================

export const authApi = {
  /**
   * 用户登录
   * POST /auth/login
   */
  login(params: LoginParams) {
    return api.post<AuthResponse>('/auth/login', params)
  },

  /**
   * 用户注册
   * POST /auth/register
   */
  register(params: RegisterParams) {
    return api.post<AuthResponse>('/auth/register', params)
  },

  /**
   * 用户登出
   * POST /auth/logout (如果存在)
   */
  async logout() {
    try {
      await api.post<void>('/auth/logout')
    } catch {
      // 登出接口可能不存在，忽略错误
    }
  },

  /**
   * 刷新 Token
   * POST /auth/refresh
   */
  refresh(refreshToken: string) {
    return api.post<{ access_token: string; refresh_token: string }>('/auth/refresh', {
      refresh_token: refreshToken,
    })
  },

  /**
   * 获取当前用户信息
   * GET /auth/me
   */
  me() {
    return api.get<User>('/auth/me')
  },

  /**
   * 修改密码
   * POST /auth/change-password (如果存在)
   */
  changePassword(params: ChangePasswordParams) {
    return api.post<void>('/auth/change-password', params)
  },

  /**
   * 更新个人信息
   * PUT /auth/profile (如果存在)
   */
  updateProfile(params: UpdateProfileParams) {
    return api.put<User>('/auth/profile', params)
  },
}

// 默认导出
export default authApi
