<script setup lang="ts">
/**
 * 仪表盘布局组件
 * 
 * 提供统一的侧边栏 + 主内容区布局
 * 
 * @example
 * <DashboardLayout title="页面标题">
 *   <template #header-actions>
 *     <button>操作按钮</button>
 *   </template>
 *   
 *   <!-- 默认插槽：页面主内容 -->
 *   <div>页面内容</div>
 * </DashboardLayout>
 */
import { ref } from 'vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import QuotaIndicator from '@/components/common/QuotaIndicator.vue'
import { useUserStore } from '@/stores'

interface Props {
  /** 页面标题 */
  title?: string
  /** 是否显示头部 */
  showHeader?: boolean
  /** 是否显示配额指示器 */
  showQuota?: boolean
  /** 内容区是否添加内边距 */
  padding?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  showHeader: true,
  showQuota: true,
  padding: true,
})

const userStore = useUserStore()
const sidebarCollapsed = ref(false)
</script>

<template>
  <div class="dashboard-layout flex h-screen overflow-hidden bg-slate-50">
    <!-- 侧边栏 -->
    <Sidebar v-model:collapsed="sidebarCollapsed" />
    
    <!-- 主内容区 -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- 头部 -->
      <header
        v-if="showHeader"
        class="h-16 flex-shrink-0 flex items-center justify-between px-8 bg-white/85 backdrop-blur-xl border-b border-slate-200 sticky top-0 z-30"
      >
        <!-- 左侧：标题 -->
        <div class="flex items-center gap-4">
          <h1 v-if="title" class="text-lg font-semibold text-slate-900">
            {{ title }}
          </h1>
          <slot name="header-title" />
        </div>
        
        <!-- 右侧：操作区 -->
        <div class="flex items-center gap-4">
          <slot name="header-actions" />
          
          <!-- 配额指示器 -->
          <QuotaIndicator v-if="showQuota" />
          
          <!-- 用户头像 -->
          <el-dropdown trigger="click">
            <button class="flex items-center gap-2 hover:bg-slate-100 rounded-lg p-1.5 transition-colors">
              <div class="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                <span class="text-sm font-semibold text-indigo-600">
                  {{ userStore.user?.nickname?.charAt(0) || userStore.user?.email?.charAt(0)?.toUpperCase() || 'U' }}
                </span>
              </div>
              <el-icon class="text-slate-400"><ArrowDown /></el-icon>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="$router.push('/settings')">
                  <el-icon><Setting /></el-icon>
                  设置
                </el-dropdown-item>
                <el-dropdown-item divided @click="userStore.logout()">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      
      <!-- 页面内容 -->
      <main :class="['flex-1 overflow-y-auto', padding ? 'p-8' : '']">
        <slot />
      </main>
    </div>
  </div>
</template>

<script lang="ts">
import { ArrowDown, Setting, SwitchButton } from '@element-plus/icons-vue'

export default {
  components: { ArrowDown, Setting, SwitchButton }
}
</script>

<style scoped>
.dashboard-layout {
  min-height: 100vh;
  min-height: 100dvh;
}
</style>

