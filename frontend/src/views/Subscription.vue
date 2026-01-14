<template>
  <MainLayout title="订阅管理">
    <div class="subscription-page">
      <div class="page-header">
        <h1>订阅管理</h1>
        <p>管理您的订阅计划和查看使用情况</p>
      </div>
    
    <el-row :gutter="24">
      <!-- 当前计划 -->
      <el-col :xs="24" :lg="8">
        <el-card class="plan-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>当前计划</span>
              <el-tag 
                :type="statusTagType" 
                size="small"
              >
                {{ statusText }}
              </el-tag>
            </div>
          </template>
          
          <div v-if="loading" class="loading-state">
            <el-skeleton :rows="4" animated />
          </div>
          
          <div v-else-if="subscription" class="plan-info">
            <h2 class="plan-name">{{ subscription.plan.name }}</h2>
            <p class="plan-price">
              ¥{{ currentPrice }}/{{ subscription.billing_cycle === 'yearly' ? '年' : '月' }}
            </p>
            
            <div class="plan-period">
              <el-icon><Calendar /></el-icon>
              <span>
                {{ formatDate(subscription.current_period_start) }} - 
                {{ formatDate(subscription.current_period_end) }}
              </span>
            </div>
            
            <div class="plan-renew" v-if="subscription.status === 'active'">
              <el-icon><Refresh /></el-icon>
              <span>{{ subscription.auto_renew ? '自动续费已开启' : '自动续费已关闭' }}</span>
            </div>
            
            <el-divider />
            
            <div class="plan-actions">
              <el-button type="primary" @click="handleUpgrade">
                {{ isHighestPlan ? '已是最高计划' : '升级计划' }}
              </el-button>
              <el-button 
                v-if="subscription.status === 'active'" 
                type="text"
                @click="handleCancel"
              >
                取消订阅
              </el-button>
            </div>
          </div>
          
          <div v-else class="no-subscription">
            <el-empty description="暂无订阅" :image-size="80">
              <el-button type="primary" @click="handleUpgrade">选择计划</el-button>
            </el-empty>
          </div>
        </el-card>
        
        <!-- 续费提醒 -->
        <el-alert
          v-if="daysRemaining > 0 && daysRemaining <= 7"
          :title="`订阅将在 ${daysRemaining} 天后到期`"
          type="warning"
          :closable="false"
          class="renew-alert"
        >
          <template #default>
            <el-button size="small" type="primary" @click="handleRenew">
              立即续费
            </el-button>
          </template>
        </el-alert>
      </el-col>
      
      <!-- 使用量统计 -->
      <el-col :xs="24" :lg="16">
        <el-card class="usage-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>本月使用量</span>
              <el-tag size="small" type="info">
                {{ usagePeriod }}
              </el-tag>
            </div>
          </template>
          
          <div v-if="loading" class="loading-state">
            <el-skeleton :rows="6" animated />
          </div>
          
          <div v-else class="usage-grid">
            <UsageBar
              label="LLM Token"
              :used="usageData.llm.used"
              :limit="usageData.llm.limit"
              unit="token"
              icon="ChatDotRound"
            />
            <UsageBar
              label="图片生成"
              :used="usageData.image.used"
              :limit="usageData.image.limit"
              unit="张"
              icon="Picture"
            />
            <UsageBar
              label="视频生成"
              :used="usageData.video.used"
              :limit="usageData.video.limit"
              unit="个"
              icon="VideoCamera"
            />
            <UsageBar
              label="视频时长"
              :used="usageData.video_duration.used"
              :limit="usageData.video_duration.limit"
              unit="秒"
              icon="Timer"
            />
            <UsageBar
              label="语音合成"
              :used="usageData.tts.used"
              :limit="usageData.tts.limit"
              unit="字符"
              icon="Microphone"
            />
            <UsageBar
              label="存储空间"
              :used="usageData.storage.used"
              :limit="usageData.storage.limit"
              unit="GB"
              icon="FolderOpened"
            />
          </div>
        </el-card>
        
        <!-- 功能权限 -->
        <el-card class="features-card" shadow="never">
          <template #header>
            <span>功能权限</span>
          </template>
          
          <div class="features-grid">
            <div 
              v-for="feature in featureList" 
              :key="feature.key"
              class="feature-item"
              :class="{ enabled: feature.enabled }"
            >
              <el-icon v-if="feature.enabled" color="#67C23A"><Check /></el-icon>
              <el-icon v-else color="#C0C4CC"><Close /></el-icon>
              <span>{{ feature.label }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Calendar, Refresh, Check, Close } from '@element-plus/icons-vue'
import { subscriptionApi, type UserSubscription, type UsageSummary } from '@/api/subscription'
import UsageBar from '@/components/subscription/UsageBar.vue'
import MainLayout from '@/components/layout/MainLayout.vue'

const router = useRouter()

// 状态
const loading = ref(true)
const subscription = ref<UserSubscription | null>(null)
const usage = ref<UsageSummary | null>(null)

