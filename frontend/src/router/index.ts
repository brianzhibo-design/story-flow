/**
 * Vue Router 配置
 * 
 * 功能:
 * - 路由定义
 * - 路由守卫（认证、权限）
 * - 页面标题
 * - 异步初始化等待
 */
import { createRouter, createWebHistory, type RouteRecordRaw, type RouteLocationNormalized } from 'vue-router'
import { useUserStore } from '@/stores'
import { storage } from '@/utils/storage'

// ==================== 路由元数据类型 ====================

declare module 'vue-router' {
  interface RouteMeta {
    /** 页面标题 */
    title?: string
    /** 需要登录 */
    requiresAuth?: boolean
    /** 仅游客可访问（已登录用户会跳转） */
    guest?: boolean
    /** 需要的角色 */
    roles?: string[]
    /** 是否缓存组件 */
    keepAlive?: boolean
  }
}

// ==================== 路由定义 ====================

const routes: RouteRecordRaw[] = [
  // ==================== 公开页面 ====================
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' },
  },
  {
    path: '/pricing',
    name: 'Pricing',
    component: () => import('@/views/Pricing.vue'),
    meta: { title: '定价方案' },
  },
  {
    path: '/s/:shareCode',
    name: 'SharedProject',
    component: () => import('@/views/SharedProject.vue'),
    meta: { title: '分享项目' },
  },
  
  // ==================== 认证页面（仅游客） ====================
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册', guest: true },
  },
  
  // ==================== 需要登录的页面 ====================
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '工作台', requiresAuth: true, keepAlive: true },
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('@/views/Projects.vue'),
    meta: { title: '我的项目', requiresAuth: true, keepAlive: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { title: '设置', requiresAuth: true },
  },
  {
    path: '/projects/create',
    name: 'ProjectCreate',
    component: () => import('@/views/ProjectCreate.vue'),
    meta: { title: '创建项目', requiresAuth: true },
  },
  {
    path: '/projects/:id',
    name: 'ProjectEditor',
    component: () => import('@/views/ProjectEditor.vue'),
    meta: { title: '项目编辑', requiresAuth: true },
  },
  {
    path: '/quota',
    name: 'Quota',
    component: () => import('@/views/QuotaPage.vue'),
    meta: { title: '配额管理', requiresAuth: true },
  },
  {
    path: '/subscription',
    name: 'Subscription',
    component: () => import('@/views/Subscription.vue'),
    meta: { title: '订阅管理', requiresAuth: true },
  },
  
  // ==================== 支付相关 ====================
  {
    path: '/payment',
    name: 'Payment',
    component: () => import('@/views/Payment.vue'),
    meta: { title: '支付', requiresAuth: true },
  },
  {
    path: '/payment/success',
    name: 'PaymentSuccess',
    component: () => import('@/views/PaymentResult.vue'),
    props: { status: 'success' },
    meta: { title: '支付成功', requiresAuth: true },
  },
  {
    path: '/payment/expired',
    name: 'PaymentExpired',
    component: () => import('@/views/PaymentResult.vue'),
    props: { status: 'expired' },
    meta: { title: '订单过期', requiresAuth: true },
  },
  
  // ==================== 错误页面 ====================
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面不存在' },
  },
]

// ==================== 创建路由实例 ====================

const router = createRouter({
  history: createWebHistory(),
  routes,
  // 滚动行为
  scrollBehavior(to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    return { top: 0 }
  },
})

// ==================== 路由守卫 ====================

/**
 * 设置页面标题
 */
function setPageTitle(to: RouteLocationNormalized) {
  const title = to.meta.title || 'StoryFlow'
  document.title = `${title} - AI视频创作平台`
}

/**
 * 检查认证状态
 */
async function checkAuth(to: RouteLocationNormalized): Promise<boolean | { name: string; query?: Record<string, string> }> {
  const userStore = useUserStore()
  
  // 如果有 Token 但未初始化，先进行初始化
  if (storage.getToken() && !userStore.initialized) {
    await userStore.init()
  }
  
  // 需要登录的页面
  if (to.meta.requiresAuth) {
    if (!userStore.isLoggedIn) {
      return { 
        name: 'Login', 
        query: { redirect: to.fullPath } 
      }
    }
    
    // 角色检查
    if (to.meta.roles && to.meta.roles.length > 0) {
      const userRole = userStore.user?.role
      if (!userRole || !to.meta.roles.includes(userRole)) {
        return { name: 'Dashboard' } // 无权限，跳转到工作台
      }
    }
  }
  
  // 仅游客可访问的页面（登录/注册）
  if (to.meta.guest && userStore.isLoggedIn) {
    return { name: 'Dashboard' }
  }
  
  return true
}

// 全局前置守卫
router.beforeEach(async (to, _from, next) => {
  // 设置页面标题
  setPageTitle(to)
  
  // 检查认证
  const authResult = await checkAuth(to)
  
  if (authResult === true) {
    next()
  } else {
    next(authResult)
  }
})

// 全局后置守卫 - 可用于分析、错误上报等
router.afterEach((to, from) => {
  // 页面访问统计（如果需要）
  // analytics.trackPageView(to.fullPath)
})

// 路由错误处理
router.onError((error) => {
  console.error('Router error:', error)
  
  // 动态导入失败时的处理（如网络问题）
  if (error.message.includes('Failed to fetch dynamically imported module')) {
    window.location.reload()
  }
})

export default router
