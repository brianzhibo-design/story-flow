<script setup lang="ts">
/**
 * 项目卡片骨架屏
 */
</script>

<template>
  <div class="skeleton-project-card bg-white border border-slate-200 rounded-xl overflow-hidden">
    <!-- 封面占位 -->
    <div class="aspect-video shimmer-bg" />
    
    <!-- 信息区占位 -->
    <div class="p-4 space-y-3">
      <div class="h-5 w-3/4 rounded shimmer-bg" />
      <div class="h-4 w-full rounded shimmer-bg" />
      <div class="flex justify-between">
        <div class="h-4 w-16 rounded shimmer-bg" />
        <div class="h-4 w-20 rounded shimmer-bg" />
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

