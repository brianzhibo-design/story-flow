<script setup lang="ts">
/**
 * 设置页面
 */
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Lock, Bell, Brush, Moon, Sunny } from '@element-plus/icons-vue'

const userStore = useUserStore()

// 当前标签页
const activeTab = ref('profile')

// 用户资料表单
const profileForm = ref({
  nickname: userStore.user?.nickname || '',
  avatar_url: userStore.user?.avatar_url || '',
})

// 密码表单
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

// 通知设置
const notificationSettings = ref({
  emailNotification: true,
  pushNotification: true,
  marketingEmail: false,
})

// 外观设置
const appearanceSettings = ref({
  theme: 'light' as 'light' | 'dark' | 'system',
  language: 'zh-CN',
})

// 保存资料
const savingProfile = ref(false)
async function handleSaveProfile() {
  savingProfile.value = true
  try {
    // TODO: 调用 API 更新用户资料
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('资料已更新')
  } catch (error) {
    ElMessage.error('更新失败，请重试')
  } finally {
    savingProfile.value = false
  }
}

// 修改密码
const changingPassword = ref(false)
async function handleChangePassword() {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  if (passwordForm.value.newPassword.length < 8) {
    ElMessage.error('密码长度至少8位')
    return
  }
  
  changingPassword.value = true
  try {
    // TODO: 调用 API 修改密码
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('密码已修改')
    passwordForm.value = { currentPassword: '', newPassword: '', confirmPassword: '' }
  } catch (error) {
    ElMessage.error('修改失败，请重试')
  } finally {
    changingPassword.value = false
  }
}

