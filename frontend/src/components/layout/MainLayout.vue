<script setup lang="ts">
/**
 * 主布局组件
 * 
 * 用法:
 * <MainLayout>
 *   <template #header>头部内容</template>
 *   <template #default>页面内容</template>
 * </MainLayout>
 */
import { ref } from 'vue'
import Sidebar from './Sidebar.vue'
import GlassHeader from '@/components/common/GlassHeader.vue'

interface Props {
  /** 是否显示侧边栏 */
  showSidebar?: boolean
  /** 是否显示头部 */
  showHeader?: boolean
  /** 页面标题 */
  title?: string
  /** 是否全宽内容 */
  fullWidth?: boolean
}

withDefaults(defineProps<Props>(), {
  showSidebar: true,
  showHeader: true,
  fullWidth: false,
})

const sidebarCollapsed = ref(false)
</script>

<template>
  <div class="main-layout flex min-h-screen bg-slate-50">
    <!-- 侧边栏 -->
    <Sidebar
      v-if="showSidebar"
      v-model:collapsed="sidebarCollapsed"
    />
    
    <!-- 主内容区 -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- 头部 -->
      <GlassHeader v-if="showHeader">
        <template #left>
          <slot name="header-left">
            <h1 v-if="title" class="text-lg font-semibold text-slate-900">
              {{ title }}
            </h1>
          </slot>
        </template>
        
        <template #center>
          <slot name="header-center" />
        </template>
        
        <template #right>
          <slot name="header-right" />
        </template>
      </GlassHeader>
      
      <!-- 页面内容 -->
      <main
        :class="[
          'flex-1 overflow-y-auto',
          fullWidth ? '' : 'p-8',
        ]"
      >
        <div :class="fullWidth ? '' : 'max-w-7xl mx-auto'">
          <slot />
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.main-layout {
  min-height: 100vh;
  min-height: 100dvh;
}
</style>

