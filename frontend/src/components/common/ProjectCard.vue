<script setup lang="ts">
/**
 * 项目卡片组件
 * 
 * 用法:
 * <ProjectCard :project="project" @click="handleClick" />
 */
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Film,
  MoreFilled,
  Edit,
  Delete,
  Share,
} from '@element-plus/icons-vue'
import type { Project } from '@/types'
import StatusBadge from './StatusBadge.vue'
import dayjs from 'dayjs'

const props = defineProps<{
  project: Project
}>()

const emit = defineEmits<{
  edit: [id: string]
  delete: [id: string]
  share: [id: string]
}>()

const router = useRouter()

// 状态映射
const badgeStatus = computed(() => {
  const map: Record<string, 'completed' | 'processing' | 'pending' | 'failed' | 'draft'> = {
    draft: 'draft',
    processing: 'processing',
    completed: 'completed',
    failed: 'failed',
  }
  return map[props.project.status] || 'draft'
})

// 格式化时间
const formattedDate = computed(() => {
  return dayjs(props.project.updated_at || props.project.created_at).format('MM/DD HH:mm')
})

// 进入项目编辑
function handleClick() {
  router.push(`/projects/${props.project.id}`)
}

// 获取缩略图
const thumbnail = computed(() => {
  // 可以从第一个场景获取缩略图
  return props.project.thumbnail || null
})
</script>

<template>
  <div
    class="project-card
      bg-white
      border border-slate-200 hover:border-indigo-300
      rounded-xl
      overflow-hidden
      transition-all duration-200
      hover:shadow-floating hover:-translate-y-0.5
      cursor-pointer
      group"
    @click="handleClick"
  >
    <!-- 封面图 -->
    <div class="aspect-video bg-slate-100 relative overflow-hidden">
      <img
        v-if="thumbnail"
        :src="thumbnail"
        class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
        alt=""
      />
      <div
        v-else
        class="absolute inset-0 flex items-center justify-center"
      >
        <el-icon class="w-12 h-12 text-slate-300">
          <Film />
        </el-icon>
      </div>
      
      <!-- 状态标签 -->
      <div class="absolute top-3 left-3">
        <StatusBadge :status="badgeStatus" />
      </div>
      
      <!-- 更多操作 -->
      <div
        class="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity"
        @click.stop
      >
        <el-dropdown trigger="click">
          <button class="w-8 h-8 bg-black/50 hover:bg-black/70 backdrop-blur-sm rounded-lg flex items-center justify-center transition-colors">
            <el-icon class="w-4 h-4 text-white">
              <MoreFilled />
            </el-icon>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="emit('edit', project.id)">
                <el-icon class="mr-2"><Edit /></el-icon>
                编辑
              </el-dropdown-item>
              <el-dropdown-item @click="emit('share', project.id)">
                <el-icon class="mr-2"><Share /></el-icon>
                分享
              </el-dropdown-item>
              <el-dropdown-item divided @click="emit('delete', project.id)">
                <el-icon class="mr-2 text-red-500"><Delete /></el-icon>
                <span class="text-red-500">删除</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <!-- 信息区 -->
    <div class="p-4">
      <!-- 标题 -->
      <h3 class="font-semibold text-slate-900 text-base mb-1 truncate">
        {{ project.title }}
      </h3>
      
      <!-- 描述 -->
      <p
        v-if="project.description"
        class="text-sm text-slate-500 mb-3 line-clamp-2"
      >
        {{ project.description }}
      </p>
      
      <!-- 元数据 -->
      <div class="flex items-center justify-between text-xs text-slate-400">
        <span>{{ formattedDate }}</span>
        <span v-if="project.scene_count">
          {{ project.scene_count }} 个场景
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.project-card {
  --shadow-floating: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
}

.project-card:hover {
  box-shadow: var(--shadow-floating);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

