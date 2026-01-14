/**
 * 订阅 API 模块
 * 
 * 适配后端 RESTful API
 */
import api from '@/utils/request'

// ==================== 类型定义 ====================

export interface SubscriptionPlan {
  type: string
  name: string
  description?: string
  price_monthly: number
  price_yearly: number
  projects_limit: number
  scenes_per_project: number
  storage_gb: number
  llm_tokens: number
  image_count: number
  video_count: number
  video_duration: number
  tts_chars: number
  can_export_hd: boolean
  can_remove_watermark: boolean
  can_use_premium_voices: boolean
  can_collaborate: boolean
  priority_queue: boolean
  api_access: boolean
}

export interface UserSubscription {
  plan: {
    type: string
    name: string
  }
  subscription: {
    status: string
    billing_cycle: string | null
    current_period_start: string | null
    current_period_end: string | null
    auto_renew: boolean
  } | null
  limits: {
    projects: number
    scenes_per_project: number
    storage_gb: number
    llm_tokens: number
    image_count: number
    video_count: number
    video_duration: number
    tts_chars: number
  }
  features: {
    can_export_hd: boolean
    can_remove_watermark: boolean
    can_use_premium_voices: boolean
    can_collaborate: boolean
    priority_queue: boolean
    api_access: boolean
  }
}

export interface UsageSummary {
  [key: string]: {
    used: number
    limit: number
    remaining: number
    percentage: number
  }
}

export interface SubscribeParams {
  plan_type: string
  billing_cycle: 'monthly' | 'yearly'
}

export interface CheckQuotaResult {
  allowed: boolean
  remaining: number
  limit: number
  used: number
}

// ==================== API 方法 ====================

export const subscriptionApi = {
  /**
   * 获取所有订阅计划
   * GET /subscription/plans
   */
  plans() {
    return api.get<{ plans: SubscriptionPlan[] }>('/subscription/plans')
      .then(res => res.plans || [])
  },

  /**
   * 获取当前用户订阅
   * GET /subscription/current
   */
  getCurrent() {
    return api.get<UserSubscription>('/subscription/current')
  },

  /**
   * 订阅计划
   * POST /subscription/subscribe
   */
  subscribe(params: SubscribeParams) {
    return api.post<{ subscription_id: string; plan_type: string; period_end: string }>(
      '/subscription/subscribe',
      params
    )
  },

  /**
   * 取消订阅
   * POST /subscription/cancel
   */
  cancel(reason?: string) {
    return api.post<{ cancelled_at: string; valid_until: string }>(
      '/subscription/cancel',
      { reason }
    )
  },

  /**
   * 获取使用量统计
   * GET /subscription/usage
   */
  getUsage() {
    return api.get<UsageSummary>('/subscription/usage')
  },

  /**
   * 检查配额
   * GET /subscription/check/{usageType}
   */
  checkQuota(usageType: string, amount: number = 1) {
    return api.get<CheckQuotaResult>(`/subscription/check/${usageType}`, { amount })
  },

  /**
   * 获取使用记录
   * GET /subscription/usage/history
   */
  getUsageHistory(usageType?: string, limit: number = 50) {
    return api.get<{ records: Array<{
      id: string
      type: string
      amount: number
      unit: string
      cost: number
      project_id: string | null
      recorded_at: string
    }> }>('/subscription/usage/history', { usage_type: usageType, limit })
  },
}

// 默认导出
export default subscriptionApi
