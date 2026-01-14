<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
    <!-- 顶部导航 -->
    <header class="bg-black/20 backdrop-blur-xl border-b border-white/10">
      <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <router-link to="/dashboard" class="text-white/60 hover:text-white transition">
            <el-icon :size="24"><ArrowLeft /></el-icon>
          </router-link>
          <h1 class="text-xl font-semibold text-white">配额管理</h1>
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-6 py-8">
      <!-- 当前配额状态 -->
      <div class="mb-12">
        <div class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-violet-600 to-purple-600 p-8">
          <div class="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32 blur-3xl"></div>
          
          <div class="relative z-10">
            <div class="flex items-center gap-2 mb-4">
              <el-tag :type="planTagType" size="large" effect="dark">
                {{ planName }}
              </el-tag>
            </div>
            
            <h2 class="text-3xl font-bold text-white mb-2">
              {{ quota?.credits?.remaining || 0 }} / {{ quota?.credits?.total || 0 }}
            </h2>
            <p class="text-white/70">剩余积分</p>
            
            <el-progress 
              :percentage="quotaPercentage" 
              :stroke-width="12"
              :color="progressColor"
              class="mt-6"
            />
            
            <p v-if="quota?.reset_at" class="text-white/60 text-sm mt-4">
              下次重置：{{ formatDate(quota.reset_at) }}
            </p>
          </div>
        </div>
      </div>

      <!-- 今日使用量 -->
      <div class="mb-12">
        <h3 class="text-xl font-semibold text-white mb-6">今日使用量</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div 
            v-for="usage in usageStats" 
            :key="usage.key"
            class="bg-white/5 backdrop-blur rounded-xl p-5 border border-white/10"
          >
            <div class="flex items-center gap-3 mb-3">
              <div :class="['w-10 h-10 rounded-lg flex items-center justify-center', usage.bgColor]">
                <el-icon :size="20" class="text-white">
                  <component :is="usage.icon" />
                </el-icon>
              </div>
              <span class="text-white/80">{{ usage.label }}</span>
            </div>
            <div class="text-2xl font-bold text-white">
              {{ quota?.daily_usage?.[usage.key] || 0 }}
              <span class="text-sm font-normal text-white/50">
                / {{ quota?.limits?.[usage.key] || '∞' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 套餐方案 -->
      <div>
        <h3 class="text-xl font-semibold text-white mb-6">升级套餐</h3>
        <div class="grid md:grid-cols-3 gap-6">
          <div 
            v-for="plan in plans" 
            :key="plan.id"
            :class="[
              'relative rounded-2xl p-6 border transition-all duration-300',
              plan.id === currentPlan 
                ? 'bg-violet-600/20 border-violet-500' 
                : 'bg-white/5 border-white/10 hover:border-white/30'
            ]"
          >
            <!-- 当前套餐标记 -->
            <div 
              v-if="plan.id === currentPlan" 
              class="absolute -top-3 left-6 px-3 py-1 bg-violet-500 text-white text-xs rounded-full"
            >
              当前套餐
            </div>
            
            <h4 class="text-xl font-semibold text-white mb-2">{{ plan.name }}</h4>
            <div class="text-3xl font-bold text-white mb-4">
              ¥{{ plan.price }}
              <span class="text-sm font-normal text-white/50">/月</span>
            </div>
            
            <ul class="space-y-3 mb-6">
              <li v-for="feature in getPlanFeatures(plan)" :key="feature" class="flex items-center gap-2 text-white/70">
                <el-icon class="text-green-400"><Check /></el-icon>
                <span>{{ feature }}</span>
              </li>
            </ul>
            
            <el-button 
              v-if="plan.id !== currentPlan"
              type="primary"
              class="w-full"
              :disabled="plan.id === 'free'"
              @click="handleUpgrade(plan.id)"
            >
              {{ plan.id === 'free' ? '基础版' : '升级套餐' }}
            </el-button>
            <el-button v-else disabled class="w-full">当前套餐</el-button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ArrowLeft, Picture, VideoCamera, Microphone, Document, Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { quotaApi } from '@/api/quota'

interface QuotaStatus {
  plan: string
  credits: { used: number; total: number; remaining: number }
  daily_usage: Record<string, number>
  limits: Record<string, number>
  reset_at: string
}

interface Plan {
  id: string
  name: string
  price: number
  limits: Record<string, number>
}

const quota = ref<QuotaStatus | null>(null)
const plans = ref<Plan[]>([])
const loading = ref(false)

const usageStats = [
  { key: 'image_generation', label: '图片生成', icon: Picture, bgColor: 'bg-blue-500' },
  { key: 'video_generation', label: '视频生成', icon: VideoCamera, bgColor: 'bg-purple-500' },
  { key: 'audio_generation', label: '配音生成', icon: Microphone, bgColor: 'bg-green-500' },
  { key: 'storyboard', label: '分镜生成', icon: Document, bgColor: 'bg-orange-500' },
]

const currentPlan = computed(() => quota.value?.plan || 'free')

const planName = computed(() => {
  const names: Record<string, string> = {
    free: '免费版',
    premium: '专业版',
    enterprise: '企业版'
  }
  return names[currentPlan.value] || currentPlan.value
})

const planTagType = computed(() => {
  const types: Record<string, 'info' | 'warning' | 'success'> = {
    free: 'info',
    premium: 'warning',
    enterprise: 'success'
  }
  return types[currentPlan.value] || 'info'
})

const quotaPercentage = computed(() => {
  if (!quota.value) return 0
  const { used, total } = quota.value.credits
  if (!total || total === 0) return 0 // 防止除零
  return Math.round((used / total) * 100)
})

const progressColor = computed(() => {
  if (quotaPercentage.value > 80) return '#ef4444'
  if (quotaPercentage.value > 50) return '#f59e0b'
  return '#10b981'
})

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function getPlanFeatures(plan: Plan): string[] {
  const features = []
  if (plan.limits.monthly_credits) {
    features.push(`每月 ${plan.limits.monthly_credits} 积分`)
  }
  if (plan.limits.max_projects > 0) {
    features.push(`最多 ${plan.limits.max_projects} 个项目`)
  } else if (plan.limits.max_projects === -1) {
    features.push('无限项目')
  }
  if (plan.limits.image_generation) {
    features.push(`每日 ${plan.limits.image_generation} 次图片生成`)
  }
  if (plan.limits.video_generation) {
    features.push(`每日 ${plan.limits.video_generation} 次视频生成`)
  }
  return features
}

async function handleUpgrade(planId: string) {
  try {
    loading.value = true
    await quotaApi.upgradePlan(planId)
    ElMessage.success('套餐升级成功！')
    await loadQuotaStatus()
  } catch (error) {
    ElMessage.error('升级失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

async function loadQuotaStatus() {
  try {
    const [statusRes, plansRes] = await Promise.all([
      quotaApi.getStatus(),
      quotaApi.getPlans()
    ])
    quota.value = statusRes.data
    plans.value = plansRes.data
  } catch (error) {
    console.error('Failed to load quota:', error)
  }
}

onMounted(() => {
  loadQuotaStatus()
})
</script>

