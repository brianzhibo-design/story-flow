<!--
  错误边界组件
  
  用于捕获子组件的错误，防止整个应用崩溃
  
  使用方式:
  <ErrorBoundary>
    <SomeComponent />
  </ErrorBoundary>
-->
<template>
  <div v-if="hasError" class="error-boundary">
    <div class="error-content">
      <el-icon :size="64" class="error-icon">
        <WarningFilled />
      </el-icon>
      <h3 class="error-title">页面出现错误</h3>
      <p class="error-message">{{ errorMessage }}</p>
      <div class="error-actions">
        <el-button type="primary" @click="handleRetry">
          <el-icon class="mr-1"><RefreshRight /></el-icon>
          重试
        </el-button>
        <el-button @click="handleGoHome">
          <el-icon class="mr-1"><HomeFilled /></el-icon>
          返回首页
        </el-button>
      </div>
      <div v-if="showDetails" class="error-details">
        <el-collapse>
          <el-collapse-item title="错误详情" name="1">
            <pre>{{ errorStack }}</pre>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </div>
  <slot v-else />
</template>

<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'
import { useRouter } from 'vue-router'
import { WarningFilled, RefreshRight, HomeFilled } from '@element-plus/icons-vue'

// Props
const props = withDefaults(defineProps<{
  /** 是否显示错误详情 */
  showDetails?: boolean
  /** 自定义错误消息 */
  fallbackMessage?: string
}>(), {
  showDetails: import.meta.env.DEV,
  fallbackMessage: '抱歉，页面加载出现问题。请尝试刷新页面或返回首页。',
})

// Emits
const emit = defineEmits<{
  error: [error: Error, info: string]
}>()

const router = useRouter()

// 状态
const hasError = ref(false)
const error = ref<Error | null>(null)
const errorInfo = ref<string>('')

// 计算属性
const errorMessage = ref(props.fallbackMessage)
const errorStack = ref('')

// 捕获错误
onErrorCaptured((err: Error, instance, info: string) => {
  hasError.value = true
  error.value = err
  errorInfo.value = info
  errorMessage.value = err.message || props.fallbackMessage
  errorStack.value = err.stack || ''
  
  // 上报错误
  console.error('[ErrorBoundary] Captured error:', err)
  console.error('[ErrorBoundary] Error info:', info)
  
  emit('error', err, info)
  
  // 阻止错误向上传播
  return false
})

// 重试
function handleRetry() {
  hasError.value = false
  error.value = null
  errorInfo.value = ''
}

// 返回首页
function handleGoHome() {
  hasError.value = false
  error.value = null
  router.push('/')
}
</script>

<style scoped>
.error-boundary {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 40px;
}

.error-content {
  text-align: center;
  max-width: 500px;
}

.error-icon {
  color: var(--el-color-danger);
  margin-bottom: 16px;
}

.error-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin: 0 0 12px;
}

.error-message {
  font-size: 15px;
  color: var(--el-text-color-secondary);
  margin: 0 0 24px;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.error-details {
  margin-top: 24px;
  text-align: left;
}

.error-details pre {
  font-size: 12px;
  line-height: 1.5;
  background: var(--el-fill-color-light);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>

