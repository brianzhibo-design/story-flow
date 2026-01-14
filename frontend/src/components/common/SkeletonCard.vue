<script setup lang="ts">
/**
 * 场景卡片骨架屏组件
 * 
 * 用法:
 * <SkeletonCard />
 * <SkeletonCard v-for="i in 3" :key="i" />
 */

interface Props {
  /** 是否显示动画 */
  animated?: boolean
}

withDefaults(defineProps<Props>(), {
  animated: true,
})
</script>

<template>
  <div class="scene-card-skeleton bg-white border border-slate-200 rounded-xl p-1">
    <div class="flex gap-6 p-4">
      <!-- 左侧媒体占位 -->
      <div
        :class="[
          'w-60 aspect-video flex-shrink-0 rounded-md',
          { 'shimmer-bg': animated },
          { 'bg-slate-100': !animated },
        ]"
      />
      
      <!-- 右侧内容占位 -->
      <div class="flex-1 flex flex-col min-w-0">
        <!-- 标题行 -->
        <div class="flex items-center gap-3 mb-4">
          <div
            :class="[
              'w-6 h-6 rounded',
              { 'shimmer-bg': animated },
              { 'bg-slate-100': !animated },
            ]"
          />
          <div
            :class="[
              'h-5 w-40 rounded',
              { 'shimmer-bg': animated },
              { 'bg-slate-100': !animated },
            ]"
          />
          <div
            :class="[
              'h-5 w-20 rounded-full',
              { 'shimmer-bg': animated },
              { 'bg-slate-100': !animated },
            ]"
          />
        </div>
        
        <!-- Prompt 区域占位 -->
        <div
          :class="[
            'h-24 rounded-lg mb-4',
            { 'shimmer-bg': animated },
            { 'bg-slate-100': !animated },
          ]"
        />
        
        <!-- 元数据标签占位 -->
        <div class="mt-auto flex gap-3">
          <div
            :class="[
              'h-6 w-20 rounded',
              { 'shimmer-bg': animated },
              { 'bg-slate-100': !animated },
            ]"
          />
          <div
            :class="[
              'h-6 w-24 rounded',
              { 'shimmer-bg': animated },
              { 'bg-slate-100': !animated },
            ]"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.shimmer-bg {
  background: #f6f7f8;
  background-image: linear-gradient(
    to right,
    #f6f7f8 0%,
    #e2e8f0 20%,
    #f6f7f8 40%,
    #f6f7f8 100%
  );
  background-repeat: no-repeat;
  background-size: 1000px 100%;
  animation: shimmer 2s infinite linear;
}

@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}
</style>

