<template>
  <MainLayout title="工作台">
    <template #header-right>
      <!-- 配额指示器 -->
      <QuotaIndicator />
      
      <!-- 用户菜单 -->
      <el-dropdown>
        <div class="flex items-center gap-2 cursor-pointer hover:bg-slate-100 px-3 py-2 rounded-lg transition-colors">
          <div class="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-sm">
            <span class="text-sm font-semibold text-white">
              {{ user?.nickname?.[0] || user?.email?.[0] || 'U' }}
            </span>
          </div>
          <span class="text-slate-700 text-sm font-medium hidden sm:inline">{{ user?.nickname || user?.email?.split('@')[0] }}</span>
          <el-icon class="text-slate-400 w-3 h-3"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="$router.push('/subscription')">
              <el-icon class="mr-2"><CreditCard /></el-icon>
              订阅管理
            </el-dropdown-item>
            <el-dropdown-item @click="$router.push('/settings')">
              <el-icon class="mr-2"><Setting /></el-icon>
              设置
            </el-dropdown-item>
            <el-dropdown-item divided @click="logout">
              <el-icon class="mr-2 text-red-500"><SwitchButton /></el-icon>
              <span class="text-red-500">退出登录</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </template>
    
    <!-- Hero 欢迎区域 -->
    <div class="relative mb-10 rounded-2xl overflow-hidden">
      <!-- 背景渐变 -->
      <div class="absolute inset-0 bg-gradient-to-br from-indigo-600 via-purple-600 to-indigo-800"></div>
      <!-- 装饰性图案 -->
      <div class="absolute inset-0 opacity-30">
        <div class="absolute top-0 right-0 w-64 h-64 bg-white/20 rounded-full -mr-32 -mt-32 blur-3xl"></div>
        <div class="absolute bottom-0 left-1/4 w-48 h-48 bg-cyan-400/30 rounded-full blur-3xl"></div>
      </div>
      <!-- 网格图案 -->
      <div class="absolute inset-0 opacity-10" style="background-image: url(&quot;data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E&quot;);"></div>
      
      <!-- 内容 -->
      <div class="relative px-8 py-10">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div>
            <div class="inline-flex items-center gap-2 px-3 py-1 bg-white/10 backdrop-blur-sm rounded-full text-white/80 text-xs font-medium mb-4">
              <span class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
              欢迎回来
            </div>
            <h2 class="text-2xl md:text-3xl font-bold text-white mb-2">
              {{ greeting }}，{{ user?.nickname || '创作者' }}！
            </h2>
            <p class="text-white/70 text-sm md:text-base max-w-lg">
              今天想创作什么精彩的视频故事呢？让 AI 帮你把想法变成现实。
            </p>
          </div>
          
          <!-- 快捷创建按钮 -->
          <button
            class="group flex items-center gap-3 bg-white hover:bg-slate-50 text-slate-900 px-6 py-4 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-0.5"
            @click="$router.push('/projects/create')"
          >
            <div class="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center transition-transform group-hover:rotate-90 duration-300">
              <el-icon class="w-5 h-5 text-white"><Plus /></el-icon>
            </div>
            <div class="text-left">
              <span class="block font-semibold">创建新项目</span>
              <span class="block text-xs text-slate-500">输入故事，一键生成</span>
            </div>
          </button>
        </div>
      </div>
    </div>
    
    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-10">
      <!-- 项目总数 -->
      <div class="stat-card group">
        <div class="stat-icon bg-gradient-to-br from-blue-500 to-cyan-500">
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <p class="stat-label">项目总数</p>
          <p class="stat-value">{{ stats.totalProjects }}</p>
        </div>
        <div class="stat-trend stat-trend-up" v-if="stats.totalProjects > 0">
          <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
          活跃
        </div>
      </div>
      
      <!-- 已完成 -->
      <div class="stat-card group">
        <div class="stat-icon bg-gradient-to-br from-emerald-500 to-teal-500">
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <p class="stat-label">已完成</p>
          <p class="stat-value">{{ stats.completedProjects }}</p>
        </div>
        <div class="stat-trend stat-trend-success" v-if="stats.completedProjects > 0">
          {{ Math.round((stats.completedProjects / (stats.totalProjects || 1)) * 100) }}%
        </div>
      </div>
      
      <!-- 处理中 -->
      <div class="stat-card group">
        <div class="stat-icon bg-gradient-to-br from-amber-500 to-orange-500">
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <p class="stat-label">处理中</p>
          <p class="stat-value">{{ stats.processingProjects }}</p>
        </div>
        <div class="stat-trend stat-trend-warning" v-if="stats.processingProjects > 0">
          进行中
        </div>
      </div>
      
      <!-- 草稿 -->
      <div class="stat-card group">
        <div class="stat-icon bg-gradient-to-br from-slate-500 to-slate-600">
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <p class="stat-label">草稿</p>
          <p class="stat-value">{{ stats.draftProjects }}</p>
        </div>
      </div>
    </div>
    
    <!-- 项目列表标题 -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
      <div class="flex items-center gap-3">
        <h3 class="text-lg font-semibold text-slate-900">我的项目</h3>
        <span class="px-2 py-0.5 bg-slate-100 text-slate-500 text-xs font-medium rounded-full">
          {{ filteredProjects.length }}
        </span>
      </div>
      
      <div class="flex flex-col sm:flex-row gap-3">
        <!-- 搜索框 -->
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索项目..."
            class="input pl-10 w-full sm:w-64"
          />
        </div>
        
        <!-- 状态筛选 -->
        <select
          v-model="statusFilter"
          class="input w-full sm:w-32 appearance-none cursor-pointer"
        >
          <option value="">全部状态</option>
          <option value="draft">草稿</option>
          <option value="processing">生成中</option>
          <option value="completed">已完成</option>
        </select>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <SkeletonProjectCard v-for="i in 6" :key="i" />
    </div>
    
    <!-- 项目列表 -->
    <div v-else-if="filteredProjects.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <ProjectCard
        v-for="project in filteredProjects"
        :key="project.id"
        :project="project"
        @edit="handleEdit"
        @delete="handleDelete"
        @share="handleShare"
      />
    </div>
    
    <!-- 空状态 -->
    <div
      v-else
      class="flex flex-col items-center justify-center py-20 text-center"
    >
      <div class="w-20 h-20 bg-gradient-to-br from-slate-100 to-slate-200 rounded-2xl flex items-center justify-center mb-6">
        <svg class="w-10 h-10 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
      </div>
      <h3 class="text-lg font-semibold text-slate-900 mb-2">
        {{ searchQuery ? '没有找到匹配的项目' : '还没有任何项目' }}
      </h3>
      <p class="text-slate-500 mb-6 max-w-sm">
        {{ searchQuery ? '尝试其他关键词搜索' : '创建您的第一个项目，开始 AI 视频创作之旅' }}
      </p>
      <button
        v-if="!searchQuery"
        class="btn-primary"
        @click="$router.push('/projects/create')"
      >
        <el-icon class="w-4 h-4"><Plus /></el-icon>
        创建第一个项目
      </button>
    </div>
    
    <!-- 分页 -->
    <div v-if="pagination.total_pages > 1" class="mt-10 flex justify-center">
      <el-pagination
        v-model:current-page="pagination.page"
        :page-size="pagination.page_size"
        :total="pagination.total"
        layout="prev, pager, next"
        background
        @current-change="handlePageChange"
      />
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { 
  Plus, ArrowDown, 
  CreditCard, SwitchButton, Setting 
} from '@element-plus/icons-vue'
import { useAuth } from '@/composables/useAuth'
import { useProjectStore } from '@/stores'
import { MainLayout } from '@/components/layout'
import { ProjectCard } from '@/components/common'
import QuotaIndicator from '@/components/common/QuotaIndicator.vue'
import SkeletonProjectCard from '@/components/common/SkeletonProjectCard.vue'

