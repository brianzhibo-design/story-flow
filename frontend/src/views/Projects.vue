<script setup lang="ts">
/**
 * 项目列表页面
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useProjectStore } from '@/stores'
import DashboardLayout from '@/layouts/DashboardLayout.vue'
import SkeletonProjectCard from '@/components/common/SkeletonProjectCard.vue'

const router = useRouter()
const projectStore = useProjectStore()

// 搜索和筛选
const searchQuery = ref('')
const statusFilter = ref<string>('')
const viewMode = ref<'grid' | 'list'>('grid')

// 分页
const currentPage = ref(1)
const pageSize = ref(12)

// 状态选项
const statusOptions = [
  { label: '全部状态', value: '', icon: 'all' },
  { label: '草稿', value: 'draft', icon: 'draft' },
  { label: '处理中', value: 'processing', icon: 'processing' },
  { label: '已完成', value: 'completed', icon: 'completed' },
  { label: '失败', value: 'failed', icon: 'failed' },
]

// 加载项目
async function loadProjects() {
  await projectStore.fetchProjects({
    page: currentPage.value,
    page_size: pageSize.value,
    search: searchQuery.value || undefined,
    status: statusFilter.value || undefined,
  })
}

// 监听筛选条件变化
watch([searchQuery, statusFilter], () => {
  currentPage.value = 1
  loadProjects()
}, { debounce: 300 } as any)

watch(currentPage, () => {
  loadProjects()
})

onMounted(() => {
  loadProjects()
})

// 计算属性
const projects = computed(() => projectStore.projects)
const loading = computed(() => projectStore.loading)
const pagination = computed(() => projectStore.pagination)

// 创建项目
function handleCreate() {
  router.push('/projects/create')
}

// 查看项目
function handleView(projectId: string) {
  router.push(`/projects/${projectId}`)
}

// 删除项目
async function handleDelete(projectId: string, title: string, event: Event) {
  event.stopPropagation()
  try {
    await ElMessageBox.confirm(
      `确定要删除项目 "${title}" 吗？此操作不可恢复。`,
      '删除项目',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await projectStore.remove(projectId)
    ElMessage.success('项目已删除')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 格式化日期
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`
  
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

// 状态配置
const statusConfig: Record<string, { class: string; text: string; icon: string }> = {
  draft: { 
    class: 'bg-slate-100 text-slate-600 border-slate-200',
    text: '草稿',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
  },
  processing: { 
    class: 'bg-blue-50 text-blue-600 border-blue-200',
    text: '处理中',
    icon: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15'
  },
  completed: { 
    class: 'bg-emerald-50 text-emerald-600 border-emerald-200',
    text: '已完成',
    icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
  },
  failed: { 
    class: 'bg-red-50 text-red-600 border-red-200',
    text: '失败',
    icon: 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
  },
}

function getStatusConfig(status: string) {
  return statusConfig[status] || statusConfig.draft
}
</script>

<template>
  <DashboardLayout title="我的项目">
    <template #header-actions>
      <button 
        class="btn-primary"
        @click="handleCreate"
      >
        <el-icon class="w-4 h-4"><Plus /></el-icon>
        新建项目
      </button>
    </template>
    
    <div class="max-w-7xl mx-auto">
      <!-- 筛选工具栏 -->
      <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 mb-8">
        <!-- 左侧：搜索和筛选 -->
        <div class="flex flex-col sm:flex-row items-start sm:items-center gap-3 w-full lg:w-auto">
          <!-- 搜索框 -->
          <div class="relative w-full sm:w-80">
            <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索项目名称..."
              class="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
            />
          </div>
          
          <!-- 状态筛选 -->
          <div class="flex gap-2 overflow-x-auto pb-1 sm:pb-0 w-full sm:w-auto">
            <button
              v-for="option in statusOptions"
              :key="option.value"
              class="filter-chip"
              :class="{ active: statusFilter === option.value }"
              @click="statusFilter = option.value"
            >
              {{ option.label }}
            </button>
          </div>
        </div>
        
        <!-- 右侧：视图切换 -->
        <div class="flex items-center gap-2 bg-slate-100 p-1 rounded-lg">
          <button
            class="view-toggle"
            :class="{ active: viewMode === 'grid' }"
            @click="viewMode = 'grid'"
            title="网格视图"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </button>
          <button
            class="view-toggle"
            :class="{ active: viewMode === 'list' }"
            @click="viewMode = 'list'"
            title="列表视图"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <SkeletonProjectCard v-for="i in 6" :key="i" />
      </div>
      
      <!-- 空状态 -->
      <div
        v-else-if="projects.length === 0"
        class="flex flex-col items-center justify-center py-20 text-center"
      >
        <div class="w-24 h-24 bg-gradient-to-br from-slate-100 to-slate-200 rounded-2xl flex items-center justify-center mb-6 shadow-inner">
          <svg class="w-12 h-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-slate-900 mb-2">
          {{ searchQuery || statusFilter ? '未找到匹配的项目' : '还没有任何项目' }}
        </h3>
        <p class="text-slate-500 mb-8 max-w-md">
          {{ searchQuery || statusFilter ? '尝试调整搜索条件或筛选器' : '创建您的第一个项目，开始 AI 视频创作之旅' }}
        </p>
        <button
          v-if="!searchQuery && !statusFilter"
          class="btn-primary"
          @click="handleCreate"
        >
          <el-icon class="w-4 h-4"><Plus /></el-icon>
          创建第一个项目
        </button>
        <button
          v-else
          class="btn-ghost"
          @click="searchQuery = ''; statusFilter = ''"
        >
          清除筛选条件
        </button>
      </div>
      
      <!-- 网格视图 -->
      <div v-else-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="project in projects"
          :key="project.id"
          class="project-card group"
          @click="handleView(project.id)"
        >
          <!-- 缩略图 -->
          <div class="relative aspect-video bg-gradient-to-br from-slate-100 to-slate-50 overflow-hidden">
            <img
              v-if="project.thumbnail_url"
              :src="project.thumbnail_url"
              :alt="project.title"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
            <div v-else class="w-full h-full flex items-center justify-center">
              <svg class="w-16 h-16 text-slate-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            
            <!-- 状态标签 -->
            <span
              :class="[
                'absolute top-3 left-3 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide rounded-full border',
                getStatusConfig(project.status).class
              ]"
            >
              {{ getStatusConfig(project.status).text }}
            </span>
            
            <!-- 悬停操作层 -->
            <div class="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-slate-900/40 to-transparent opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-end justify-between p-4">
              <button
                class="action-btn-light"
                title="打开项目"
                @click.stop="handleView(project.id)"
              >
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
              <button
                class="action-btn-danger"
                title="删除项目"
                @click.stop="handleDelete(project.id, project.title, $event)"
              >
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
          
          <!-- 信息区 -->
          <div class="p-5">
            <h3 class="font-semibold text-slate-900 mb-1.5 truncate group-hover:text-indigo-600 transition-colors">
              {{ project.title }}
            </h3>
            <p v-if="project.description" class="text-sm text-slate-500 mb-4 line-clamp-2">
              {{ project.description }}
            </p>
            <div class="flex items-center justify-between text-xs text-slate-400">
              <span class="flex items-center gap-1.5">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ formatDate(project.updated_at) }}
              </span>
              <span class="flex items-center gap-1.5">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
                {{ project.scene_count }} 个分镜
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 列表视图 -->
      <div v-else class="space-y-3">
        <div
          v-for="project in projects"
          :key="project.id"
          class="project-list-item group"
          @click="handleView(project.id)"
        >
          <!-- 缩略图 -->
          <div class="w-32 h-20 flex-shrink-0 rounded-lg overflow-hidden bg-slate-100">
            <img
              v-if="project.thumbnail_url"
              :src="project.thumbnail_url"
              :alt="project.title"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full flex items-center justify-center">
              <svg class="w-8 h-8 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
          
          <!-- 信息 -->
          <div class="flex-1 min-w-0 py-1">
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <h3 class="font-semibold text-slate-900 truncate group-hover:text-indigo-600 transition-colors">
                  {{ project.title }}
                </h3>
                <p v-if="project.description" class="text-sm text-slate-500 truncate mt-0.5">
                  {{ project.description }}
                </p>
              </div>
              <span
                :class="[
                  'flex-shrink-0 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide rounded-full border',
                  getStatusConfig(project.status).class
                ]"
              >
                {{ getStatusConfig(project.status).text }}
              </span>
            </div>
            <div class="flex items-center gap-4 mt-2 text-xs text-slate-400">
              <span class="flex items-center gap-1">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ formatDate(project.updated_at) }}
              </span>
              <span class="flex items-center gap-1">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
                {{ project.scene_count }} 个分镜
              </span>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              class="p-2 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
              title="打开项目"
              @click.stop="handleView(project.id)"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </button>
            <button
              class="p-2 rounded-lg hover:bg-red-50 text-slate-400 hover:text-red-600 transition-colors"
              title="删除项目"
              @click.stop="handleDelete(project.id, project.title, $event)"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- 分页 -->
      <div v-if="pagination.total_pages > 1" class="flex justify-center mt-10">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="pagination.total"
          layout="prev, pager, next"
          background
        />
      </div>
    </div>
  </DashboardLayout>
</template>

<style scoped>
/* 筛选标签 */
.filter-chip {
  @apply px-3 py-1.5 text-xs font-medium rounded-full whitespace-nowrap;
  @apply bg-white border border-slate-200 text-slate-600;
  @apply hover:border-slate-300 hover:bg-slate-50;
  @apply transition-all cursor-pointer;
}

