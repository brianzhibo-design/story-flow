<script setup lang="ts">
/**
 * 导航项组件
 * 
 * 用法:
 * <NavItem to="/dashboard" icon="House" label="Dashboard" />
 * <NavItem to="/projects" icon="Film" label="Projects" badge="12" />
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'

interface Props {
  /** 路由路径 */
  to: string
  /** 图标名称 */
  icon?: string
  /** 标签文本 */
  label: string
  /** 徽章数量/文本 */
  badge?: string | number
  /** 是否精确匹配路由 */
  exact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  exact: false,
})

const route = useRoute()

// 判断是否激活
const isActive = computed(() => {
  if (props.exact) {
    return route.path === props.to
  }
  return route.path.startsWith(props.to)
})
</script>

<template>
  <router-link
    :to="to"
    :class="[
      'nav-item relative',
      'flex items-center gap-3 px-3 py-2 rounded-lg',
      'transition-all duration-200',
      'group',
      isActive
        ? 'bg-slate-50 text-slate-900 font-medium'
        : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900',
    ]"
  >
    <!-- 激活指示条 -->
    <div
      v-if="isActive"
      class="absolute left-[-12px] top-1/2 -translate-y-1/2 h-5 w-1 bg-indigo-600 rounded-r transition-all duration-200"
    />
    
    <!-- 图标 -->
    <el-icon
      :class="[
        'w-4 h-4 transition-colors',
        isActive ? 'text-indigo-600' : 'group-hover:text-indigo-600',
      ]"
    >
      <component :is="icon" />
    </el-icon>
    
    <!-- 标签 -->
    <span class="flex-1">{{ label }}</span>
    
    <!-- 徽章 -->
    <span
      v-if="badge !== undefined"
      class="ml-auto bg-slate-100 text-slate-600 text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[20px] text-center"
    >
      {{ badge }}
    </span>
  </router-link>
</template>

<style scoped>
.nav-item {
  text-decoration: none;
}
</style>

