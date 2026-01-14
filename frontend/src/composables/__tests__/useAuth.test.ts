/**
 * useAuth Composable 单元测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuth } from '@/composables/useAuth'
import { useUserStore } from '@/stores/user'
import { createMockUser } from '@/test'

// Mock vue-router
const mockPush = vi.fn()
const mockCurrentRoute = { value: { query: {} } }

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush,
    currentRoute: mockCurrentRoute,
  }),
}))

// Mock Element Plus
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

import { ElMessage } from 'element-plus'

describe('useAuth', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mockCurrentRoute.value.query = {}
  })

  describe('isLoggedIn', () => {
    it('未登录时应该返回 false', () => {
      const { isLoggedIn } = useAuth()
      expect(isLoggedIn.value).toBe(false)
    })

    it('登录后应该返回 true', () => {
      const userStore = useUserStore()
      userStore.token = 'test-token'

      const { isLoggedIn } = useAuth()
      expect(isLoggedIn.value).toBe(true)
    })
  })

  describe('user', () => {
    it('应该返回当前用户', () => {
      const userStore = useUserStore()
      const mockUser = createMockUser()
      userStore.user = mockUser

      const { user } = useAuth()
      expect(user.value).toEqual(mockUser)
    })
  })

  describe('login', () => {
    it('登录成功后应该跳转到工作台', async () => {
      const userStore = useUserStore()
      vi.spyOn(userStore, 'doLogin').mockResolvedValueOnce(createMockUser())

      const { login } = useAuth()
      await login('test@example.com', 'password123')

      expect(ElMessage.success).toHaveBeenCalledWith('登录成功')
      expect(mockPush).toHaveBeenCalledWith('/dashboard')
    })

    it('有 redirect 参数时应该跳转到该页面', async () => {
      const userStore = useUserStore()
      vi.spyOn(userStore, 'doLogin').mockResolvedValueOnce(createMockUser())
      mockCurrentRoute.value.query = { redirect: '/projects/123' }

      const { login } = useAuth()
      await login('test@example.com', 'password123')

      expect(mockPush).toHaveBeenCalledWith('/projects/123')
    })

    it('登录失败时应该显示错误消息', async () => {
      const userStore = useUserStore()
      vi.spyOn(userStore, 'doLogin').mockRejectedValueOnce(new Error('Invalid credentials'))

      const { login } = useAuth()

      await expect(login('wrong@example.com', 'wrong')).rejects.toThrow()
      expect(ElMessage.error).toHaveBeenCalled()
    })
  })

  describe('register', () => {
    it('注册成功后应该跳转到工作台', async () => {
      const userStore = useUserStore()
      vi.spyOn(userStore, 'doRegister').mockResolvedValueOnce(createMockUser())

      const { register } = useAuth()
      await register('new@example.com', 'password123', 'Test User')

      expect(ElMessage.success).toHaveBeenCalledWith('注册成功')
      expect(mockPush).toHaveBeenCalledWith('/dashboard')
    })

    it('注册失败时应该显示错误消息', async () => {
      const userStore = useUserStore()
      vi.spyOn(userStore, 'doRegister').mockRejectedValueOnce(new Error('Email already exists'))

      const { register } = useAuth()

      await expect(register('existing@example.com', 'password123')).rejects.toThrow()
      expect(ElMessage.error).toHaveBeenCalled()
    })
  })

  describe('logout', () => {
    it('登出后应该跳转到登录页', () => {
      const userStore = useUserStore()
      userStore.user = createMockUser()
      userStore.token = 'test-token'

      const { logout } = useAuth()
      logout()

      expect(userStore.user).toBeNull()
      expect(ElMessage.success).toHaveBeenCalledWith('已退出登录')
      expect(mockPush).toHaveBeenCalledWith('/login')
    })
  })
})

