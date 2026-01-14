<template>
  <div 
    class="plan-card" 
    :class="{ 
      'is-popular': isPopular, 
      'is-current': isCurrent,
      'is-enterprise': plan.type === 'enterprise'
    }"
  >
    <!-- 热门标签 -->
    <div v-if="isPopular" class="popular-badge">
      <span>最受欢迎</span>
    </div>
    
    <!-- 计划信息 -->
    <div class="plan-header">
      <h3 class="plan-name">{{ plan.name }}</h3>
      <p class="plan-description">{{ planDescriptions[plan.type] }}</p>
    </div>
    
    <!-- 价格 -->
    <div class="plan-price">
      <template v-if="plan.type === 'enterprise'">
        <span class="price-text">联系销售</span>
      </template>
      <template v-else-if="plan.type === 'free'">
        <span class="price-amount">¥0</span>
        <span class="price-period">永久免费</span>
      </template>
      <template v-else>
        <span class="price-amount">¥{{ displayPrice }}</span>
        <span class="price-period">/{{ billingCycle === 'yearly' ? '年' : '月' }}</span>
        <div v-if="billingCycle === 'yearly' && originalPrice > displayPrice" class="price-savings">
          <span class="original-price">¥{{ originalPrice }}</span>
          <el-tag size="small" type="success">省 ¥{{ originalPrice - displayPrice }}</el-tag>
        </div>
      </template>
    </div>
    
    <!-- 配额列表 -->
    <ul class="plan-limits">
      <li v-for="item in limitItems" :key="item.label">
        <el-icon><Check /></el-icon>
        <span>{{ item.label }}: <strong>{{ item.value }}</strong></span>
      </li>
    </ul>
    
    <!-- 功能列表 -->
    <ul class="plan-features">
      <li v-for="feature in featureItems" :key="feature.label" :class="{ disabled: !feature.enabled }">
        <el-icon v-if="feature.enabled" color="#67C23A"><Check /></el-icon>
        <el-icon v-else color="#C0C4CC"><Close /></el-icon>
        <span>{{ feature.label }}</span>
      </li>
    </ul>
    
    <!-- 操作按钮 -->
    <div class="plan-action">
      <el-button 
        v-if="isCurrent" 
        disabled 
        size="large"
      >
        当前计划
      </el-button>
      <el-button 
        v-else-if="plan.type === 'enterprise'" 
        type="primary" 
        size="large"
        @click="handleContact"
      >
        联系销售
      </el-button>
      <el-button 
        v-else-if="plan.type === 'free'" 
        size="large"
        @click="handleSelect"
      >
        免费使用
      </el-button>
      <el-button 
        v-else 
        :type="isPopular ? 'primary' : 'default'" 
        size="large"
        @click="handleSelect"
      >
        {{ isUpgrade ? '升级到此计划' : '选择此计划' }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Check, Close } from '@element-plus/icons-vue'
import type { SubscriptionPlan } from '@/api/subscription'

const props = defineProps<{
  plan: SubscriptionPlan
  billingCycle: 'monthly' | 'yearly'
  isCurrent?: boolean
  isPopular?: boolean
  currentPlanType?: string
}>()

const emit = defineEmits<{
  select: [planType: string]
  contact: []
}>()

// 计划描述
const planDescriptions: Record<string, string> = {
  free: '适合个人体验',
  basic: '适合内容创作者',
  pro: '适合专业团队',
  enterprise: '适合大型企业'
}

// 价格计算
const displayPrice = computed(() => {
  if (props.billingCycle === 'yearly') {
    return props.plan.price_yearly
  }
  return props.plan.price_monthly
})

const originalPrice = computed(() => {
  return props.plan.price_monthly * 12
})

// 是否为升级
const isUpgrade = computed(() => {
  if (!props.currentPlanType) return false
  const order = ['free', 'basic', 'pro', 'enterprise']
  return order.indexOf(props.plan.type) > order.indexOf(props.currentPlanType)
})

// 配额项
const limitItems = computed(() => {
  const limits = props.plan.limits
  return [
    { label: '项目数量', value: formatLimit(limits.projects) },
    { label: '每项目分镜', value: formatLimit(limits.scenes_per_project) },
    { label: '图片生成/月', value: formatLimit(limits.image_count) },
    { label: '视频生成/月', value: formatLimit(limits.video_count) },
    { label: '存储空间', value: limits.storage_gb === -1 ? '无限' : `${limits.storage_gb} GB` }
  ]
})

// 功能项
const featureItems = computed(() => {
  const features = props.plan.features
  return [
    { label: '高清导出', enabled: features.can_export_hd },
    { label: '去水印', enabled: features.can_remove_watermark },
    { label: '高级音色', enabled: features.can_use_premium_voices },
    { label: '团队协作', enabled: features.can_collaborate },
    { label: '优先队列', enabled: features.priority_queue },
    { label: 'API 访问', enabled: features.api_access }
  ]
})

// 格式化限制值
function formatLimit(value: number): string {
  if (value === -1) return '无限'
  if (value >= 1000) return `${value / 1000}K`
  return String(value)
}

// 事件处理
function handleSelect() {
  emit('select', props.plan.type)
}

function handleContact() {
  emit('contact')
}
</script>

<style scoped>
.plan-card {
  position: relative;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 16px;
  padding: 32px 24px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.plan-card:hover {
  border-color: var(--el-color-primary-light-5);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transform: translateY(-4px);
}

.plan-card.is-popular {
  border-color: var(--el-color-primary);
  box-shadow: 0 8px 32px rgba(var(--el-color-primary-rgb), 0.15);
}

.plan-card.is-current {
  border-color: var(--el-color-success);
}

.plan-card.is-enterprise {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.plan-card.is-enterprise .plan-limits li,
.plan-card.is-enterprise .plan-features li {
  color: rgba(255, 255, 255, 0.9);
}

.popular-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, var(--el-color-primary) 0%, var(--el-color-primary-light-3) 100%);
  color: white;
  padding: 4px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.plan-header {
  text-align: center;
  margin-bottom: 24px;
}

.plan-name {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px;
}

.plan-description {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin: 0;
}

.plan-card.is-enterprise .plan-description {
  color: rgba(255, 255, 255, 0.8);
}

.plan-price {
  text-align: center;
  margin-bottom: 24px;
  min-height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.price-text {
  font-size: 28px;
  font-weight: 700;
}

.price-amount {
  font-size: 48px;
  font-weight: 800;
  line-height: 1;
}

.price-period {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-left: 4px;
}

.plan-card.is-enterprise .price-period {
  color: rgba(255, 255, 255, 0.8);
}

.price-savings {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.original-price {
  text-decoration: line-through;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.plan-limits,
.plan-features {
  list-style: none;
  padding: 0;
  margin: 0 0 16px;
}

.plan-limits li,
.plan-features li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.plan-features li.disabled {
  color: var(--el-text-color-placeholder);
}

.plan-limits {
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding-bottom: 16px;
}

.plan-action {
  margin-top: auto;
  padding-top: 24px;
}

.plan-action .el-button {
  width: 100%;
}
</style>

