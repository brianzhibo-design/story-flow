<template>
  <div class="payment-result-page">
    <el-card class="result-card" shadow="never">
      <!-- 成功状态 -->
      <template v-if="status === 'success'">
        <div class="result-icon success">
          <el-icon :size="64"><CircleCheckFilled /></el-icon>
        </div>
        <h1 class="result-title">支付成功！</h1>
        <p class="result-message">
          感谢您的订阅，您现在可以使用 {{ planName }} 的全部功能。
        </p>
        
        <div class="order-summary" v-if="orderInfo">
          <div class="summary-row">
            <span class="label">订单号</span>
            <span class="value">{{ orderInfo.order_no }}</span>
          </div>
          <div class="summary-row">
            <span class="label">订阅计划</span>
            <span class="value">{{ planName }}</span>
          </div>
          <div class="summary-row">
            <span class="label">支付金额</span>
            <span class="value">¥{{ orderInfo.amount }}</span>
          </div>
          <div class="summary-row">
            <span class="label">支付时间</span>
            <span class="value">{{ formatDate(orderInfo.paid_at) }}</span>
          </div>
        </div>
        
        <div class="result-actions">
          <el-button type="primary" size="large" @click="goToDashboard">
            开始创作
          </el-button>
          <el-button size="large" @click="goToSubscription">
            管理订阅
          </el-button>
        </div>
      </template>
      
      <!-- 过期状态 -->
      <template v-else-if="status === 'expired'">
        <div class="result-icon warning">
          <el-icon :size="64"><WarningFilled /></el-icon>
        </div>
        <h1 class="result-title">订单已过期</h1>
        <p class="result-message">
          支付超时，订单已自动取消。您可以返回重新下单。
        </p>
        
        <div class="result-actions">
          <el-button type="primary" size="large" @click="goToPricing">
            重新选择计划
          </el-button>
          <el-button size="large" @click="goToDashboard">
            返回首页
          </el-button>
        </div>
      </template>
      
      <!-- 失败状态 -->
      <template v-else>
        <div class="result-icon error">
          <el-icon :size="64"><CircleCloseFilled /></el-icon>
        </div>
        <h1 class="result-title">支付失败</h1>
        <p class="result-message">
          {{ errorMessage || '支付过程中出现问题，请稍后重试。' }}
        </p>
        
        <div class="result-actions">
          <el-button type="primary" size="large" @click="goToPricing">
            重新支付
          </el-button>
          <el-button size="large" @click="contactSupport">
            联系客服
          </el-button>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  CircleCheckFilled, 
  WarningFilled, 
  CircleCloseFilled 
} from '@element-plus/icons-vue'
import { paymentApi, type OrderStatus } from '@/api/payment'

// Props
const props = defineProps<{
  status?: 'success' | 'expired' | 'failed'
}>()

const route = useRoute()
const router = useRouter()

// 状态
const status = computed(() => props.status || (route.name as string)?.includes('Success') ? 'success' : 
                            (route.name as string)?.includes('Expired') ? 'expired' : 'failed')
const orderInfo = ref<OrderStatus | null>(null)
const errorMessage = ref('')

// 计划名称
const planNames: Record<string, string> = {
  basic: '基础版',
  pro: '专业版',
  enterprise: '企业版'
}
const planName = computed(() => {
  if (orderInfo.value) {
    return planNames[orderInfo.value.plan_type] || orderInfo.value.plan_type
  }
  return '订阅计划'
})

// 加载订单信息
onMounted(async () => {
  const orderNo = route.query.order as string
  if (orderNo && status.value === 'success') {
    try {
      const res = await paymentApi.queryOrder(orderNo)
      orderInfo.value = res.data.data
    } catch (error) {
      console.error('Failed to load order:', error)
    }
  }
})

// 格式化日期
function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 导航
function goToDashboard() {
  router.push('/dashboard')
}

function goToSubscription() {
  router.push('/subscription')
}

function goToPricing() {
  router.push('/pricing')
}

function contactSupport() {
  window.open('mailto:support@storyflow.com', '_blank')
}
</script>

<style scoped>
.payment-result-page {
  min-height: 100vh;
  background: var(--el-fill-color-lighter);
  padding: 80px 24px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.result-card {
  width: 100%;
  max-width: 480px;
  border-radius: 16px;
  text-align: center;
  padding: 40px 32px;
}

.result-icon {
  margin-bottom: 24px;
}

.result-icon.success {
  color: var(--el-color-success);
}

.result-icon.warning {
  color: var(--el-color-warning);
}

.result-icon.error {
  color: var(--el-color-danger);
}

.result-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 16px;
}

.result-message {
  font-size: 16px;
  color: var(--el-text-color-secondary);
  margin: 0 0 32px;
  line-height: 1.6;
}

.order-summary {
  background: var(--el-fill-color-light);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 32px;
  text-align: left;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.summary-row:not(:last-child) {
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.summary-row .label {
  color: var(--el-text-color-secondary);
}

.summary-row .value {
  font-weight: 500;
}

.result-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-actions .el-button {
  width: 100%;
}
</style>

