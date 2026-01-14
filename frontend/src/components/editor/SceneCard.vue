<script setup lang="ts">
/**
 * 场景卡片组件 - StoryFlow Pro 设计风格
 * 
 * 用法:
 * <SceneCard :scene="scene" :index="1" />
 */
import { computed } from 'vue'
import {
  Picture,
  Loading,
  RefreshRight,
  Delete,
  Setting,
  VideoPlay,
  VideoPause,
} from '@element-plus/icons-vue'
import type { Scene } from '@/types'
import StatusBadge from '@/components/common/StatusBadge.vue'
import IconButton from '@/components/common/IconButton.vue'
import MetaTag from '@/components/common/MetaTag.vue'
import ProcessingOverlay from './ProcessingOverlay.vue'

const props = defineProps<{
  scene: Scene
  index?: number
}>()

const emit = defineEmits<{
  'regenerate-image': [sceneId: string]
  'regenerate-video': [sceneId: string]
  'edit': [sceneId: string]
  'delete': [sceneId: string]
}>()

// 是否正在生成
const isGenerating = computed(() => 
  props.scene.status === 'generating' || props.scene.status === 'processing'
)

// 状态映射到 StatusBadge
const badgeStatus = computed(() => {
  const map: Record<string, 'completed' | 'processing' | 'pending' | 'failed' | 'draft'> = {
    pending: 'pending',
    generating: 'processing',
    processing: 'processing',
    completed: 'completed',
    failed: 'failed',
  }
  return map[props.scene.status] || 'pending'
})

// 格式化时长
function formatDuration(seconds?: number): string {
  if (!seconds) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// 获取场景索引显示
const displayIndex = computed(() => {
  const idx = props.index ?? props.scene.scene_index ?? 1
  return String(idx).padStart(2, '0')
})
</script>

<template>
  <div
    class="scene-card
      bg-white
      border border-slate-200 hover:border-indigo-300
      rounded-xl
      p-1
      transition-all duration-200
      hover:shadow-floating hover:-translate-y-0.5
      group"
  >
    <div class="flex gap-6 p-4">
      <!-- 左侧媒体区 -->
      <div class="w-60 aspect-video flex-shrink-0 relative rounded-md overflow-hidden bg-slate-100 shadow-sm">
        <!-- 视频已生成 -->
        <template v-if="scene.video_url">
          <video
            :src="scene.video_url"
            class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
            :poster="scene.image_url"
          />
          <!-- 播放按钮 -->
          <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <button class="w-10 h-10 bg-white/90 rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform">
              <el-icon class="w-4 h-4 text-slate-900 ml-0.5">
                <VideoPlay />
              </el-icon>
            </button>
          </div>
        </template>
        
        <!-- 图片已生成 -->
        <template v-else-if="scene.image_url">
          <img
            :src="scene.image_url"
            class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
            alt="Scene image"
          />
          <!-- 悬停播放按钮 -->
          <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              class="w-10 h-10 bg-white/90 rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform"
              @click="emit('regenerate-image', scene.id)"
            >
              <el-icon class="w-4 h-4 text-slate-900">
                <RefreshRight />
              </el-icon>
            </button>
          </div>
        </template>
        
        <!-- 生成中状态 -->
        <template v-else-if="isGenerating">
          <ProcessingOverlay
            :progress="scene.progress || 0"
            message="Generating Assets..."
            :cancelable="true"
          />
        </template>
        
        <!-- 占位状态 -->
        <template v-else>
          <div class="absolute inset-0 flex flex-col items-center justify-center text-slate-400">
            <el-icon class="w-8 h-8 mb-2">
              <Picture />
            </el-icon>
            <span class="text-xs">待生成</span>
          </div>
        </template>
        
        <!-- 时长标签 -->
        <div
          v-if="scene.duration"
          class="absolute bottom-2 right-2 bg-black/70 backdrop-blur-sm text-white text-[10px] font-mono px-1.5 py-0.5 rounded"
        >
          {{ formatDuration(scene.duration) }}
        </div>
      </div>
      
      <!-- 右侧内容区 -->
      <div class="flex-1 flex flex-col min-w-0">
        <!-- 标题行 -->
        <div class="flex justify-between items-start mb-3">
          <div class="flex items-center gap-3">
            <!-- 拖拽手柄插槽 -->
            <slot name="drag-handle" />
            
            <!-- 序号 -->
            <div class="w-6 h-6 rounded bg-slate-100 text-slate-500 font-mono text-xs font-bold flex items-center justify-center border border-slate-200">
              {{ displayIndex }}
            </div>
            
            <!-- 标题/描述 -->
            <h3 class="font-semibold text-slate-900 text-base truncate max-w-xs">
              {{ scene.text || `场景 ${displayIndex}` }}
            </h3>
            
            <!-- 状态徽章 -->
            <StatusBadge :status="badgeStatus" />
          </div>
          
          <!-- 操作按钮组 - 悬停显示 -->
          <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <IconButton
              icon="RefreshRight"
              title="重新生成"
              @click="emit('regenerate-image', scene.id)"
            />
            <IconButton
              icon="Setting"
              title="设置"
              @click="emit('edit', scene.id)"
            />
            <IconButton
              icon="Delete"
              title="删除"
              variant="danger"
              @click="emit('delete', scene.id)"
            />
          </div>
        </div>
        
        <!-- Prompt 编辑区 -->
        <div class="relative group/prompt mb-3">
          <div
            class="prompt-block bg-slate-50 border border-slate-200 rounded-lg p-3
                   group-hover/prompt:border-indigo-200 group-hover/prompt:bg-indigo-50/10
                   transition-colors"
          >
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1.5">
              Visual Prompt
            </span>
            <p class="font-mono text-xs text-slate-600 leading-relaxed line-clamp-3">
              {{ scene.scene_description || scene.text || 'No prompt available' }}
            </p>
          </div>
          <!-- 左侧高亮条 -->
          <div class="absolute -left-3 top-0 bottom-0 w-1 bg-indigo-500 rounded-full opacity-0 group-hover/prompt:opacity-100 transition-opacity" />
        </div>
        
        <!-- 元数据标签 -->
        <div class="mt-auto flex items-center gap-3 flex-wrap">
          <!-- 镜头类型 -->
          <MetaTag
            v-if="scene.camera_type"
            icon="Camera"
            :text="scene.camera_type"
          />
          
          <!-- 情绪/氛围 -->
          <MetaTag
            v-if="scene.mood"
            icon="Sun"
            :text="scene.mood"
          />
          
          <!-- 角色 -->
          <template v-if="scene.characters?.length">
            <MetaTag
              v-for="char in scene.characters.slice(0, 2)"
              :key="char"
              icon="User"
              :text="char"
            />
            <span
              v-if="scene.characters.length > 2"
              class="text-[10px] text-slate-400"
            >
              +{{ scene.characters.length - 2 }}
            </span>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scene-card {
  --shadow-floating: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
}

.scene-card:hover {
  box-shadow: var(--shadow-floating);
}

/* 多行截断 */
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