.filter-chip.active {
  @apply bg-indigo-600 border-indigo-600 text-white;
  @apply hover:bg-indigo-700 hover:border-indigo-700;
}

/* 视图切换 */
.view-toggle {
  @apply p-2 rounded-md text-slate-500 transition-colors cursor-pointer;
}

.view-toggle:hover {
  @apply text-slate-700;
}

.view-toggle.active {
  @apply bg-white text-indigo-600 shadow-sm;
}

/* 项目卡片 */
.project-card {
  @apply bg-white rounded-xl border border-slate-100 overflow-hidden;
  @apply transition-all duration-300 cursor-pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.project-card:hover {
  @apply border-indigo-200 -translate-y-1;
  box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.1), 0 10px 15px -5px rgba(0, 0, 0, 0.04);
}

/* 列表项 */
.project-list-item {
  @apply flex items-center gap-5 p-4 bg-white rounded-xl border border-slate-100;
  @apply transition-all duration-200 cursor-pointer;
}

.project-list-item:hover {
  @apply border-indigo-200;
  box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.05);
}

/* 操作按钮 */
.action-btn-light {
  @apply p-2.5 rounded-lg bg-white/90 backdrop-blur-sm text-slate-700;
  @apply hover:bg-white transition-colors cursor-pointer;
}

.action-btn-danger {
  @apply p-2.5 rounded-lg bg-red-500/90 backdrop-blur-sm text-white;
  @apply hover:bg-red-600 transition-colors cursor-pointer;
}

/* 按钮样式 */
.btn-primary {
  @apply inline-flex items-center gap-2;
  @apply bg-indigo-600 hover:bg-indigo-700 text-white;
  @apply font-semibold text-sm;
  @apply px-4 py-2.5 rounded-lg;
  @apply transition-all duration-200;
  @apply active:scale-[0.98];
  box-shadow: 0 0 20px -5px rgba(79, 70, 229, 0.3);
}

.btn-ghost {
  @apply inline-flex items-center gap-2;
  @apply text-slate-600 hover:text-slate-900;
  @apply hover:bg-slate-100;
  @apply font-medium text-sm;
  @apply px-4 py-2.5 rounded-lg;
  @apply transition-all;
}

/* 文字截断 */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 响应式动画 */
@media (prefers-reduced-motion: reduce) {
  .project-card,
  .project-list-item,
  .filter-chip,
  .view-toggle {
    transition: none !important;
  }
}
</style>
