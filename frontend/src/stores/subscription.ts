/**
 * 订阅状态管理
 * 
 * 使用 Pinia 管理用户订阅状态和配额信息
 */
import { defineStore } from 'pinia'
import { subscriptionApi } from '@/api'
import type { SubscriptionPlan, UserSubscription, UsageSummary } from '@/api'

interface SubscriptionState {
  /** 所有订阅计划 */
  plans: SubscriptionPlan[]
  /** 当前用户订阅 */
  currentSubscription: UserSubscription | null
  /** 使用量统计 */
  usage: UsageSummary | null
  /** 加载状态 */
  loading: boolean
  /** 是否已初始化 */
  initialized: boolean
}

export const useSubscriptionStore = defineStore('subscription', {
  state: (): SubscriptionState => ({
    plans: [],
    currentSubscription: null,
    usage: null,
    loading: false,
    initialized: false
  }),
  
  getters: {
    /**
     * 当前计划类型
     */
    planType(): string {
      return this.currentSubscription?.plan?.type || 'free'
    },
    
    /**
     * 当前计划
     */
    currentPlan(): SubscriptionPlan | null {
      if (!this.currentSubscription?.plan) return null
      // 从 plans 列表中找到完整的计划信息
      const planType = this.currentSubscription.plan.type
      return this.plans.find(p => p.type === planType) || null
    },
    
    /**
     * 是否为付费用户
     */
    isPaid(): boolean {
      return ['basic', 'pro', 'enterprise'].includes(this.planType)
    },
    
    /**
     * 是否为专业版或以上
     */
    isPro(): boolean {
      return ['pro', 'enterprise'].includes(this.planType)
    },
    
    /**
     * 是否为企业版
     */
    isEnterprise(): boolean {
      return this.planType === 'enterprise'
    },
    
    /**
     * 订阅是否有效
     */
    isActive(): boolean {
      return this.currentSubscription?.subscription?.status === 'active'
    },
    
    /**
     * 订阅剩余天数
     */
    daysRemaining(): number {
      const endDate = this.currentSubscription?.subscription?.current_period_end
      if (!endDate) return 0
      const end = new Date(endDate)
      const now = new Date()
      return Math.max(0, Math.ceil((end.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)))
    },
    
    /**
     * 检查是否有某功能权限
     */
    hasFeature(): (feature: string) => boolean {
      return (feature: string) => {
        const features = this.currentSubscription?.features
        return features?.[feature as keyof typeof features] || false
      }
    },
    
    /**
     * 获取配额剩余量
     */
    quotaRemaining(): (type: string) => number {
      return (type: string) => {
        if (!this.usage) return 0
        const usageData = this.usage[type]
        if (!usageData) return 0
        if (usageData.limit === -1) return Infinity
        return usageData.remaining || 0
      }
    },
    
    /**
     * 获取配额使用百分比
     */
    quotaPercentage(): (type: string) => number {
      return (type: string) => {
        if (!this.usage) return 0
        const usageData = this.usage[type]
        if (!usageData) return 0
        return usageData.percentage || 0
      }
    }
  },
  
  actions: {
    /**
     * 获取所有订阅计划
     */
    async fetchPlans() {
      try {
        this.plans = await subscriptionApi.plans()
      } catch (error) {
        console.error('Failed to fetch plans:', error)
      }
    },
    
    /**
     * 获取当前用户订阅
     */
    async fetchCurrent() {
      this.loading = true
      try {
        this.currentSubscription = await subscriptionApi.getCurrent()
      } catch (error) {
        console.error('Failed to fetch subscription:', error)
        this.currentSubscription = null
      } finally {
        this.loading = false
      }
    },
    
    /**
     * 获取使用量统计
     */
    async fetchUsage() {
      try {
        this.usage = await subscriptionApi.getUsage()
      } catch (error) {
        console.error('Failed to fetch usage:', error)
      }
    },
    
    /**
     * 取消订阅
     */
    async cancel(reason?: string) {
      await subscriptionApi.cancel(reason)
      await this.fetchCurrent()
    },
    
    /**
     * 检查配额是否足够
     * @param type 使用类型
     * @param amount 需要的数量
     */
    async checkQuota(type: string, amount: number = 1): Promise<boolean> {
      try {
        const result = await subscriptionApi.checkQuota(type, amount)
        return result.allowed
      } catch (error) {
        console.error('Failed to check quota:', error)
        return false
      }
    },
    
    /**
     * 初始化订阅状态
     * 登录后调用此方法
     */
    async init() {
      if (this.initialized) return
      
      this.loading = true
      try {
        await Promise.all([
          this.fetchCurrent(),
          this.fetchUsage()
        ])
        this.initialized = true
      } finally {
        this.loading = false
      }
    },
    
    /**
     * 刷新订阅状态
     */
    async refresh() {
      await Promise.all([
        this.fetchCurrent(),
        this.fetchUsage()
      ])
    },
    
    /**
     * 重置状态
     * 登出时调用
     */
    reset() {
      this.plans = []
      this.currentSubscription = null
      this.usage = null
      this.loading = false
      this.initialized = false
    }
  }
})
