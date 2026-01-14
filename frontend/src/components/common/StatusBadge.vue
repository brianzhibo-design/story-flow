<script setup lang="ts">
/**
 * 状态徽章组件
 * 
 * 用法:
 * <StatusBadge status="completed" />
 * <StatusBadge status="processing" show-dot />
 */

type Status = 'completed' | 'processing' | 'pending' | 'failed' | 'draft' | 'queued' | 'running'

interface Props {
  status: Status
  /** 是否显示状态点 */
  showDot?: boolean
  /** 自定义文本 */
  text?: string
}

const props = withDefaults(defineProps<Props>(), {
  showDot: true,
})

// 状态样式映射
const statusClasses: Record<Status, string> = {
  completed: 'text-emerald-600 bg-emerald-50 border-emerald-100',
  processing: 'text-orange-600 bg-orange-50 border-orange-100',
  pending: 'text-slate-500 bg-slate-50 border-slate-200',
  failed: 'text-red-600 bg-red-50 border-red-100',
  draft: 'text-yellow-700 bg-yellow-50 border-yellow-200/60',
  queued: 'text-blue-600 bg-blue-50 border-blue-100',
  running: 'text-indigo-600 bg-indigo-50 border-indigo-100',
}

// 状态文本映射
const statusText: Record<Status, string> = {
  completed: 'Rendered',
  processing: 'Processing',
  pending: 'Pending',
  failed: 'Failed',
  draft: 'Draft',
  queued: 'Queued',
  running: 'Running',
}

// 状态点颜色
const dotColors: Record<Status, string> = {
  completed: 'bg-emerald-500',
  processing: 'bg-orange-500',
  pending: 'bg-slate-400',
  failed: 'bg-red-500',
  draft: 'bg-yellow-500',
  queued: 'bg-blue-500',
  running: 'bg-indigo-500',
}
</script>

<template>
  <span
    :class="[
      'inline-flex items-center gap-1.5',
      'text-[10px] font-bold uppercase tracking-wide',
      'px-2 py-0.5 rounded-full border',
      'transition-colors duration-200',
      statusClasses[status],
    ]"
  >
    <!-- 状态点 -->
    <span
      v-if="showDot"
      :class="[
        'status-dot w-1.5 h-1.5 rounded-full',
        dotColors[status],
        { 'animate-pulse': status === 'processing' || status === 'running' },
      ]"
    />
    
    <!-- 文本 -->
    {{ text || statusText[status] }}
  </span>
</template>

<style scoped>
/* 完成状态的脉冲效果 */
.status-dot {
  position: relative;
}

/* Processing 和 Running 状态的呼吸动画 */
.animate-pulse {
  animation: status-pulse 2s infinite;
}

@keyframes status-pulse {
  0% {
    box-shadow: 0 0 0 0 currentColor;
    opacity: 1;
  }
  70% {
    box-shadow: 0 0 0 4px transparent;
    opacity: 0.7;
  }
  100% {
    box-shadow: 0 0 0 0 transparent;
    opacity: 1;
  }
}
</style>

