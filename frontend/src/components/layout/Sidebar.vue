<script setup lang="ts">
/**
 * 侧边栏组件
 * 
 * 用法:
 * <Sidebar :collapsed="false" />
 */
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore, useProjectStore } from '@/stores'
import NavItem from './NavItem.vue'
import {
  House,
  Film,
  CreditCard,
  Setting,
  SwitchButton,
  Plus,
  MagicStick,
} from '@element-plus/icons-vue'

interface Props {
  /** 是否收起 */
  collapsed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  collapsed: false,
})

const emit = defineEmits<{
  'update:collapsed': [value: boolean]
}>()

const router = useRouter()
const userStore = useUserStore()
const projectStore = useProjectStore()

// 项目数量
const projectCount = computed(() => projectStore.projects.length || 0)

// 导航项配置
const navItems = computed(() => [
  { to: '/dashboard', icon: 'House', label: '工作台', exact: true },
  { to: '/projects', icon: 'Film', label: '项目', badge: projectCount.value > 0 ? projectCount.value : undefined },
  { to: '/subscription', icon: 'CreditCard', label: '订阅' },
  { to: '/settings', icon: 'Setting', label: '设置' },
])

// 创建新项目
function handleCreateProject() {
  router.push('/projects/create')
}

// 登出
function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<template>
  <aside
    :class="[
      'sidebar h-screen bg-white border-r border-slate-200',
      'flex flex-col',
      'transition-all duration-300',
      collapsed ? 'w-16' : 'w-60',
    ]"
  >
    <!-- Logo -->
    <div class="h-16 flex items-center px-4 border-b border-slate-100">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
          <el-icon class="w-5 h-5 text-white">
            <MagicStick />
          </el-icon>
        </div>
        <span
          v-if="!collapsed"
          class="text-lg font-bold text-slate-900 whitespace-nowrap"
        >
          StoryFlow
        </span>
      </div>
    </div>
    
    <!-- 新建按钮 -->
    <div class="p-4">
      <button
        :class="[
          'w-full flex items-center justify-center gap-2',
          'bg-slate-900 hover:bg-slate-800 text-white',
          'text-xs font-semibold',
          'rounded-lg shadow-sm hover:shadow-md',
          'transition-all active:scale-[0.98]',
          'group',
          collapsed ? 'px-3 py-2.5' : 'px-4 py-2.5',
        ]"
        @click="handleCreateProject"
      >
        <el-icon class="w-4 h-4 transition-transform group-hover:rotate-90">
          <Plus />
        </el-icon>
        <span v-if="!collapsed">New Project</span>
      </button>
    </div>
    
    <!-- 导航菜单 -->
    <nav class="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
      <template v-if="!collapsed">
        <NavItem
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          :icon="item.icon"
          :label="item.label"
          :badge="item.badge"
          :exact="item.exact"
        />
      </template>
      
      <!-- 收起状态只显示图标 -->
      <template v-else>
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          :class="[
            'flex items-center justify-center p-2 rounded-lg',
            'text-slate-500 hover:text-slate-900 hover:bg-slate-50',
            'transition-colors',
          ]"
          :title="item.label"
        >
          <el-icon class="w-5 h-5">
            <component :is="item.icon" />
          </el-icon>
        </router-link>
      </template>
    </nav>
    
    <!-- 底部用户区域 -->
    <div class="p-4 border-t border-slate-100">
      <div
        v-if="!collapsed && userStore.user"
        class="flex items-center gap-3 mb-3"
      >
        <div class="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
          <span class="text-sm font-semibold text-indigo-600">
            {{ userStore.user.nickname?.charAt(0) || userStore.user.email.charAt(0).toUpperCase() }}
          </span>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-slate-900 truncate">
            {{ userStore.user.nickname || userStore.user.email.split('@')[0] }}
          </p>
          <p class="text-xs text-slate-500 truncate">
            {{ userStore.user.email }}
          </p>
        </div>
      </div>
      
      <button
        :class="[
          'w-full flex items-center gap-2',
          'text-slate-500 hover:text-red-600',
          'text-xs font-medium',
          'rounded-lg hover:bg-red-50',
          'transition-colors',
          collapsed ? 'justify-center p-2' : 'px-3 py-2',
        ]"
        @click="handleLogout"
      >
        <el-icon class="w-4 h-4">
          <SwitchButton />
        </el-icon>
        <span v-if="!collapsed">退出登录</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  position: sticky;
  top: 0;
}
</style>

