<template>
  <el-dialog 
    v-model="visible" 
    title="分享项目" 
    width="520px"
    :close-on-click-modal="false"
  >
    <!-- 创建分享表单 -->
    <el-form 
      ref="formRef" 
      :model="shareForm" 
      label-width="80px"
      class="share-form"
    >
      <el-form-item label="权限类型">
        <el-radio-group v-model="shareForm.share_type">
          <el-radio value="view">
            <div class="radio-content">
              <span class="radio-title">仅查看</span>
              <span class="radio-desc">可浏览项目内容</span>
            </div>
          </el-radio>
          <el-radio value="comment">
            <div class="radio-content">
              <span class="radio-title">可评论</span>
              <span class="radio-desc">可查看并添加评论</span>
            </div>
          </el-radio>
          <el-radio value="edit">
            <div class="radio-content">
              <span class="radio-title">可编辑</span>
              <span class="radio-desc">可修改项目内容</span>
            </div>
          </el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="密码保护">
        <div class="password-control">
          <el-switch v-model="usePassword" />
          <el-input
            v-if="usePassword"
            v-model="shareForm.password"
            placeholder="设置访问密码"
            show-password
            class="password-input"
          />
        </div>
      </el-form-item>
      
      <el-form-item label="有效期">
        <el-select v-model="shareForm.expires_days" placeholder="永久有效" clearable>
          <el-option label="永久有效" :value="null" />
          <el-option label="1 天" :value="1" />
          <el-option label="7 天" :value="7" />
          <el-option label="30 天" :value="30" />
          <el-option label="90 天" :value="90" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="高级选项">
        <div class="advanced-options">
          <el-checkbox v-model="shareForm.allow_download">允许下载</el-checkbox>
        </div>
      </el-form-item>
    </el-form>
    
    <el-button 
      type="primary" 
      class="create-button"
      :loading="creating"
      @click="handleCreate"
    >
      <el-icon><Link /></el-icon>
      创建分享链接
    </el-button>
    
    <!-- 已创建的分享链接 -->
    <div class="share-list" v-if="shares.length > 0">
      <h4>已创建的分享链接</h4>
      
      <div 
        v-for="share in shares" 
        :key="share.share_code"
        class="share-item"
      >
        <div class="share-info">
          <div class="share-url">
            <el-input 
              :value="share.share_url" 
              readonly 
              size="small"
            >
              <template #append>
                <el-button @click="copyLink(share.share_url)">
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
              </template>
            </el-input>
          </div>
          
          <div class="share-meta">
            <el-tag size="small" :type="getShareTypeTag(share.share_type)">
              {{ getShareTypeText(share.share_type) }}
            </el-tag>
            <el-tag v-if="share.has_password" size="small" type="warning">
              有密码
            </el-tag>
            <el-tag v-if="share.expires_at" size="small" type="info">
              {{ formatExpires(share.expires_at) }}
            </el-tag>
            <span class="view-count">
              <el-icon><View /></el-icon>
              {{ share.view_count }} 次访问
            </span>
          </div>
        </div>
        
        <el-button 
          type="danger" 
          text 
          size="small"
          @click="handleDelete(share.share_code)"
        >
          删除
        </el-button>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Link, CopyDocument, View } from '@element-plus/icons-vue'
import { shareApi, type ShareLink, type ShareType } from '@/api/share'

// Props & Emits
const props = defineProps<{
  projectId: string
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// 可见性
const visible = ref(props.modelValue)
watch(() => props.modelValue, (val) => visible.value = val)
watch(visible, (val) => emit('update:modelValue', val))

// 状态
const creating = ref(false)
const shares = ref<ShareLink[]>([])
const usePassword = ref(false)

// 表单
const shareForm = reactive({
  share_type: 'view' as ShareType,
  password: '',
  expires_days: null as number | null,
  allow_download: false
})

// 加载已有分享
watch(visible, async (val) => {
  if (val) {
    await loadShares()
  }
})

async function loadShares() {
  try {
    const res = await shareApi.list(props.projectId)
    shares.value = res.data.data.shares || []
  } catch (error) {
    console.error('Failed to load shares:', error)
  }
}

// 创建分享
async function handleCreate() {
  creating.value = true
  
  try {
    await shareApi.create({
      project_id: props.projectId,
      share_type: shareForm.share_type,
      password: usePassword.value ? shareForm.password : undefined,
      expires_days: shareForm.expires_days || undefined,
      allow_download: shareForm.allow_download
    })
    
    ElMessage.success('分享链接已创建')
    await loadShares()
    
    // 重置表单
    shareForm.password = ''
    usePassword.value = false
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  } finally {
    creating.value = false
  }
}

// 删除分享
async function handleDelete(shareCode: string) {
  try {
    await shareApi.delete(shareCode)
    ElMessage.success('分享链接已删除')
    shares.value = shares.value.filter(s => s.share_code !== shareCode)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

// 复制链接
async function copyLink(url: string) {
  try {
    await navigator.clipboard.writeText(url)
    ElMessage.success('链接已复制')
  } catch {
    ElMessage.error('复制失败')
  }
}

// 辅助函数
function getShareTypeText(type: ShareType): string {
  const map = { view: '仅查看', comment: '可评论', edit: '可编辑' }
  return map[type] || type
}

function getShareTypeTag(type: ShareType): string {
  const map = { view: 'info', comment: 'warning', edit: 'success' }
  return map[type] || 'info'
}

function formatExpires(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = date.getTime() - now.getTime()
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24))
  
  if (days <= 0) return '已过期'
  if (days === 1) return '1 天后过期'
  return `${days} 天后过期`
}
</script>

<style scoped>
.share-form {
  margin-bottom: 24px;
}

.share-form :deep(.el-radio-group) {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.share-form :deep(.el-radio) {
  height: auto;
  padding: 12px 16px;
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  margin-right: 0;
}

.share-form :deep(.el-radio.is-checked) {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.radio-content {
  display: flex;
  flex-direction: column;
  margin-left: 8px;
}

.radio-title {
  font-weight: 500;
}

.radio-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.password-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.password-input {
  width: 200px;
}

.advanced-options {
  display: flex;
  gap: 16px;
}

.create-button {
  width: 100%;
  margin-bottom: 24px;
}

.share-list h4 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.share-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
  margin-bottom: 12px;
}

.share-info {
  flex: 1;
}

.share-url {
  margin-bottom: 8px;
}

.share-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.view-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-left: auto;
}
</style>

