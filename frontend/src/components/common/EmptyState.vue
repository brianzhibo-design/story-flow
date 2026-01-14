<script setup lang="ts">
/**
 * 空状态组件
 * 
 * 用法:
 * <EmptyState
 *   icon="Film"
 *   title="暂无项目"
 *   description="创建您的第一个项目开始使用"
 * >
 *   <el-button type="primary">创建项目</el-button>
 * </EmptyState>
 */

interface Props {
  /** 图标名称 */
  icon?: string
  /** 标题 */
  title: string
  /** 描述文本 */
  description?: string
  /** 图片URL (优先于图标) */
  image?: string
}

withDefaults(defineProps<Props>(), {
  icon: 'Files',
})
</script>

<template>
  <div class="empty-state flex flex-col items-center justify-center py-16 px-8 text-center">
    <!-- 图片或图标 -->
    <div class="mb-6">
      <img
        v-if="image"
        :src="image"
        class="w-48 h-48 object-contain opacity-60"
        alt=""
      />
      <div
        v-else
        class="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center"
      >
        <el-icon class="w-10 h-10 text-slate-400">
          <component :is="icon" />
        </el-icon>
      </div>
    </div>
    
    <!-- 标题 -->
    <h3 class="text-lg font-semibold text-slate-900 mb-2">
      {{ title }}
    </h3>
    
    <!-- 描述 -->
    <p v-if="description" class="text-sm text-slate-500 max-w-sm mb-6">
      {{ description }}
    </p>
    
    <!-- 操作区 -->
    <slot />
  </div>
</template>

<style scoped>
.empty-state {
  min-height: 300px;
}
</style>

