<template>
  <div class="pricing-page">
    <!-- 页面标题 -->
    <div class="pricing-header">
      <h1 class="title">选择适合你的计划</h1>
      <p class="subtitle">从免费开始，随时升级。所有计划均可 7 天无理由退款。</p>
      
      <!-- 月付/年付切换 -->
      <div class="billing-toggle">
        <span :class="{ active: billingCycle === 'monthly' }">月付</span>
        <el-switch 
          v-model="isYearly" 
          :active-color="'var(--el-color-primary)'"
        />
        <span :class="{ active: billingCycle === 'yearly' }">
          年付 
          <el-tag type="success" size="small" effect="dark">省 2 个月</el-tag>
        </span>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="5" animated />
    </div>
    
    <!-- 计划卡片 -->
    <div v-else class="plans-grid">
      <PlanCard
        v-for="plan in plans"
        :key="plan.type"
        :plan="plan"
        :billing-cycle="billingCycle"
        :is-current="currentPlan?.type === plan.type"
        :is-popular="plan.type === 'pro'"
        :current-plan-type="currentPlan?.type"
        @select="handleSelectPlan"
        @contact="handleContactSales"
      />
    </div>
    
    <!-- 功能对比表 -->
    <div class="feature-comparison">
      <h2 class="section-title">功能对比</h2>
      <el-table 
        :data="featureRows" 
        stripe 
        :header-cell-style="{ background: 'var(--el-fill-color-light)' }"
      >
        <el-table-column prop="feature" label="功能" width="200" fixed />
        <el-table-column 
          v-for="plan in plans" 
          :key="plan.type"
          :label="plan.name"
          align="center"
          min-width="120"
        >
          <template #default="{ row }">
            <el-icon v-if="row[plan.type] === true" color="#67C23A" :size="20">
              <Check />
            </el-icon>
            <el-icon v-else-if="row[plan.type] === false" color="#C0C4CC" :size="20">
              <Close />
            </el-icon>
            <span v-else class="feature-value">{{ row[plan.type] }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- FAQ -->
    <div class="faq-section">
      <h2 class="section-title">常见问题</h2>
      <el-collapse accordion>
        <el-collapse-item title="可以随时升级或降级吗？" name="1">
          <p>是的，您可以随时升级到更高级的计划。升级后立即生效，费用按比例计算。降级将在当前计费周期结束后生效。</p>
        </el-collapse-item>
        <el-collapse-item title="支持哪些支付方式？" name="2">
          <p>我们支持支付宝和微信支付。企业客户还可以选择银行转账或对公付款。</p>
        </el-collapse-item>
        <el-collapse-item title="配额用完了怎么办？" name="3">
          <p>您可以随时升级计划获得更多配额。配额会在每个计费周期开始时重置。</p>
        </el-collapse-item>
        <el-collapse-item title="如何申请发票？" name="4">
          <p>付费用户可以在订阅管理页面申请电子发票，通常在 3 个工作日内发送到您的邮箱。</p>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Check, Close } from '@element-plus/icons-vue'
import { subscriptionApi, type SubscriptionPlan } from '@/api/subscription'
import PlanCard from '@/components/subscription/PlanCard.vue'

const router = useRouter()

// 状态
const plans = ref<SubscriptionPlan[]>([])
const currentPlan = ref<SubscriptionPlan | null>(null)
const isYearly = ref(false)
const loading = ref(true)

// 计费周期
const billingCycle = computed(() => isYearly.value ? 'yearly' : 'monthly')

// 加载数据
onMounted(async () => {
  try {
    const [plansRes, currentRes] = await Promise.all([
      subscriptionApi.getPlans(),
      subscriptionApi.getCurrent()
    ])
    
    // 按 sort_order 排序
    plans.value = (plansRes.data.data || []).sort((a, b) => a.sort_order - b.sort_order)
    currentPlan.value = currentRes.data.data?.plan || null
  } catch (error) {
    console.error('Failed to load plans:', error)
    // 使用默认计划
    plans.value = getDefaultPlans()
  } finally {
    loading.value = false
  }
})

