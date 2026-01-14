<template>
  <el-config-provider :locale="zhCn">
    <!-- 加载中状态 -->
    <div v-if="initializing" class="app-loading">
      <div class="loading-spinner">
        <el-icon :size="48" class="is-loading"><Loading /></el-icon>
        <p>加载中...</p>
      </div>
    </div>
    
    <!-- 主内容 -->
    <router-view v-else v-slot="{ Component, route }">
      <transition name="fade" mode="out-in">
        <keep-alive :include="cachedViews">
          <component :is="Component" :key="route.path" />
        </keep-alive>
      </transition>
    </router-view>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { useUserStore } from '@/stores'

const route = useRoute()
const userStore = useUserStore()

const initializing = ref(true)

// 需要缓存的视图
const cachedViews = computed(() => {
  const views: string[] = []
  if (route.meta.keepAlive) {
    views.push(route.name as string)
  }
  return views
})

onMounted(async () => {
  try {
    // 初始化用户状态
    await userStore.init()
  } finally {
    initializing.value = false
  }
})
</script>

<style>
.app-loading {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.loading-spinner {
  text-align: center;
  color: white;
}

.loading-spinner p {
  margin-top: 16px;
  font-size: 16px;
  opacity: 0.9;
}

/* 页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
