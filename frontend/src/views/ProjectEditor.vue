<template>
  <div class="min-h-screen bg-slate-50">
    <!-- 毛玻璃头部 -->
    <header class="h-16 sticky top-0 z-30 flex items-center justify-between px-8 bg-white/85 backdrop-blur-xl border-b border-slate-200">
      <!-- 左侧 -->
      <div class="flex items-center gap-4">
        <button
          class="p-2 rounded-lg text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          @click="$router.push('/dashboard')"
        >
          <el-icon class="w-5 h-5"><ArrowLeft /></el-icon>
        </button>
        
        <div class="flex items-center gap-3">
          <h1 class="text-lg font-semibold text-slate-900 truncate max-w-md">
            {{ project?.title || '加载中...' }}
          </h1>
          <StatusBadge :status="badgeStatus" />
        </div>
      </div>
      
      <!-- 右侧操作 -->
      <div class="flex items-center gap-3">
        <!-- 生成按钮 -->
        <el-dropdown v-if="project?.status === 'draft'" split-button @click="handleGenerate()">
          <template #default>
            <span class="flex items-center gap-2 font-semibold text-xs">
              <el-icon class="w-4 h-4"><MagicStick /></el-icon>
              开始生成
            </span>
          </template>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleGenerate(['storyboard'])">
                <el-icon class="mr-2"><Document /></el-icon>
                仅生成分镜
              </el-dropdown-item>
              <el-dropdown-item @click="handleGenerate(['storyboard', 'image'])">
                <el-icon class="mr-2"><Picture /></el-icon>
                生成分镜和图片
              </el-dropdown-item>
              <el-dropdown-item @click="handleGenerate()">
                <el-icon class="mr-2"><VideoCamera /></el-icon>
                全部生成
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        
        <!-- 导出按钮 -->
        <button
          v-if="project?.status === 'completed'"
          class="btn-primary"
        >
          <el-icon class="w-4 h-4"><Download /></el-icon>
          Export Video
        </button>
      </div>
    </header>
    
    <!-- 主内容 -->
    <main class="max-w-7xl mx-auto px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <!-- 左侧：分镜列表 -->
        <div class="lg:col-span-3">
          <!-- 进度条 -->
          <div v-if="isProcessing" class="card-hover p-6 mb-6">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                  <el-icon class="w-4 h-4 text-orange-600 animate-spin"><Loading /></el-icon>
                </div>
                <span class="text-sm font-medium text-slate-900">生成进度</span>
              </div>
              <span class="text-sm font-bold text-indigo-600">{{ progress }}%</span>
            </div>
            <div class="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
              <div
                class="h-full bg-indigo-600 transition-all duration-500 ease-out"
                :style="{ width: `${progress}%` }"
              />
            </div>
            <p v-if="currentTask" class="text-xs text-slate-500 mt-3">
              {{ currentTask.progress_message || '处理中...' }}
            </p>
          </div>
          
          <!-- 分镜列表 -->
          <div v-if="scenes.length > 0" class="space-y-4">
            <SceneCard
              v-for="(scene, idx) in scenes"
              :key="scene.id"
              :scene="scene"
              :index="idx + 1"
              @regenerate-image="handleRegenerateImage"
              @regenerate-video="handleRegenerateVideo"
              @edit="handleEditScene"
              @delete="handleDeleteScene"
            />
          </div>
          
          <!-- 加载状态 -->
          <div v-else-if="loading" class="space-y-4">
            <SkeletonCard v-for="i in 3" :key="i" />
          </div>
          
          <!-- 空状态 -->
          <EmptyState
            v-else
            icon="Document"
            title="还没有分镜"
            description="点击「开始生成」按钮，AI 将自动分析故事并生成分镜"
          />
        </div>
        
        <!-- 右侧：信息面板 -->
        <div class="space-y-6">
          <!-- 项目信息 -->
          <div class="bg-white border border-slate-200 rounded-xl p-5">
            <h3 class="text-sm font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <el-icon class="w-4 h-4 text-slate-400"><InfoFilled /></el-icon>
              项目信息
            </h3>
            <div class="space-y-3">
              <div class="flex justify-between text-sm">
                <span class="text-slate-500">分镜数量</span>
                <span class="font-medium text-slate-900">{{ scenes.length }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-slate-500">已完成</span>
                <span class="font-medium text-emerald-600">{{ completedCount }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-slate-500">总时长</span>
                <span class="font-mono text-slate-900">{{ formatDuration(totalDuration) }}</span>
              </div>
            </div>
          </div>
          
          <!-- 故事文本 -->
          <div class="bg-white border border-slate-200 rounded-xl p-5">
            <h3 class="text-sm font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <el-icon class="w-4 h-4 text-slate-400"><Document /></el-icon>
              故事文本
            </h3>
            <p class="text-sm text-slate-600 whitespace-pre-wrap line-clamp-10 leading-relaxed">
              {{ project?.story_text }}
            </p>
            <button
              v-if="(project?.story_text?.length || 0) > 200"
              class="text-xs font-medium text-indigo-600 hover:text-indigo-700 mt-3"
              @click="showFullText = true"
            >
              查看全文 →
            </button>
          </div>
          
          <!-- 任务队列 -->
          <div v-if="tasks.length > 0" class="bg-white border border-slate-200 rounded-xl p-5">
            <h3 class="text-sm font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <el-icon class="w-4 h-4 text-slate-400"><List /></el-icon>
              任务队列
            </h3>
            <div class="space-y-2 max-h-60 overflow-y-auto">
              <div
                v-for="task in tasks"
                :key="task.id"
                class="flex items-center justify-between text-sm py-2 border-b border-slate-100 last:border-0"
              >
                <span class="text-slate-600">{{ taskTypeText(task.type) }}</span>
                <StatusBadge
                  :status="taskBadgeStatus(task.status)"
                  :text="taskStatusText(task.status)"
                  :show-dot="task.status === 'running'"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <!-- 全文弹窗 -->
    <el-dialog
      v-model="showFullText"
      title="故事全文"
      width="600"
      :close-on-click-modal="true"
    >
      <p class="whitespace-pre-wrap text-slate-700 leading-relaxed">
        {{ project?.story_text }}
      </p>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  ArrowLeft, Download, Document, Loading,
  Picture, VideoCamera, MagicStick, InfoFilled, List,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useProjectStore } from '@/stores'
import { useWebSocket } from '@/composables/useWebSocket'
import { SceneCard } from '@/components/editor'
import { StatusBadge, SkeletonCard, EmptyState } from '@/components/common'

const route = useRoute()
const projectStore = useProjectStore()

const projectId = route.params.id as string
const showFullText = ref(false)

// WebSocket 连接
useWebSocket(projectId)

// 计算属性
const project = computed(() => projectStore.currentProject)
const scenes = computed(() => projectStore.scenes)
const tasks = computed(() => projectStore.tasks)
const loading = computed(() => projectStore.loading)
const isProcessing = computed(() => projectStore.isProcessing)
const progress = computed(() => projectStore.progress)

const completedCount = computed(() => 
  scenes.value.filter(s => s.status === 'completed').length
)

const totalDuration = computed(() => 
  scenes.value.reduce((sum, s) => sum + (s.duration || 0), 0)
)

const currentTask = computed(() => 
  tasks.value.find(t => t.status === 'running')
)

// 状态映射
const badgeStatus = computed(() => {
  const map: Record<string, 'completed' | 'processing' | 'pending' | 'failed' | 'draft'> = {
    draft: 'draft',
    processing: 'processing',
    completed: 'completed',
    failed: 'failed',
  }
  return map[project.value?.status || ''] || 'draft'
})

function taskBadgeStatus(status: string): 'completed' | 'processing' | 'pending' | 'failed' | 'queued' | 'running' {
  const map: Record<string, 'completed' | 'processing' | 'pending' | 'failed' | 'queued' | 'running'> = {
    pending: 'pending',
    queued: 'queued',
    running: 'running',
    completed: 'completed',
    failed: 'failed',
  }
  return map[status] || 'pending'
}

// 生命周期
onMounted(() => {
  projectStore.fetchProject(projectId)
})

onUnmounted(() => {
  projectStore.clearCurrent()
})

// 方法
function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

async function handleGenerate(steps?: string[]) {
  try {
    await projectStore.generate(projectId, steps)
    ElMessage.success('已开始生成')
  } catch (error) {
    const err = error as Error
    ElMessage.error(err.message || '启动失败')
  }
}

async function handleRegenerateImage(sceneId: string) {
  ElMessage.info(`重新生成图片: ${sceneId}`)
}

async function handleRegenerateVideo(sceneId: string) {
  ElMessage.info(`重新生成视频: ${sceneId}`)
}

function handleEditScene(sceneId: string) {
  ElMessage.info(`编辑场景: ${sceneId}`)
}

function handleDeleteScene(sceneId: string) {
  ElMessage.info(`删除场景: ${sceneId}`)
}

function taskTypeText(type: string) {
  const map: Record<string, string> = {
    storyboard: '分镜生成',
    image: '图片生成',
    video: '视频生成',
    compose: '视频合成',
  }
  return map[type] || type
}

function taskStatusText(status: string) {
  const map: Record<string, string> = {
    pending: 'Pending',
    queued: 'Queued',
    running: 'Running',
    completed: 'Done',
    failed: 'Failed',
  }
  return map[status] || status
}
</script>

<style scoped>
.card-hover {
  @apply bg-white border border-slate-200 rounded-xl;
  transition: all 0.2s;
}

.card-hover:hover {
  @apply border-indigo-300 -translate-y-0.5;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
}

.btn-primary {
  @apply inline-flex items-center gap-2;
  @apply bg-indigo-600 hover:bg-indigo-700 text-white;
  @apply font-semibold text-xs;
  @apply px-4 py-2.5 rounded-lg;
  @apply transition-all;
  box-shadow: 0 0 20px -5px rgba(79, 70, 229, 0.3);
}

.btn-primary:active {
  transform: scale(0.98);
}

.line-clamp-10 {
  display: -webkit-box;
  -webkit-line-clamp: 10;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