// 加载数据
onMounted(async () => {
  try {
    const [subRes, usageRes] = await Promise.all([
      subscriptionApi.getCurrent(),
      subscriptionApi.getUsage()
    ])
    subscription.value = subRes.data.data
    usage.value = usageRes.data.data
  } catch (error) {
    console.error('Failed to load subscription:', error)
  } finally {
    loading.value = false
  }
})

// 计算属性
const currentPrice = computed(() => {
  if (!subscription.value) return 0
  const plan = subscription.value.plan
  return subscription.value.billing_cycle === 'yearly' 
    ? plan.price_yearly 
    : plan.price_monthly
})

const statusText = computed(() => {
  const map: Record<string, string> = {
    active: '生效中',
    cancelled: '已取消',
    expired: '已过期',
    trial: '试用中'
  }
  return map[subscription.value?.status || ''] || ''
})

const statusTagType = computed(() => {
  const map: Record<string, string> = {
    active: 'success',
    cancelled: 'warning',
    expired: 'info',
    trial: 'primary'
  }
  return map[subscription.value?.status || ''] || 'info'
})

const daysRemaining = computed(() => {
  if (!subscription.value?.current_period_end) return 0
  const end = new Date(subscription.value.current_period_end)
  const now = new Date()
  return Math.max(0, Math.ceil((end.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)))
})

const isHighestPlan = computed(() => {
  return subscription.value?.plan.type === 'enterprise'
})

const usagePeriod = computed(() => {
  if (!usage.value) return ''
  const start = new Date(usage.value.current_period_start)
  return `${start.getMonth() + 1} 月`
})

// 使用量数据
const usageData = computed(() => {
  const defaultItem = { used: 0, limit: 0 }
  if (!usage.value) {
    return {
      llm: defaultItem,
      image: defaultItem,
      video: defaultItem,
      video_duration: defaultItem,
      tts: defaultItem,
      storage: defaultItem
    }
  }
  
  const limits = usage.value.limits || {}
  const used = usage.value.usage || {}
  
  return {
    llm: { used: used.llm_tokens || 0, limit: limits.llm_tokens || 0 },
    image: { used: used.image_count || 0, limit: limits.image_count || 0 },
    video: { used: used.video_count || 0, limit: limits.video_count || 0 },
    video_duration: { used: used.video_duration || 0, limit: limits.video_duration || 0 },
    tts: { used: used.tts_chars || 0, limit: limits.tts_chars || 0 },
    storage: { used: used.storage_gb || 0, limit: limits.storage_gb || 0 }
  }
})

// 功能列表
const featureList = computed(() => {
  const features = subscription.value?.plan.features || {}
  return [
    { key: 'can_export_hd', label: '高清导出', enabled: features.can_export_hd },
    { key: 'can_remove_watermark', label: '去水印', enabled: features.can_remove_watermark },
    { key: 'can_use_premium_voices', label: '高级音色', enabled: features.can_use_premium_voices },
    { key: 'can_collaborate', label: '团队协作', enabled: features.can_collaborate },
    { key: 'priority_queue', label: '优先队列', enabled: features.priority_queue },
    { key: 'api_access', label: 'API 访问', enabled: features.api_access }
  ]
})

// 格式化日期
function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 事件处理
function handleUpgrade() {
  router.push('/pricing')
}

async function handleCancel() {
  try {
    await ElMessageBox.confirm(
      '确定要取消订阅吗？取消后将在当前计费周期结束后失效，届时将自动切换为免费版。',
      '取消订阅',
      {
        confirmButtonText: '确定取消',
        cancelButtonText: '我再想想',
        type: 'warning'
      }
    )
    
    await subscriptionApi.cancel()
    ElMessage.success('订阅已取消，将在当前周期结束后生效')
    
    // 刷新数据
    const res = await subscriptionApi.getCurrent()
    subscription.value = res.data.data
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消订阅失败')
    }
  }
}

function handleRenew() {
  if (!subscription.value) return
  router.push({
    path: '/payment',
    query: {
      plan: subscription.value.plan.type,
      cycle: subscription.value.billing_cycle
    }
  })
}
</script>

<style scoped>
.subscription-page {
  max-width: 1200px;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px;
}

.page-header p {
  color: var(--el-text-color-secondary);
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plan-card,
.usage-card,
.features-card {
  border-radius: 12px;
  margin-bottom: 24px;
}

.loading-state {
  padding: 20px 0;
}

/* 计划信息 */
.plan-info {
  text-align: center;
}

.plan-name {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px;
  background: linear-gradient(135deg, var(--el-color-primary) 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.plan-price {
  font-size: 16px;
  color: var(--el-text-color-secondary);
  margin: 0 0 24px;
}

.plan-period,
.plan-renew {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

.plan-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.no-subscription {
  padding: 20px 0;
}

.renew-alert {
  margin-top: 16px;
}

/* 使用量网格 */
.usage-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

@media (max-width: 768px) {
  .usage-grid {
    grid-template-columns: 1fr;
  }
}

/* 功能权限 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

@media (max-width: 768px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.feature-item.enabled {
  color: var(--el-text-color-primary);
}
</style>

