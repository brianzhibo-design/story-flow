<!--
  骨架屏组件
  
  用于页面加载时显示占位内容
  
  使用方式:
  <Skeleton type="card" />
  <Skeleton type="list" :rows="5" />
  <Skeleton type="scene" />
  <Skeleton type="custom">
    <template #default>
      自定义骨架内容
    </template>
  </Skeleton>
-->
<template>
  <div class="skeleton-wrapper" :class="[`skeleton-${type}`, { animated }]">
    <!-- 卡片类型 -->
    <template v-if="type === 'card'">
      <div class="skeleton-card" v-for="i in count" :key="i">
        <div class="skeleton-image skeleton-animate" />
        <div class="skeleton-content">
          <div class="skeleton-title skeleton-animate" />
          <div class="skeleton-text skeleton-animate" />
          <div class="skeleton-text skeleton-animate short" />
        </div>
      </div>
    </template>
    
    <!-- 列表类型 -->
    <template v-else-if="type === 'list'">
      <div class="skeleton-list-item" v-for="i in rows" :key="i">
        <div class="skeleton-avatar skeleton-animate" v-if="avatar" />
        <div class="skeleton-list-content">
          <div class="skeleton-title skeleton-animate" />
          <div class="skeleton-text skeleton-animate" />
        </div>
      </div>
    </template>
    
    <!-- 分镜类型 -->
    <template v-else-if="type === 'scene'">
      <div class="skeleton-scene" v-for="i in count" :key="i">
        <div class="skeleton-scene-image skeleton-animate" />
        <div class="skeleton-scene-content">
          <div class="skeleton-scene-header">
            <div class="skeleton-badge skeleton-animate" />
            <div class="skeleton-badge skeleton-animate" />
            <div class="skeleton-badge skeleton-animate" />
          </div>
          <div class="skeleton-text skeleton-animate" style="width: 100%" />
          <div class="skeleton-text skeleton-animate" style="width: 80%" />
          <div class="skeleton-text skeleton-animate" style="width: 60%" />
          <div class="skeleton-scene-tags">
            <div class="skeleton-tag skeleton-animate" v-for="j in 3" :key="j" />
          </div>
        </div>
      </div>
    </template>
    
    <!-- 项目卡片类型 -->
    <template v-else-if="type === 'project'">
      <div class="skeleton-project" v-for="i in count" :key="i">
        <div class="skeleton-project-image skeleton-animate" />
        <div class="skeleton-project-content">
          <div class="skeleton-title skeleton-animate" />
          <div class="skeleton-text skeleton-animate" style="width: 70%" />
          <div class="skeleton-project-footer">
            <div class="skeleton-text skeleton-animate" style="width: 30%" />
            <div class="skeleton-text skeleton-animate" style="width: 20%" />
          </div>
        </div>
      </div>
    </template>
    
    <!-- 表格类型 -->
    <template v-else-if="type === 'table'">
      <div class="skeleton-table">
        <div class="skeleton-table-header skeleton-animate" />
        <div class="skeleton-table-row" v-for="i in rows" :key="i">
          <div class="skeleton-table-cell skeleton-animate" v-for="j in columns" :key="j" />
        </div>
      </div>
    </template>
    
    <!-- 自定义 -->
    <template v-else-if="type === 'custom'">
      <slot />
    </template>
    
    <!-- 默认 (块) -->
    <template v-else>
      <div 
        class="skeleton-block skeleton-animate" 
        :style="{ width, height }"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  /** 骨架类型 */
  type?: 'block' | 'card' | 'list' | 'scene' | 'project' | 'table' | 'custom'
  /** 动画效果 */
  animated?: boolean
  /** 显示数量 (card/scene/project) */
  count?: number
  /** 行数 (list/table) */
  rows?: number
  /** 列数 (table) */
  columns?: number
  /** 是否显示头像 (list) */
  avatar?: boolean
  /** 宽度 (block) */
  width?: string
  /** 高度 (block) */
  height?: string
}>(), {
  type: 'block',
  animated: true,
  count: 3,
  rows: 3,
  columns: 4,
  avatar: true,
  width: '100%',
  height: '100px',
})
</script>

<style scoped>
.skeleton-wrapper {
  width: 100%;
}

/* 动画效果 */
.skeleton-animate {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
  border-radius: 4px;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 暗色模式 */
.dark .skeleton-animate {
  background: linear-gradient(90deg, #2d2d2d 25%, #3d3d3d 50%, #2d2d2d 75%);
  background-size: 200% 100%;
}

/* 块类型 */
.skeleton-block {
  border-radius: 8px;
}

/* 卡片类型 */
.skeleton-card {
  background: var(--el-bg-color);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 16px;
}

.skeleton-card .skeleton-image {
  width: 100%;
  height: 180px;
}

.skeleton-card .skeleton-content {
  padding: 16px;
}

.skeleton-card .skeleton-title {
  height: 20px;
  width: 60%;
  margin-bottom: 12px;
}

.skeleton-card .skeleton-text {
  height: 14px;
  width: 100%;
  margin-bottom: 8px;
}

.skeleton-card .skeleton-text.short {
  width: 40%;
}

/* 列表类型 */
.skeleton-list-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.skeleton-list-item:last-child {
  border-bottom: none;
}

.skeleton-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  flex-shrink: 0;
}

.skeleton-list-content {
  flex: 1;
}

.skeleton-list-content .skeleton-title {
  height: 16px;
  width: 30%;
  margin-bottom: 8px;
}

.skeleton-list-content .skeleton-text {
  height: 14px;
  width: 60%;
}

/* 分镜类型 */
.skeleton-scene {
  display: flex;
  gap: 24px;
  padding: 20px;
  background: var(--el-bg-color);
  border-radius: 12px;
  margin-bottom: 16px;
}

.skeleton-scene-image {
  width: 256px;
  height: 144px;
  border-radius: 8px;
  flex-shrink: 0;
}

.skeleton-scene-content {
  flex: 1;
}

.skeleton-scene-header {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.skeleton-badge {
  width: 48px;
  height: 24px;
  border-radius: 4px;
}

.skeleton-scene-tags {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.skeleton-tag {
  width: 60px;
  height: 22px;
  border-radius: 4px;
}

/* 项目卡片类型 */
.skeleton-project {
  background: var(--el-bg-color);
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 16px;
}

.skeleton-project-image {
  width: 100%;
  aspect-ratio: 16/9;
}

.skeleton-project-content {
  padding: 20px;
}

.skeleton-project-content .skeleton-title {
  height: 22px;
  width: 70%;
  margin-bottom: 12px;
}

.skeleton-project-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}

/* 表格类型 */
.skeleton-table {
  background: var(--el-bg-color);
  border-radius: 8px;
  overflow: hidden;
}

.skeleton-table-header {
  height: 48px;
  background: var(--el-fill-color-light);
}

.skeleton-table-row {
  display: flex;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.skeleton-table-row:last-child {
  border-bottom: none;
}

.skeleton-table-cell {
  flex: 1;
  height: 14px;
  margin: 16px;
}

.skeleton-text {
  height: 14px;
  margin-bottom: 8px;
}
</style>

