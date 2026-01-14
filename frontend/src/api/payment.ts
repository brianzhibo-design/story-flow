/**
 * 支付 API 模块
 * 
 * 适配后端 RESTful API
 */
import api from '@/utils/request'

// ==================== 类型定义 ====================

export interface PaymentMethod {
  id: string
  name: string
  icon: string
  description: string
  enabled: boolean
}

export interface PriceInfo {
  original_price: number
  final_price: number
  discount: number
  saved: number
}

export interface CreateOrderParams {
  plan_type: string
  billing_cycle: 'monthly' | 'yearly'
  payment_method: 'alipay' | 'wechat'
}

export interface Order {
  order_no: string
  amount: number
  pay_url: string
  qr_code?: string
  status?: 'pending' | 'paid' | 'expired' | 'canceled'
}

// ==================== API 方法 ====================

export const paymentApi = {
  /**
   * 获取可用支付方式
   * GET /payment/methods
   */
  methods() {
    return api.get<{ methods: PaymentMethod[] }>('/payment/methods')
      .then(res => res.methods || [])
  },

  /**
   * 获取价格信息
   * GET /payment/price
   */
  getPrice(planType: string, billingCycle: 'monthly' | 'yearly') {
    return api.get<PriceInfo>('/payment/price', { 
      plan_type: planType, 
      billing_cycle: billingCycle 
    })
  },

  /**
   * 创建支付订单
   * POST /payment/create-order
   */
  createOrder(params: CreateOrderParams) {
    return api.post<Order>('/payment/create-order', params)
  },

  /**
   * 查询订单状态
   * GET /payment/order/{orderNo}
   */
  queryOrder(orderNo: string) {
    return api.get<Order>(`/payment/order/${orderNo}`)
  },
}

// 默认导出
export default paymentApi
