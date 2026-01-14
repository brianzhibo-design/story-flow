<template>
  <router-link 
    to="/subscription" 
    class="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 transition-colors"
  >
    <div class="relative">
      <el-progress 
        type="circle" 
        :percentage="percentage" 
        :width="32"
        :stroke-width="3"
        :color="progressColor"
        :show-text="false"
      />
      <el-icon 
        class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500"
      >
        <Coin />
      </el-icon>
    </div>
    <div class="text-sm">
      <div class="text-slate-900 font-medium">{{ remaining }}</div>
      <div class="text-slate-500 text-[10px]">积分</div>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Coin } from '@element-plus/icons-vue'
import { quotaApi } from '@/api/quota'

const quota = ref<{
  credits: { used: number; total: number; remaining: number }
} | null>(null)

const percentage = computed(() => {
  if (!quota.value) return 0
  const { used, total } = quota.value.credits
  if (!total || total === 0) return 0 // 防止除零
  return Math.round((1 - used / total) * 100)
})

const remaining = computed(() => quota.value?.credits.remaining || 0)

const progressColor = computed(() => {
  if (percentage.value < 20) return '#ef4444'
  if (percentage.value < 50) return '#f59e0b'
  return '#10b981'
})

onMounted(async () => {
  try {
    const res = await quotaApi.getStatus()
    quota.value = res.data ?? res
  } catch (error) {
    console.error('Failed to load quota:', error)
  }
})
</script>
