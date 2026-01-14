<!--
  虚拟滚动分镜列表
  
  使用 @vueuse/core 的 useVirtualList 实现高性能渲染
  
  Props:
    - scenes: 分镜数组
    - itemHeight: 每项高度 (默认 220)
    - overscan: 预渲染数量 (默认 3)
-->
<template>
  <div class="virtual-scene-list">
    <!-- 空状态 -->
    <div v-if="scenes.length === 0" class="empty-state">
      <el-empty description="暂无分镜">
        <slot name="empty-action" />
      </el-empty>
    </div>
    
    <!-- 虚拟列表 -->
    <div v-else ref="containerRef" class="list-container" :style="{ height: `${containerHeight}px` }">
      <div ref="wrapperRef" class="list-wrapper" :style="{ transform: `translateY(${offsetTop}px)` }">
        <div
          v-for="item in visibleItems"
          :key="item.data.id"
          class="list-item"
          :style="{ height: `${itemHeight}px` }"
        >
          <SceneCard
            :scene="item.data"
            @regenerate-image="$emit('regenerate-image', item.data.id)"
            @regenerate-video="$emit('regenerate-video', item.data.id)"
          />
        </div>
      </div>
    </div>
    
    <!-- 滚动提示 -->
    <div v-if="scenes.length > 10" class="scroll-hint">
      共 {{ scenes.length }} 个分镜，显示 {{ startIndex + 1 }}-{{ endIndex }} 个
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import SceneCard from '@/components/editor/SceneCard.vue'
import type { Scene } from '@/types'

// ==================== Props & Emits ====================

const props = withDefaults(defineProps<{
  scenes: Scene[]
  itemHeight?: number
  containerHeight?: number
  overscan?: number
}>(), {
  itemHeight: 220,
  containerHeight: 600,
  overscan: 3,
})

defineEmits<{
  'regenerate-image': [sceneId: string]
  'regenerate-video': [sceneId: string]
}>()

// ==================== 状态 ====================

const containerRef = ref<HTMLElement | null>(null)
const wrapperRef = ref<HTMLElement | null>(null)
const scrollTop = ref(0)

// ==================== 计算属性 ====================

/** 总高度 */
const totalHeight = computed(() => props.scenes.length * props.itemHeight)

/** 可见区域能显示的数量 */
const visibleCount = computed(() => Math.ceil(props.containerHeight / props.itemHeight))

/** 开始索引 */
const startIndex = computed(() => {
  const start = Math.floor(scrollTop.value / props.itemHeight) - props.overscan
  return Math.max(0, start)
})

/** 结束索引 */
const endIndex = computed(() => {
  const end = startIndex.value + visibleCount.value + props.overscan * 2
  return Math.min(props.scenes.length, end)
})

/** 可见项 */
const visibleItems = computed(() => {
  return props.scenes.slice(startIndex.value, endIndex.value).map((scene, index) => ({
    data: scene,
    index: startIndex.value + index,
  }))
})

/** 偏移量 */
const offsetTop = computed(() => startIndex.value * props.itemHeight)

// ==================== 方法 ====================

function handleScroll(e: Event) {
  const target = e.target as HTMLElement
  scrollTop.value = target.scrollTop
}

// ==================== 滚动到指定分镜 ====================

function scrollToScene(sceneId: string) {
  const index = props.scenes.findIndex(s => s.id === sceneId)
  if (index !== -1 && containerRef.value) {
    containerRef.value.scrollTop = index * props.itemHeight
  }
}

// ==================== 生命周期 ====================

onMounted(() => {
  if (containerRef.value) {
    containerRef.value.addEventListener('scroll', handleScroll)
  }
})

onUnmounted(() => {
  if (containerRef.value) {
    containerRef.value.removeEventListener('scroll', handleScroll)
  }
})

// 暴露方法
defineExpose({
  scrollToScene,
})
</script>

<style scoped>
.virtual-scene-list {
  position: relative;
}

.list-container {
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
}

.list-wrapper {
  position: relative;
  will-change: transform;
}

.list-item {
  padding-bottom: 16px;
}

.empty-state {
  padding: 60px 20px;
}

.scroll-hint {
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px 16px;
  background: var(--el-bg-color);
  border-top: 1px solid var(--el-border-color-lighter);
  font-size: 12px;
  color: var(--el-text-color-secondary);
  text-align: center;
}
</style>

