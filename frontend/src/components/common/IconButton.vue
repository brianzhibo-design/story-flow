<script setup lang="ts">
/**
 * 图标按钮组件
 * 
 * 用法:
 * <IconButton icon="RefreshCw" @click="handleClick" />
 * <IconButton icon="Trash2" variant="danger" />
 */
import { computed } from 'vue'

type Variant = 'default' | 'primary' | 'danger' | 'success' | 'ghost'
type Size = 'sm' | 'md' | 'lg'

interface Props {
  /** 图标名称 (Element Plus Icons) */
  icon?: string
  /** 按钮变体 */
  variant?: Variant
  /** 尺寸 */
  size?: Size
  /** 提示文字 */
  title?: string
  /** 是否禁用 */
  disabled?: boolean
  /** 是否加载中 */
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

// 尺寸样式
const sizeClasses: Record<Size, string> = {
  sm: 'p-1.5',
  md: 'p-2',
  lg: 'p-2.5',
}

const iconSizes: Record<Size, string> = {
  sm: 'w-3.5 h-3.5',
  md: 'w-4 h-4',
  lg: 'w-5 h-5',
}

// 变体样式
const variantClasses = computed(() => {
  const base = 'rounded-lg transition-all duration-200'
  
  const variants: Record<Variant, string> = {
    default: `${base} text-slate-400 hover:text-indigo-600 hover:bg-slate-100`,
    primary: `${base} text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50`,
    danger: `${base} text-slate-400 hover:text-red-600 hover:bg-red-50`,
    success: `${base} text-slate-400 hover:text-emerald-600 hover:bg-emerald-50`,
    ghost: `${base} text-slate-500 hover:text-slate-900`,
  }
  
  return variants[props.variant]
})

function handleClick(event: MouseEvent) {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<template>
  <button
    type="button"
    :class="[
      'icon-button inline-flex items-center justify-center',
      sizeClasses[size],
      variantClasses,
      { 'opacity-50 cursor-not-allowed': disabled },
      { 'cursor-wait': loading },
    ]"
    :disabled="disabled || loading"
    :title="title"
    @click="handleClick"
  >
    <!-- 加载状态 -->
    <el-icon v-if="loading" :class="iconSizes[size]" class="animate-spin">
      <Loading />
    </el-icon>
    
    <!-- 图标 -->
    <el-icon v-else :class="iconSizes[size]">
      <component :is="icon" />
    </el-icon>
  </button>
</template>

<style scoped>
.icon-button:hover:not(:disabled) {
  transform: scale(1.05);
}

.icon-button:active:not(:disabled) {
  transform: scale(0.95);
}
</style>

