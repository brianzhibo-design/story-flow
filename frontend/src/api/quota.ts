/**
 * 配额 API 模块
 * 
 * 适配后端 RESTful API
 */
import api from '@/utils/request'

// ==================== 类型定义 ====================

export interface Quota {
  plan: string
  credits: {
    used: number
    total: number
    remaining: number
  }
  daily_usage: Record<string, number>
  limits: Record<string, number>
  reset_at: string | null
}

export interface Plan {
  id: string
  name: string
  limits: Record<string, number>
  price: number
}

// ==================== API 方法 ====================

export const quotaApi = {
  /**
   * 获取配额状态
   * GET /quota/status
   */
  status() {
    return api.get<Quota>('/quota/status')
  },

  /**
   * 获取可用计划列表
   * GET /quota/plans
   */
  getPlans() {
    return api.get<Plan[]>('/quota/plans')
  },

  /**
   * 升级计划
   * POST /quota/upgrade/{planId}
   */
  upgradePlan(planId: string) {
    return api.post<void>(`/quota/upgrade/${planId}`)
  },
}

// 默认导出
export default quotaApi