// 删除账户
async function handleDeleteAccount() {
  try {
    await ElMessageBox.confirm(
      '此操作将永久删除您的账户和所有数据，是否继续？',
      '删除账户',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger',
      }
    )
    // TODO: 调用 API 删除账户
    ElMessage.success('账户已删除')
    userStore.logout()
  } catch {
    // 用户取消
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <!-- 侧边栏 -->
    <aside class="fixed left-0 top-0 h-screen w-60 bg-white border-r border-slate-200 flex flex-col">
      <!-- Logo -->
      <div class="h-16 flex items-center px-4 border-b border-slate-100">
        <router-link to="/dashboard" class="flex items-center gap-2">
          <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
            <span class="text-white text-sm font-bold">S</span>
          </div>
          <span class="text-lg font-bold text-slate-900">StoryFlow</span>
        </router-link>
      </div>
      
      <!-- 设置菜单 -->
      <nav class="flex-1 p-4 space-y-1">
        <button
          v-for="tab in [
            { id: 'profile', label: '个人资料', icon: User },
            { id: 'password', label: '修改密码', icon: Lock },
            { id: 'notifications', label: '通知设置', icon: Bell },
            { id: 'appearance', label: '外观设置', icon: Brush },
          ]"
          :key="tab.id"
          :class="[
            'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors',
            activeTab === tab.id
              ? 'bg-indigo-50 text-indigo-600 font-medium'
              : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
          ]"
          @click="activeTab = tab.id"
        >
          <el-icon class="w-4 h-4"><component :is="tab.icon" /></el-icon>
          {{ tab.label }}
        </button>
      </nav>
      
      <!-- 返回 -->
      <div class="p-4 border-t border-slate-100">
        <router-link
          to="/dashboard"
          class="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-900 transition-colors"
        >
          <span>← 返回工作台</span>
        </router-link>
      </div>
    </aside>
    
    <!-- 主内容 -->
    <main class="ml-60 p-8">
      <div class="max-w-2xl">
        <!-- 个人资料 -->
        <div v-if="activeTab === 'profile'" class="space-y-6">
          <div>
            <h2 class="text-2xl font-bold text-slate-900">个人资料</h2>
            <p class="text-slate-500 mt-1">管理您的账户信息</p>
          </div>
          
          <div class="bg-white rounded-xl border border-slate-200 p-6 space-y-6">
            <!-- 头像 -->
            <div class="flex items-center gap-4">
              <div class="w-20 h-20 bg-indigo-100 rounded-full flex items-center justify-center">
                <span class="text-2xl font-bold text-indigo-600">
                  {{ userStore.user?.nickname?.charAt(0) || userStore.user?.email?.charAt(0)?.toUpperCase() || 'U' }}
                </span>
              </div>
              <div>
                <button class="text-sm text-indigo-600 hover:text-indigo-700 font-medium">
                  更换头像
                </button>
                <p class="text-xs text-slate-400 mt-1">支持 JPG、PNG，最大 2MB</p>
              </div>
            </div>
            
            <!-- 昵称 -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">昵称</label>
              <input
                v-model="profileForm.nickname"
                type="text"
                class="input"
                placeholder="输入昵称"
              />
            </div>
            
            <!-- 邮箱 (只读) -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">邮箱</label>
              <input
                :value="userStore.user?.email"
                type="email"
                class="input bg-slate-50"
                disabled
              />
              <p class="text-xs text-slate-400 mt-1">邮箱不可修改</p>
            </div>
            
            <button
              class="btn-primary"
              :disabled="savingProfile"
              @click="handleSaveProfile"
            >
              {{ savingProfile ? '保存中...' : '保存更改' }}
            </button>
          </div>
        </div>
        
        <!-- 修改密码 -->
        <div v-if="activeTab === 'password'" class="space-y-6">
          <div>
            <h2 class="text-2xl font-bold text-slate-900">修改密码</h2>
            <p class="text-slate-500 mt-1">定期更换密码可以提高账户安全性</p>
          </div>
          
          <div class="bg-white rounded-xl border border-slate-200 p-6 space-y-6">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">当前密码</label>
              <input
                v-model="passwordForm.currentPassword"
                type="password"
                class="input"
                placeholder="输入当前密码"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">新密码</label>
              <input
                v-model="passwordForm.newPassword"
                type="password"
                class="input"
                placeholder="输入新密码（至少8位）"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">确认新密码</label>
              <input
                v-model="passwordForm.confirmPassword"
                type="password"
                class="input"
                placeholder="再次输入新密码"
              />
            </div>
            
            <button
              class="btn-primary"
              :disabled="changingPassword"
              @click="handleChangePassword"
            >
              {{ changingPassword ? '修改中...' : '修改密码' }}
            </button>
          </div>
        </div>
        
        <!-- 通知设置 -->
        <div v-if="activeTab === 'notifications'" class="space-y-6">
          <div>
            <h2 class="text-2xl font-bold text-slate-900">通知设置</h2>
            <p class="text-slate-500 mt-1">管理您接收通知的方式</p>
          </div>
          
          <div class="bg-white rounded-xl border border-slate-200 p-6 space-y-4">
            <div class="flex items-center justify-between py-3 border-b border-slate-100">
              <div>
                <p class="font-medium text-slate-900">邮件通知</p>
                <p class="text-sm text-slate-500">接收项目状态更新邮件</p>
              </div>
              <el-switch v-model="notificationSettings.emailNotification" />
            </div>
            
            <div class="flex items-center justify-between py-3 border-b border-slate-100">
              <div>
                <p class="font-medium text-slate-900">推送通知</p>
                <p class="text-sm text-slate-500">接收浏览器推送通知</p>
              </div>
              <el-switch v-model="notificationSettings.pushNotification" />
            </div>
            
            <div class="flex items-center justify-between py-3">
              <div>
                <p class="font-medium text-slate-900">营销邮件</p>
                <p class="text-sm text-slate-500">接收产品更新和优惠信息</p>
              </div>
              <el-switch v-model="notificationSettings.marketingEmail" />
            </div>
          </div>
        </div>
        
        <!-- 外观设置 -->
        <div v-if="activeTab === 'appearance'" class="space-y-6">
          <div>
            <h2 class="text-2xl font-bold text-slate-900">外观设置</h2>
            <p class="text-slate-500 mt-1">自定义界面外观</p>
          </div>
          
          <div class="bg-white rounded-xl border border-slate-200 p-6 space-y-6">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-3">主题</label>
              <div class="flex gap-3">
                <button
                  v-for="theme in [
                    { id: 'light', label: '浅色', icon: Sunny },
                    { id: 'dark', label: '深色', icon: Moon },
                  ]"
                  :key="theme.id"
                  :class="[
                    'flex-1 flex items-center justify-center gap-2 py-3 rounded-lg border-2 transition-colors',
                    appearanceSettings.theme === theme.id
                      ? 'border-indigo-600 bg-indigo-50 text-indigo-600'
                      : 'border-slate-200 hover:border-slate-300 text-slate-600'
                  ]"
                  @click="appearanceSettings.theme = theme.id as 'light' | 'dark'"
                >
                  <el-icon><component :is="theme.icon" /></el-icon>
                  {{ theme.label }}
                </button>
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">语言</label>
              <el-select v-model="appearanceSettings.language" class="w-full">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </div>
          </div>
        </div>
        
        <!-- 危险区域 -->
        <div class="mt-12 space-y-6">
          <div>
            <h2 class="text-xl font-bold text-red-600">危险区域</h2>
            <p class="text-slate-500 mt-1">以下操作不可撤销，请谨慎操作</p>
          </div>
          
          <div class="bg-red-50 border border-red-200 rounded-xl p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-red-900">删除账户</p>
                <p class="text-sm text-red-600">永久删除您的账户和所有数据</p>
              </div>
              <button
                class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors"
                @click="handleDeleteAccount"
              >
                删除账户
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.input {
  @apply w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm
         focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500
         transition-colors;
}

.btn-primary {
  @apply px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium
         rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}
</style>

