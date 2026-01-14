/**
 * 认证相关组合式函数
 * 
 * 提供登录、注册、登出等认证操作
 * 以及用户状态的响应式访问
 */
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore, useProjectStore, useSubscriptionStore } from '@/stores'

export function useAuth() {
  const router = useRouter()
  const route = useRoute()
  const userStore = useUserStore()
  const projectStore = useProjectStore()
  const subscriptionStore = useSubscriptionStore()
  
  // ==================== 状态 ====================
  
  /** 是否已登录 */
  const isLoggedIn = computed(() => userStore.isLoggedIn)
  
  /** 当前用户 */
  const user = computed(() => userStore.user)
  
  /** 用户显示名称 */
  const displayName = computed(() => userStore.displayName)
  
  /** 用户头像 */
  const avatarUrl = computed(() => userStore.avatarUrl)
  
  /** 是否是管理员 */
  const isAdmin = computed(() => userStore.isAdmin)
  
  /** 是否初始化中 */
  const initializing = computed(() => userStore.initializing)
  
  // ==================== 方法 ====================
  
  /**
   * 登录
   */
  async function login(email: string, password: string): Promise<boolean> {
    try {
      await userStore.doLogin({ email, password })
      
      ElMessage.success('登录成功')
      
      // 初始化订阅状态
      subscriptionStore.init()
      
      // 跳转到之前的页面或工作台
      const redirect = route.query.redirect as string
      await router.push(redirect || '/dashboard')
      
      return true
    } catch (error) {
      const err = error as Error
      ElMessage.error(err.message || '登录失败，请检查邮箱和密码')
      return false
    }
  }
  
  /**
   * 注册
   */
  async function register(email: string, password: string, nickname?: string): Promise<boolean> {
    try {
      await userStore.doRegister({ email, password, nickname })
      
      ElMessage.success('注册成功')
      
      // 初始化订阅状态
      subscriptionStore.init()
      
      // 跳转到工作台
      await router.push('/dashboard')
      
      return true
    } catch (error) {
      const err = error as Error
      ElMessage.error(err.message || '注册失败，请稍后重试')
      return false
    }
  }
  
  /**
   * 登出
   */
  async function logout() {
    // 清除所有状态
    userStore.logout()
    projectStore.reset()
    subscriptionStore.reset()
    
    ElMessage.success('已退出登录')
    
    // 跳转到登录页
    await router.push('/login')
  }
  
  /**
   * 检查登录状态
   * 如果未登录，跳转到登录页
   */
  function requireAuth(): boolean {
    if (!isLoggedIn.value) {
      router.push({
        name: 'Login',
        query: { redirect: route.fullPath },
      })
      return false
    }
    return true
  }
  
  /**
   * 刷新用户信息
   */
  async function refreshUser() {
    await userStore.fetchUser()
  }
  
  return {
    // 状态
    isLoggedIn,
    user,
    displayName,
    avatarUrl,
    isAdmin,
    initializing,
    
    // 方法
    login,
    register,
    logout,
    requireAuth,
    refreshUser,
  }
}