// 默认计划数据 (后端未返回时使用)
function getDefaultPlans(): SubscriptionPlan[] {
  return [
    {
      id: '1', name: '免费版', type: 'free', description: '适合个人体验',
      price_monthly: 0, price_yearly: 0,
      limits: { projects: 3, scenes_per_project: 10, storage_gb: 0.5, llm_tokens: 50000, image_count: 20, video_count: 5, video_duration: 25, tts_chars: 5000 },
      features: { can_export_hd: false, can_remove_watermark: false, can_use_premium_voices: false, can_collaborate: false, priority_queue: false, api_access: false },
      is_active: true, sort_order: 0
    },
    {
      id: '2', name: '基础版', type: 'basic', description: '适合内容创作者',
      price_monthly: 29, price_yearly: 290,
      limits: { projects: 10, scenes_per_project: 30, storage_gb: 5, llm_tokens: 500000, image_count: 200, video_count: 50, video_duration: 250, tts_chars: 50000 },
      features: { can_export_hd: true, can_remove_watermark: false, can_use_premium_voices: false, can_collaborate: false, priority_queue: false, api_access: false },
      is_active: true, sort_order: 1
    },
    {
      id: '3', name: '专业版', type: 'pro', description: '适合专业团队',
      price_monthly: 99, price_yearly: 990,
      limits: { projects: 50, scenes_per_project: 100, storage_gb: 50, llm_tokens: 2000000, image_count: 1000, video_count: 200, video_duration: 1000, tts_chars: 200000 },
      features: { can_export_hd: true, can_remove_watermark: true, can_use_premium_voices: true, can_collaborate: true, priority_queue: true, api_access: false },
      is_active: true, sort_order: 2
    },
    {
      id: '4', name: '企业版', type: 'enterprise', description: '适合大型企业',
      price_monthly: 0, price_yearly: 0,
      limits: { projects: -1, scenes_per_project: -1, storage_gb: 500, llm_tokens: -1, image_count: -1, video_count: -1, video_duration: -1, tts_chars: -1 },
      features: { can_export_hd: true, can_remove_watermark: true, can_use_premium_voices: true, can_collaborate: true, priority_queue: true, api_access: true },
      is_active: true, sort_order: 3
    }
  ]
}

// 功能对比数据
const featureRows = computed(() => [
  { feature: '项目数量', free: '3', basic: '10', pro: '50', enterprise: '无限' },
  { feature: '每项目分镜', free: '10', basic: '30', pro: '100', enterprise: '无限' },
  { feature: '图片生成/月', free: '20', basic: '200', pro: '1000', enterprise: '无限' },
  { feature: '视频生成/月', free: '5', basic: '50', pro: '200', enterprise: '无限' },
  { feature: '存储空间', free: '0.5 GB', basic: '5 GB', pro: '50 GB', enterprise: '500 GB' },
  { feature: '高清导出', free: false, basic: true, pro: true, enterprise: true },
  { feature: '去水印', free: false, basic: false, pro: true, enterprise: true },
  { feature: '高级音色', free: false, basic: false, pro: true, enterprise: true },
  { feature: '团队协作', free: false, basic: false, pro: true, enterprise: true },
  { feature: '优先队列', free: false, basic: false, pro: true, enterprise: true },
  { feature: 'API 访问', free: false, basic: false, pro: false, enterprise: true }
])

// 选择计划
function handleSelectPlan(planType: string) {
  if (planType === 'free') {
    ElMessage.info('您当前使用的是免费版')
    router.push('/dashboard')
  } else {
    router.push({
      path: '/payment',
      query: { plan: planType, cycle: billingCycle.value }
    })
  }
}

// 联系销售
function handleContactSales() {
  window.open('mailto:sales@storyflow.com?subject=企业版咨询', '_blank')
}
</script>

<style scoped>
.pricing-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 24px;
}

.pricing-header {
  text-align: center;
  margin-bottom: 48px;
}

.title {
  font-size: 42px;
  font-weight: 800;
  margin: 0 0 16px;
  background: linear-gradient(135deg, var(--el-color-primary) 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 18px;
  color: var(--el-text-color-secondary);
  margin: 0 0 32px;
}

.billing-toggle {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  background: var(--el-fill-color-light);
  padding: 12px 24px;
  border-radius: 999px;
  font-size: 15px;
}

.billing-toggle span {
  color: var(--el-text-color-secondary);
  transition: color 0.3s;
}

.billing-toggle span.active {
  color: var(--el-color-primary);
  font-weight: 600;
}

.loading-state {
  padding: 40px;
}

.plans-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 80px;
}

@media (max-width: 1024px) {
  .plans-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .plans-grid {
    grid-template-columns: 1fr;
  }
  
  .title {
    font-size: 28px;
  }
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 32px;
}

.feature-comparison {
  margin-bottom: 80px;
}

.feature-value {
  font-weight: 500;
}

.faq-section {
  max-width: 800px;
  margin: 0 auto;
}

.faq-section :deep(.el-collapse-item__header) {
  font-size: 16px;
  font-weight: 500;
}

.faq-section :deep(.el-collapse-item__content) {
  font-size: 15px;
  color: var(--el-text-color-secondary);
  line-height: 1.8;
}
</style>

