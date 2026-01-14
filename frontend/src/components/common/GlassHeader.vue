<script setup lang="ts">
/**
 * 毛玻璃头部组件
 * 
 * 用法:
 * <GlassHeader>
 *   <template #left>左侧内容</template>
 *   <template #center>中间内容</template>
 *   <template #right>右侧内容</template>
 * </GlassHeader>
 */

interface Props {
  /** 是否固定在顶部 */
  sticky?: boolean
  /** 是否显示底部边框 */
  bordered?: boolean
  /** 高度 */
  height?: string
}

withDefaults(defineProps<Props>(), {
  sticky: true,
  bordered: true,
  height: '64px',
})
</script>

<template>
  <header
    :class="[
      'glass-header',
      'flex items-center justify-between px-8',
      'bg-white/85 backdrop-blur-xl',
      { 'sticky top-0 z-30': sticky },
      { 'border-b border-slate-200': bordered },
    ]"
    :style="{ height }"
  >
    <!-- 左侧区域 -->
    <div class="flex items-center gap-4 min-w-0">
      <slot name="left" />
    </div>
    
    <!-- 中间区域 -->
    <div class="flex-1 flex items-center justify-center px-4">
      <slot name="center" />
    </div>
    
    <!-- 右侧区域 -->
    <div class="flex items-center gap-3">
      <slot name="right" />
    </div>
    
    <!-- 默认插槽 (如果不使用具名插槽) -->
    <slot />
  </header>
</template>

<style scoped>
.glass-header {
  transition: background-color 0.2s, border-color 0.2s;
}

/* 滚动时增强效果 */
.glass-header.scrolled {
  background-color: rgba(255, 255, 255, 0.95);
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
}
</style>

