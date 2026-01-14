<!--
  可拖拽分镜列表组件
  
  使用 HTML5 Drag and Drop API 实现分镜排序
  
  Props:
    - scenes: 分镜数组
    - disabled: 是否禁用拖拽
    
  Events:
    - update:scenes: 顺序变化时触发
    - reorder: 排序完成时触发 (oldIndex, newIndex)
-->
<template>
  <div class="draggable-scene-list">
    <!-- 空状态 -->
    <div v-if="scenes.length === 0" class="empty-state">
      <el-empty description="暂无分镜">
        <slot name="empty-action" />
      </el-empty>
    </div>
    
    <!-- 分镜列表 -->
    <TransitionGroup v-else name="scene-list" tag="div" class="scene-list">
      <div
        v-for="(scene, index) in scenes"
        :key="scene.id"
        class="scene-item"
        :class="{ 
          dragging: dragIndex === index,
          'drop-above': dropIndex === index && dragIndex !== null && dragIndex > index,
          'drop-below': dropIndex === index && dragIndex !== null && dragIndex < index
        }"
        :draggable="!disabled"
        @dragstart="handleDragStart($event, index)"
        @dragenter="handleDragEnter($event, index)"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop($event, index)"
        @dragend="handleDragEnd"
      >
        <!-- 拖拽手柄 -->
        <div v-if="!disabled" class="drag-handle">
          <el-icon :size="20"><Rank /></el-icon>
        </div>
        
        <!-- 分镜内容 -->
        <div class="scene-content">
          <SceneCard
            :scene="scene"
            @regenerate-image="$emit('regenerate-image', scene.id)"
            @regenerate-video="$emit('regenerate-video', scene.id)"
          />
        </div>
        
        <!-- 序号显示 -->
        <div class="scene-number">{{ index + 1 }}</div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Rank } from '@element-plus/icons-vue'
import SceneCard from '@/components/editor/SceneCard.vue'
import type { Scene } from '@/types'

// ==================== Props & Emits ====================

const props = withDefaults(defineProps<{
  scenes: Scene[]
  disabled?: boolean
}>(), {
  disabled: false,
})

const emit = defineEmits<{
  'update:scenes': [scenes: Scene[]]
  'reorder': [oldIndex: number, newIndex: number]
  'regenerate-image': [sceneId: string]
  'regenerate-video': [sceneId: string]
}>()

// ==================== 拖拽状态 ====================

const dragIndex = ref<number | null>(null)
const dropIndex = ref<number | null>(null)

// ==================== 拖拽处理 ====================

function handleDragStart(e: DragEvent, index: number) {
  if (props.disabled) return
  
  dragIndex.value = index
  
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', String(index))
    
    // 自定义拖拽预览
    const target = e.target as HTMLElement
    const ghost = target.cloneNode(true) as HTMLElement
    ghost.style.opacity = '0.5'
    ghost.style.position = 'absolute'
    ghost.style.top = '-1000px'
    document.body.appendChild(ghost)
    e.dataTransfer.setDragImage(ghost, 0, 0)
    setTimeout(() => document.body.removeChild(ghost), 0)
  }
}

function handleDragEnter(e: DragEvent, index: number) {
  e.preventDefault()
  if (dragIndex.value === null || dragIndex.value === index) return
  dropIndex.value = index
}

function handleDragOver(e: DragEvent) {
  e.preventDefault()
  if (e.dataTransfer) {
    e.dataTransfer.dropEffect = 'move'
  }
}

function handleDragLeave(e: DragEvent) {
  // 检查是否真的离开了元素
  const relatedTarget = e.relatedTarget as HTMLElement
  const currentTarget = e.currentTarget as HTMLElement
  if (currentTarget.contains(relatedTarget)) return
}

function handleDrop(e: DragEvent, toIndex: number) {
  e.preventDefault()
  
  const fromIndex = dragIndex.value
  if (fromIndex === null || fromIndex === toIndex) {
    reset()
    return
  }
  
  // 重新排序
  const newScenes = [...props.scenes]
  const [movedItem] = newScenes.splice(fromIndex, 1)
  newScenes.splice(toIndex, 0, movedItem)
  
  // 更新 scene_index
  const updatedScenes = newScenes.map((scene, index) => ({
    ...scene,
    scene_index: index + 1,
  }))
  
  emit('update:scenes', updatedScenes)
  emit('reorder', fromIndex, toIndex)
  
  reset()
}

function handleDragEnd() {
  reset()
}

function reset() {
  dragIndex.value = null
  dropIndex.value = null
}
</script>

<style scoped>
.draggable-scene-list {
  position: relative;
}

.scene-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.scene-item {
  position: relative;
  display: flex;
  align-items: stretch;
  background: var(--el-bg-color);
  border-radius: 12px;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.scene-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.scene-item.dragging {
  opacity: 0.5;
  transform: scale(0.98);
}

.scene-item.drop-above {
  border-top-color: var(--el-color-primary);
}

.scene-item.drop-below {
  border-bottom-color: var(--el-color-primary);
}

.drag-handle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  cursor: grab;
  color: var(--el-text-color-placeholder);
  background: var(--el-fill-color-light);
  border-radius: 12px 0 0 12px;
  transition: all 0.2s;
}

.drag-handle:hover {
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.drag-handle:active {
  cursor: grabbing;
}

.scene-content {
  flex: 1;
  min-width: 0;
}

.scene-content :deep(.card) {
  border: none;
  box-shadow: none;
  border-radius: 0 12px 12px 0;
}

.scene-number {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-color-primary);
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.empty-state {
  padding: 60px 20px;
}

/* 列表动画 */
.scene-list-move,
.scene-list-enter-active,
.scene-list-leave-active {
  transition: all 0.3s ease;
}

.scene-list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.scene-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.scene-list-leave-active {
  position: absolute;
  width: 100%;
}
</style>

