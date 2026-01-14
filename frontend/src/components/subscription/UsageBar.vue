<template>
  <div class="usage-bar">
    <div class="usage-header">
      <div class="usage-label">
        <el-icon :size="18">
          <component :is="iconComponent" />
        </el-icon>
        <span>{{ label }}</span>
      </div>
      <span class="usage-text">
        {{ formatNumber(used) }} / {{ limit === -1 ? '无限' : formatNumber(limit) }} {{ unit }}
      </span>
    </div>
    
    <el-progress
      :percentage="percentage"
      :status="status"
      :stroke-width="10"
      :show-text="false"
    />
    
    <div class="usage-footer" v-if="limit !== -1">
      <span :class="['remaining', { warning: isWarning, danger: isDanger }]">
        剩余 {{ formatNumber(remaining) }} {{ unit }}
      </span>
      <span class="percentage">{{ percentage }}%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, markRaw } from 'vue'
import { 
  ChatDotRound, 
  Picture, 
  VideoCamera, 
  FolderOpened,
  Timer,
  Microphone
} from '@element-plus/icons-vue'

const props = defineProps<{
  label: string
  used: number
  limit: number
  unit: string
  icon?: string
}>()

// 图标映射
const iconMap: Record<string, any> = {
  ChatDotRound: markRaw(ChatDotRound),
  Picture: markRaw(Picture),
  VideoCamera: markRaw(VideoCamera),
  FolderOpened: markRaw(FolderOpened),
  Timer: markRaw(Timer),
  Microphone: markRaw(Microphone)
}

const iconComponent = computed(() => {
  return iconMap[props.icon || 'ChatDotRound'] || ChatDotRound
})

// 计算百分比
const percentage = computed(() => {
  if (props.limit === -1) return 0
  if (props.limit === 0) return 0 // 防止除零错误
  return Math.min(100, Math.round(props.used / props.limit * 100))
})

// 剩余量
const remaining = computed(() => {
  if (props.limit === -1) return Infinity
  return Math.max(0, props.limit - props.used)
})

// 状态
const status = computed(() => {
  if (percentage.value >= 90) return 'exception'
  if (percentage.value >= 70) return 'warning'
  return ''
})

const isWarning = computed(() => percentage.value >= 70 && percentage.value < 90)
const isDanger = computed(() => percentage.value >= 90)

// 格式化数字
function formatNumber(n: number): string {
  if (n === Infinity) return '∞'
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return String(n)
}
</script>

<style scoped>
.usage-bar {
  background: var(--el-fill-color-light);
  border-radius: 12px;
  padding: 16px;
}

.usage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.usage-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.usage-text {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.usage-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
}

.remaining {
  color: var(--el-text-color-secondary);
}

.remaining.warning {
  color: var(--el-color-warning);
}

.remaining.danger {
  color: var(--el-color-danger);
}

.percentage {
  color: var(--el-text-color-placeholder);
}
</style>