const { user, logout } = useAuth()
const projectStore = useProjectStore()

const searchQuery = ref('')
const statusFilter = ref('')

const projects = computed(() => projectStore.projects)
const loading = computed(() => projectStore.loading)
const pagination = computed(() => projectStore.pagination)

// 时间问候语
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 12) return '早上好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const stats = computed(() => ({
  totalProjects: projects.value.length,
  completedProjects: projects.value.filter(p => p.status === 'completed').length,
  processingProjects: projects.value.filter(p => p.status === 'processing').length,
  draftProjects: projects.value.filter(p => p.status === 'draft').length,
}))

const filteredProjects = computed(() => {
  let result = projects.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(p => 
      p.title.toLowerCase().includes(query) ||
      p.description?.toLowerCase().includes(query)
    )
  }
  
  if (statusFilter.value) {
    result = result.filter(p => p.status === statusFilter.value)
  }
  
  return result
})

onMounted(() => {
  projectStore.fetchProjects()
})

function handlePageChange(page: number) {
  projectStore.fetchProjects(page)
}

function handleEdit(id: string) {
  // 编辑项目
}

function handleDelete(id: string) {
  // 删除项目
  projectStore.remove(id)
}

function handleShare(id: string) {
  // 分享项目
}
</script>

<style scoped>
/* 统计卡片 */
.stat-card {
  @apply flex items-center gap-4 p-5 bg-white rounded-xl border border-slate-100;
  @apply transition-all duration-300 cursor-default;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.stat-card:hover {
  @apply border-slate-200 -translate-y-0.5;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
}

.stat-icon {
  @apply w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0;
  @apply transition-transform duration-300;
}

.stat-card:hover .stat-icon {
  @apply scale-110;
}

.stat-label {
  @apply text-xs font-medium text-slate-500 uppercase tracking-wide mb-1;
}

.stat-value {
  @apply text-2xl font-bold text-slate-900 tabular-nums;
}

.stat-trend {
  @apply flex items-center gap-1 text-[10px] font-bold uppercase tracking-wide px-2 py-1 rounded-full;
}

.stat-trend-up {
  @apply bg-blue-50 text-blue-600;
}

.stat-trend-success {
  @apply bg-emerald-50 text-emerald-600;
}

.stat-trend-warning {
  @apply bg-amber-50 text-amber-600;
}

/* 响应式动画 */
@media (prefers-reduced-motion: reduce) {
  .stat-card,
  .stat-icon,
  button {
    transition: none !important;
    animation: none !important;
  }
  
  .animate-pulse {
    animation: none !important;
  }
}
</style>
