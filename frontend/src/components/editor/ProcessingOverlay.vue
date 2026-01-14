<script setup lang="ts">
/**
 * 处理中覆盖层组件
 * 
 * 用法:
 * <ProcessingOverlay :progress="50" message="Generating image..." />
 */
import { computed } from 'vue'
import { Loading } from '@element-plus/icons-vue'

interface Props {
  /** 进度 (0-100) */
  progress?: number
  /** 状态消息 */
  message?: string
  /** 预计剩余时间 (秒) */
  remainingTime?: number
  /** 是否显示取消按钮 */
  cancelable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  progress: 0,
  message: 'Processing...',
  cancelable: false,
})

const emit = defineEmits<{
  cancel: []
}>()

// 格式化剩余时间
const formattedTime = computed(() => {
  if (!props.remainingTime) return null
  
  if (props.remainingTime < 60) {
    return `${Math.round(props.remainingTime)}s`
  }
  
  const minutes = Math.floor(props.remainingTime / 60)
  const seconds = Math.round(props.remainingTime % 60)
  return `${minutes}m ${seconds}s`
})
</script>

<template>
  <div class="processing-overlay absolute inset-0 bg-white rounded-md overflow-hidden">
    <!-- 闪烁背景 -->
    <div class="absolute inset-0 shimmer-bg opacity-60" />
    
    <!-- 中心内容 -->
    <div class="absolute inset-0 flex flex-col items-center justify-center z-10">
      <!-- 加载图标 -->
      <div class="relative mb-4">
        <el-icon class="w-10 h-10 text-orange-500 animate-spin">
          <Loading />
        </el-icon>
        <!-- 进度环 (可选) -->
        <svg
          v-if="progress > 0"
          class="absolute inset-0 w-10 h-10 -rotate-90"
          viewBox="0 0 40 40"
        >
          <circle
            cx="20"
            cy="20"
            r="18"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="text-orange-200"
          />
          <circle
            cx="20"
            cy="20"
            r="18"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="text-orange-500 transition-all duration-500"
            :stroke-dasharray="`${(progress / 100) * 113} 113`"
            stroke-linecap="round"
          />
        </svg>
      </div>
      
      <!-- 状态文字 -->
      <span class="text-xs font-bold text-slate-700 mb-1">
        {{ message }}
      </span>
      
      <!-- 剩余时间 -->
      <span v-if="formattedTime" class="text-[10px] text-slate-400 mb-3">
        Est. {{ formattedTime }} remaining
      </span>
      
      <!-- 进度百分比 -->
      <span v-if="progress > 0" class="text-xs font-mono text-orange-600 font-bold">
        {{ Math.round(progress) }}%
      </span>
      
      <!-- 取消按钮 -->
      <button
        v-if="cancelable"
        class="mt-3 px-3 py-1.5 text-xs font-medium text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-md transition-colors"
        @click="emit('cancel')"
      >
        Cancel
      </button>
    </div>
    
    <!-- 底部进度条 -->
    <div class="absolute bottom-0 left-0 w-full h-1 bg-slate-100">
      <div
        class="h-full bg-orange-500 transition-all duration-1000 ease-out"
        :style="{
          width: `${progress}%`,
          boxShadow: progress > 0 ? '0 0 10px rgba(249,115,22,0.5)' : 'none',
        }"
      />
    </div>
  </div>
</template>

<style scoped>
.shimmer-bg {
  background: #f6f7f8;
  background-image: linear-gradient(
    to right,
    #f6f7f8 0%,
    #fff7ed 20%,
    #f6f7f8 40%,
    #f6f7f8 100%
  );
  background-repeat: no-repeat;
  background-size: 1000px 100%;
  animation: shimmer 2.5s infinite linear;
}

@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}
</style>

