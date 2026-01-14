/**
 * User Store 单元测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/stores/user'
import { createMockUser, resetAllMocks } from '@/test'

// Mock API 模块
vi.mock('@/api', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    me: vi.fn(),
    logout: vi.fn(),
    changePassword: vi.fn(),
    updateProfile: vi.fn(),
  },
  quotaApi: {
    status: vi.fn(),
  },
}))

import { authApi, quotaApi } from '@/api'

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    resetAllMocks()
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('初始状态', () => {
    it('应该有正确的初始状态', () => {
      const store = useUserStore()

      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.isLoggedIn).toBe(false)
      expect(store.isAdmin).toBe(false)
    })
  })

  describe('doLogin', () => {
    it('应该成功登录并保存用户信息', async () => {
      const store = useUserStore()
      const mockUser = createMockUser({ email: 'test@example.com' })

      vi.mocked(authApi.login).mockResolvedValueOnce({
        user: mockUser,
        tokens: {
          access_token: 'test-token',
          refresh_token: 'test-refresh-token',
          token_type: 'bearer',
          expires_in: 3600,
        },
      })

      vi.mocked(quotaApi.status).mockResolvedValueOnce({
        plan: 'free',
        credits: { used: 0, total: 100, remaining: 100 },
        daily_usage: {},
        limits: {},
        reset_at: null,
      })

      await store.doLogin({ email: 'test@example.com', password: 'password123' })

      expect(store.user).toEqual(mockUser)
      expect(store.token).toBe('test-token')
      expect(store.isLoggedIn).toBe(true)
    })

    it('登录失败时应该抛出错误', async () => {
      const store = useUserStore()

      vi.mocked(authApi.login).mockRejectedValueOnce(new Error('Invalid credentials'))

      await expect(
        store.doLogin({ email: 'wrong@example.com', password: 'wrong' })
      ).rejects.toThrow()

      expect(store.user).toBeNull()
      expect(store.isLoggedIn).toBe(false)
    })
  })

  describe('doRegister', () => {
    it('应该成功注册并保存用户信息', async () => {
      const store = useUserStore()
      const mockUser = createMockUser({ email: 'new@example.com' })

      vi.mocked(authApi.register).mockResolvedValueOnce({
        user: mockUser,
        tokens: {
          access_token: 'new-token',
          refresh_token: 'new-refresh-token',
          token_type: 'bearer',
          expires_in: 3600,
        },
      })

      vi.mocked(quotaApi.status).mockResolvedValueOnce({
        plan: 'free',
        credits: { used: 0, total: 100, remaining: 100 },
        daily_usage: {},
        limits: {},
        reset_at: null,
      })

      await store.doRegister({ email: 'new@example.com', password: 'password123' })

      expect(store.user).toEqual(mockUser)
      expect(store.token).toBe('new-token')
      expect(store.isLoggedIn).toBe(true)
    })
  })

  describe('fetchUser', () => {
    it('应该获取当前用户信息', async () => {
      const store = useUserStore()
      const mockUser = createMockUser()

      // 先模拟已登录状态
      store.token = 'existing-token'

      vi.mocked(authApi.me).mockResolvedValueOnce(mockUser)

      await store.fetchUser()

      expect(store.user).toEqual(mockUser)
    })

    it('没有 token 时不应该发起请求', async () => {
      const store = useUserStore()

      await store.fetchUser()

      expect(authApi.me).not.toHaveBeenCalled()
    })

    it('获取用户失败时应该清除状态', async () => {
      const store = useUserStore()
      store.token = 'invalid-token'

      vi.mocked(authApi.me).mockRejectedValueOnce(new Error('Unauthorized'))

      await store.fetchUser()

      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.isLoggedIn).toBe(false)
    })
  })

  describe('logout', () => {
    it('应该清除用户状态', async () => {
      const store = useUserStore()

      // 先设置登录状态
      store.user = createMockUser()
      store.token = 'test-token'

      vi.mocked(authApi.logout).mockResolvedValueOnce(undefined)

      await store.logout()

      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.isLoggedIn).toBe(false)
    })
  })

  describe('isAdmin', () => {
    it('管理员用户应该返回 true', () => {
      const store = useUserStore()
      store.user = createMockUser({ role: 'admin' })

      expect(store.isAdmin).toBe(true)
    })

    it('普通用户应该返回 false', () => {
      const store = useUserStore()
      store.user = createMockUser({ role: 'user' })

      expect(store.isAdmin).toBe(false)
    })
  })

  describe('fetchQuota', () => {
    it('应该获取配额信息', async () => {
      const store = useUserStore()
      store.token = 'test-token'

      const mockQuota = {
        plan: 'free',
        credits: { used: 50, total: 100, remaining: 50 },
        daily_usage: {},
        limits: {},
        reset_at: null,
      }

      vi.mocked(quotaApi.status).mockResolvedValueOnce(mockQuota)

      await store.fetchQuota()

      expect(store.quota).toEqual(mockQuota)
    })

    it('没有 token 时不应该发起请求', async () => {
      const store = useUserStore()

      await store.fetchQuota()

      expect(quotaApi.status).not.toHaveBeenCalled()
    })
  })
})
