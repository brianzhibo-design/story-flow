/**
 * 用户状态管理
 * 
 * 功能:
 * - 用户认证状态
 * - Token 管理
 * - 用户信息缓存
 * - 配额管理
 * - 异步初始化
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, quotaApi } from '@/api'
import type { User, Quota, LoginParams, RegisterParams } from '@/api'
import { storage } from '@/utils/storage'

export const useUserStore = defineStore('user', () => {
  // ==================== 状态 ====================
  
  /** 当前用户信息 */
  const user = ref<User | null>(null)
  
  /** 用户配额信息 */
  const quota = ref<Quota | null>(null)
  
  /** 访问令牌 */
  const token = ref<string | null>(storage.getToken())
  
  /** 是否已完成初始化 */
  const initialized = ref(false)
  
  /** 初始化中 */
  const initializing = ref(false)
  
  // ==================== 计算属性 ====================
  
  /** 是否已登录 */
  const isLoggedIn = computed(() => !!token.value)
  
  /** 是否是管理员 */
  const isAdmin = computed(() => user.value?.role === 'admin')
  
  /** 用户显示名称 */
  const displayName = computed(() => 
    user.value?.nickname || user.value?.email?.split('@')[0] || '用户'
  )
  
  /** 用户头像 */
  const avatarUrl = computed(() => user.value?.avatar_url)
  
  /** 剩余积分 */
  const remainingCredits = computed(() => quota.value?.credits?.remaining ?? 0)
  
  // ==================== 方法 ====================
  
  /**
   * 登录
   */
  async function doLogin(params: LoginParams) {
    const response = await authApi.login(params)
    
    // 保存 Token
    token.value = response.tokens.access_token
    storage.setToken(response.tokens.access_token)
    storage.setRefreshToken(response.tokens.refresh_token)
    
    // 保存用户信息
    user.value = response.user
    storage.setUser(response.user)
    
    // 获取配额信息
    await fetchQuota()
    
    // 标记已初始化
    initialized.value = true
    
    return response.user
  }
  
  /**
   * 注册
   */
  async function doRegister(params: RegisterParams) {
    const response = await authApi.register(params)
    
    // 保存 Token
    token.value = response.tokens.access_token
    storage.setToken(response.tokens.access_token)
    storage.setRefreshToken(response.tokens.refresh_token)
    
    // 保存用户信息
    user.value = response.user
    storage.setUser(response.user)
    
    // 获取配额信息
    await fetchQuota()
    
    // 标记已初始化
    initialized.value = true
    
    return response.user
  }
  
  /**
   * 获取当前用户信息
   */
  async function fetchUser() {
    if (!token.value) return null
    
    try {
      const userData = await authApi.me()
      user.value = userData
      storage.setUser(userData)
      return userData
    } catch {
      // 获取用户信息失败，可能 Token 已失效
      clearAuth()
      return null
    }
  }
  
  /**
   * 获取用户配额
   */
  async function fetchQuota() {
    if (!token.value) return null
    
    try {
      const quotaData = await quotaApi.status()
      quota.value = quotaData
      return quotaData
    } catch (error) {
      console.error('Failed to fetch quota:', error)
      return null
    }
  }
  
  /**
   * 清除认证信息
   */
  function clearAuth() {
    user.value = null
    quota.value = null
    token.value = null
    storage.clear()
  }
  
  /**
   * 登出
   */
  async function logout() {
    // 调用后端登出接口（可选，忽略错误）
    try {
      await authApi.logout()
    } catch {
      // 忽略登出错误
    }
    
    // 清除本地状态
    clearAuth()
  }
  
  /**
   * 初始化用户状态
   * 
   * 在应用启动时调用，从本地存储恢复状态
   * 如果有 Token，会尝试获取最新用户信息
   */
  async function init() {
    // 避免重复初始化
    if (initialized.value || initializing.value) {
      return
    }
    
    initializing.value = true
    
    try {
      // 从本地存储恢复用户信息（快速显示）
      const savedUser = storage.getUser<User>()
      if (savedUser) {
        user.value = savedUser
      }
      
      // 如果有 Token，尝试获取最新用户信息
      if (token.value) {
        try {
          await Promise.all([
            fetchUser(),
            fetchQuota(),
          ])
        } catch {
          // Token 无效，清除状态
          clearAuth()
        }
      }
    } finally {
      initialized.value = true
      initializing.value = false
    }
  }
  
  /**
   * 等待初始化完成
   * 
   * 用于路由守卫等需要等待初始化的场景
   */
  function waitForInit(): Promise<void> {
    if (initialized.value) {
      return Promise.resolve()
    }
    
    return new Promise((resolve) => {
      const checkInit = () => {
        if (initialized.value) {
          resolve()
        } else {
          setTimeout(checkInit, 50)
        }
      }
      checkInit()
    })
  }
  
  /**
   * 更新用户配额
   */
  function updateQuota(newQuota: Quota) {
    quota.value = newQuota
  }
  
  /**
   * 更新用户信息
   */
  function updateUser(updates: Partial<User>) {
    if (user.value) {
      user.value = { ...user.value, ...updates }
      storage.setUser(user.value)
    }
  }
  
  /**
   * 修改密码
   */
  async function changePassword(oldPassword: string, newPassword: string) {
    await authApi.changePassword({
      old_password: oldPassword,
      new_password: newPassword,
    })
  }
  
  /**
   * 更新个人资料
   */
  async function updateProfile(params: { nickname?: string; avatar_url?: string }) {
    const updatedUser = await authApi.updateProfile(params)
    user.value = updatedUser
    storage.setUser(updatedUser)
    return updatedUser
  }
  
  return {
    // 状态
    user,
    quota,
    token,
    initialized,
    initializing,
    
    // 计算属性
    isLoggedIn,
    isAdmin,
    displayName,
    avatarUrl,
    remainingCredits,
    
    // 方法
    doLogin,
    doRegister,
    fetchUser,
    fetchQuota,
    logout,
    init,
    waitForInit,
    updateQuota,
    updateUser,
    changePassword,
    updateProfile,
  }
})
