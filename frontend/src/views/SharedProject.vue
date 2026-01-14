<template>
  <div class="shared-project-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-icon class="loading-icon" :size="48"><Loading /></el-icon>
      <p>正在加载项目...</p>
    </div>
    
    <!-- 密码输入 -->
    <el-card v-else-if="needPassword" class="password-card" shadow="never">
      <div class="password-content">
        <el-icon :size="48" color="var(--el-color-warning)"><Lock /></el-icon>
        <h2>此项目需要密码访问</h2>
        <p>请输入分享密码以查看内容</p>
        
        <el-input
          v-model="password"
          type="password"
          placeholder="请输入访问密码"
          size="large"
          show-password
          @keyup.enter="accessProject"
        />
        
        <el-button 
          type="primary" 
          size="large" 
          :loading="accessing"
          @click="accessProject"
        >
          确认访问
        </el-button>
        
        <p v-if="passwordError" class="error-text">密码错误，请重试</p>
      </div>
    </el-card>
    
    <!-- 错误状态 -->
    <el-card v-else-if="error" class="error-card" shadow="never">
      <el-result
        icon="warning"
        :title="errorTitle"
        :sub-title="errorMessage"
      >
        <template #extra>
          <el-button type="primary" @click="goHome">返回首页</el-button>
        </template>
      </el-result>
    </el-card>
    
    <!-- 项目内容 -->
    <div v-else-if="project" class="project-content">
      <!-- 顶部信息栏 -->
      <div class="project-header">
        <div class="project-info">
          <h1 class="project-title">{{ project.title }}</h1>
          <div class="project-meta">
            <el-tag :type="permissionTagType" size="small">
              {{ permissionText }}
            </el-tag>
          </div>
        </div>
        
        <div class="header-actions">
          <el-button 
            v-if="permissions.can_download" 
            type="primary"
            @click="handleDownload"
          >
            <el-icon><Download /></el-icon>
            下载
          </el-button>
        </div>
      </div>
      
      <!-- 项目预览区域 -->
      <div class="project-preview">
        <el-empty description="项目预览区域（待实现）">
          <template #image>
            <el-icon :size="64" color="var(--el-text-color-secondary)">
              <VideoPlay />
            </el-icon>
          </template>
        </el-empty>
      </div>
      
      <!-- 评论区域 (如果有评论权限) -->
      <div v-if="permissions.can_comment" class="comments-section">
        <h3>评论</h3>
        <p class="coming-soon">评论功能即将上线</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Loading, Lock, Download, VideoPlay } from '@element-plus/icons-vue'
import { shareApi, type SharedProjectAccess } from '@/api/share'

const route = useRoute()
const router = useRouter()

// 状态
const loading = ref(true)
const accessing = ref(false)
const needPassword = ref(false)
const password = ref('')
const passwordError = ref(false)
const error = ref(false)
const errorTitle = ref('')
const errorMessage = ref('')
const project = ref<SharedProjectAccess['project'] | null>(null)
const permissions = ref<SharedProjectAccess['permissions']>({
  type: 'view',
  can_view: false,
  can_comment: false,
  can_edit: false,
  can_download: false
})

// 分享码
const shareCode = computed(() => route.params.shareCode as string)

// 权限显示
const permissionText = computed(() => {
  const map = { view: '仅查看', comment: '可评论', edit: '可编辑' }
  return map[permissions.value.type] || '查看'
})

const permissionTagType = computed(() => {
  const map = { view: 'info', comment: 'warning', edit: 'success' }
  return map[permissions.value.type] || 'info'
})

// 加载项目
onMounted(async () => {
  await accessProject()
})

async function accessProject() {
  if (needPassword.value && !password.value) {
    passwordError.value = true
    return
  }
  
  loading.value = !needPassword.value
  accessing.value = needPassword.value
  passwordError.value = false
  
  try {
    const res = await shareApi.access(shareCode.value, password.value || undefined)
    project.value = res.data.data.project
    permissions.value = res.data.data.permissions
    needPassword.value = false
    error.value = false
  } catch (err: any) {
    const status = err.response?.status
    const detail = err.response?.data?.detail
    
    if (status === 401 && detail === '需要密码') {
      needPassword.value = true
      error.value = false
    } else if (status === 401 && detail === '密码错误') {
      passwordError.value = true
    } else if (status === 404) {
      error.value = true
      errorTitle.value = '分享链接不存在'
      errorMessage.value = '该链接可能已被删除或从未存在'
    } else if (status === 410) {
      error.value = true
      errorTitle.value = '分享链接已失效'
      errorMessage.value = detail || '该链接已过期或访问次数已达上限'
    } else {
      error.value = true
      errorTitle.value = '加载失败'
      errorMessage.value = detail || '无法加载项目内容，请稍后重试'
    }
  } finally {
    loading.value = false
    accessing.value = false
  }
}

function handleDownload() {
  // TODO: 实现下载功能
}

function goHome() {
  router.push('/')
}
</script>

<style scoped>
.shared-project-page {
  min-height: 100vh;
  background: var(--el-fill-color-lighter);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  gap: 16px;
  color: var(--el-text-color-secondary);
}

.loading-icon {
  animation: spin 1.5s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.password-card,
.error-card {
  max-width: 400px;
  margin: 100px auto;
  border-radius: 16px;
}

.password-content {
  text-align: center;
  padding: 24px;
}

.password-content h2 {
  margin: 16px 0 8px;
}

.password-content p {
  color: var(--el-text-color-secondary);
  margin-bottom: 24px;
}

.password-content .el-input {
  margin-bottom: 16px;
}

.password-content .el-button {
  width: 100%;
}

.error-text {
  color: var(--el-color-danger);
  font-size: 14px;
  margin-top: 12px;
}

.project-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.project-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 12px;
}

.project-meta {
  display: flex;
  gap: 8px;
}

.project-preview {
  background: var(--el-bg-color);
  border-radius: 16px;
  padding: 80px 40px;
  margin-bottom: 32px;
}

.comments-section {
  background: var(--el-bg-color);
  border-radius: 16px;
  padding: 24px;
}

.comments-section h3 {
  margin: 0 0 16px;
}

.coming-soon {
  color: var(--el-text-color-secondary);
  text-align: center;
  padding: 40px;
}
</style>

