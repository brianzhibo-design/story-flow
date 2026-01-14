<template>
  <div class="min-h-screen flex">
    <!-- 左侧品牌区 -->
    <div class="hidden lg:flex lg:w-1/2 relative overflow-hidden">
      <!-- 动态渐变背景 -->
      <div class="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-950 to-slate-900"></div>
      
      <!-- Aurora 效果 -->
      <div class="absolute inset-0 overflow-hidden">
        <div class="aurora-blob aurora-blob-1"></div>
        <div class="aurora-blob aurora-blob-2"></div>
        <div class="aurora-blob aurora-blob-3"></div>
      </div>
      
      <!-- 网格背景 -->
      <div class="absolute inset-0 opacity-20" style="background-image: linear-gradient(rgba(255,255,255,.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.03) 1px, transparent 1px); background-size: 60px 60px;"></div>
      
      <!-- 内容 -->
      <div class="relative z-10 flex flex-col justify-between p-12 w-full">
        <!-- Logo -->
        <div class="flex items-center gap-3">
          <div class="w-11 h-11 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/30">
            <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <polygon points="23 7 16 12 23 17 23 7" fill="currentColor" stroke="none" />
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
            </svg>
          </div>
          <span class="text-xl font-bold text-white tracking-tight">StoryFlow</span>
        </div>
        
        <!-- 主标语 -->
        <div class="max-w-lg">
          <h1 class="text-4xl xl:text-5xl font-bold text-white mb-6 leading-tight">
            加入创作者<br />
            <span class="bg-gradient-to-r from-purple-400 via-pink-400 to-orange-400 bg-clip-text text-transparent">社区</span>
          </h1>
          
          <p class="text-lg text-slate-400 mb-10 leading-relaxed">
            注册即可获得免费配额，立即开始使用 AI 创作您的第一个视频作品。
          </p>
          
          <!-- 特性列表 -->
          <div class="space-y-4">
            <div class="feature-item">
              <div class="feature-icon">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
              </div>
              <span class="text-slate-300">免费试用配额</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <span class="text-slate-300">无需绑定信用卡</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <span class="text-slate-300">随时可以升级</span>
            </div>
          </div>
        </div>
        
        <!-- 底部装饰 -->
        <div class="text-xs text-slate-600">
          © 2024 StoryFlow. All rights reserved.
        </div>
      </div>
    </div>
    
    <!-- 右侧注册表单 -->
    <div class="flex-1 flex items-center justify-center bg-slate-50 px-6 sm:px-8 py-10">
      <div class="w-full max-w-[400px]">
        <!-- 移动端 Logo -->
        <div class="flex items-center justify-center gap-2.5 mb-8 lg:hidden">
          <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/20">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <polygon points="23 7 16 12 23 17 23 7" fill="currentColor" stroke="none" />
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
            </svg>
          </div>
          <span class="text-xl font-bold text-slate-900">StoryFlow</span>
        </div>
        
        <!-- 标题 -->
        <div class="text-center mb-8">
          <h2 class="text-2xl font-bold text-slate-900 mb-2">创建账号</h2>
          <p class="text-slate-500">加入 StoryFlow，开始创作</p>
        </div>
        
        <!-- 表单 -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div class="space-y-2">
            <label class="block text-sm font-medium text-slate-700">邮箱</label>
            <div class="relative">
              <input
                v-model="form.email"
                type="email"
                placeholder="your@email.com"
                class="form-input"
                required
                autocomplete="email"
              />
              <div class="input-icon-left">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </div>
          
          <div class="space-y-2">
            <label class="block text-sm font-medium text-slate-700">
              昵称 <span class="text-slate-400 font-normal">(可选)</span>
            </label>
            <div class="relative">
              <input
                v-model="form.nickname"
                type="text"
                placeholder="您的昵称"
                class="form-input"
                autocomplete="nickname"
              />
              <div class="input-icon-left">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
            </div>
          </div>
          
          <div class="space-y-2">
            <label class="block text-sm font-medium text-slate-700">密码</label>
            <div class="relative">
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="至少8位密码"
                class="form-input pr-11"
                required
                minlength="8"
                autocomplete="new-password"
              />
              <div class="input-icon-left">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-600 transition-colors rounded"
                @click="showPassword = !showPassword"
              >
                <svg v-if="!showPassword" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              </button>
            </div>
            <!-- 密码强度指示器 -->
            <div v-if="form.password.length > 0" class="flex gap-1 mt-2">
              <div 
                v-for="i in 4" 
                :key="i" 
                class="h-1 flex-1 rounded-full transition-colors"
                :class="passwordStrengthColors[i - 1]"
              ></div>
            </div>
          </div>
          
          <div class="space-y-2">
            <label class="block text-sm font-medium text-slate-700">确认密码</label>
            <div class="relative">
              <input
                v-model="form.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="再次输入密码"
                class="form-input pr-11"
                :class="{ 'border-red-300 focus:border-red-500 focus:ring-red-500/20': passwordMismatch }"
                required
                autocomplete="new-password"
              />
              <div class="input-icon-left" :class="{ 'text-red-400': passwordMismatch }">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-600 transition-colors rounded"
                @click="showConfirmPassword = !showConfirmPassword"
              >
                <svg v-if="!showConfirmPassword" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              </button>
            </div>
            <p v-if="passwordMismatch" class="text-red-500 text-xs flex items-center gap-1">
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              两次输入的密码不一致
            </p>
          </div>
          
          <button
            type="submit"
            :disabled="loading || passwordMismatch"
            class="submit-btn mt-6"
          >
            <svg v-if="loading" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{{ loading ? '注册中...' : '创建账号' }}</span>
          </button>
        </form>
        
        <!-- 分隔线 -->
        <div class="relative my-8">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-slate-200"></div>
          </div>
          <div class="relative flex justify-center text-xs">
            <span class="px-3 bg-slate-50 text-slate-400">或</span>
          </div>
        </div>
        
        <!-- 登录链接 -->
        <div class="text-center">
          <p class="text-slate-500">
            已有账号？
            <router-link to="/login" class="text-indigo-600 hover:text-indigo-700 font-semibold transition-colors">
              立即登录
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { ElMessage } from 'element-plus'

const { register } = useAuth()

const loading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const form = reactive({
  email: '',
  nickname: '',
  password: '',
  confirmPassword: '',
})

const passwordMismatch = computed(() => {
  return form.confirmPassword.length > 0 && form.password !== form.confirmPassword
})

// 密码强度计算
const passwordStrength = computed(() => {
  const pwd = form.password
  let score = 0
  if (pwd.length >= 8) score++
  if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) score++
  if (/\d/.test(pwd)) score++
  if (/[^a-zA-Z0-9]/.test(pwd)) score++
  return score
})

const passwordStrengthColors = computed(() => {
  const strength = passwordStrength.value
  const colors = ['bg-slate-200', 'bg-slate-200', 'bg-slate-200', 'bg-slate-200']
  
  if (strength >= 1) colors[0] = 'bg-red-400'
  if (strength >= 2) { colors[0] = 'bg-orange-400'; colors[1] = 'bg-orange-400' }
  if (strength >= 3) { colors[0] = 'bg-yellow-400'; colors[1] = 'bg-yellow-400'; colors[2] = 'bg-yellow-400' }
  if (strength >= 4) { colors[0] = 'bg-emerald-500'; colors[1] = 'bg-emerald-500'; colors[2] = 'bg-emerald-500'; colors[3] = 'bg-emerald-500' }
  
  return colors
})

async function handleSubmit() {
  if (!form.email || !form.password) return
  
  if (form.password !== form.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  
  if (form.password.length < 8) {
    ElMessage.error('密码至少需要8位')
    return
  }
  
  loading.value = true
  try {
    await register(form.email, form.password, form.nickname || undefined)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Aurora 效果 */
.aurora-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  animation: aurora 15s ease-in-out infinite;
}

.aurora-blob-1 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #8b5cf6, #a855f7);
  top: -100px;
  right: -100px;
  animation-delay: 0s;
}

.aurora-blob-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #ec4899, #f97316);
  bottom: 20%;
  left: -50px;
  animation-delay: -5s;
}

.aurora-blob-3 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  top: 40%;
  right: 20%;
  animation-delay: -10s;
}

@keyframes aurora {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(30px, -30px) scale(1.1);
  }
  50% {
    transform: translate(-20px, 20px) scale(0.95);
  }
  75% {
    transform: translate(20px, 10px) scale(1.05);
  }
}

/* 特性项 */
.feature-item {
  @apply flex items-center gap-3;
}

.feature-icon {
  @apply w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0;
  @apply bg-gradient-to-br from-purple-500/20 to-pink-500/20 text-purple-400;
}

/* 表单输入 */
.form-input {
  @apply w-full bg-white border border-slate-200 rounded-xl;
  @apply pl-11 pr-4 py-3.5 text-sm text-slate-900;
  @apply placeholder:text-slate-400;
  @apply focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500;
  @apply transition-all duration-200;
}

.input-icon-left {
  @apply absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none transition-colors;
}

/* 提交按钮 */
.submit-btn {
  @apply w-full flex items-center justify-center gap-2;
  @apply bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700;
  @apply text-white font-semibold text-sm;
  @apply px-4 py-3.5 rounded-xl;
  @apply transition-all duration-200;
  @apply shadow-lg shadow-purple-500/25 hover:shadow-xl hover:shadow-purple-500/30;
  @apply active:scale-[0.98];
}

.submit-btn:disabled {
  @apply opacity-70 cursor-not-allowed;
}

/* 响应式动画 */
@media (prefers-reduced-motion: reduce) {
  .aurora-blob {
    animation: none !important;
  }
  
  .submit-btn,
  .form-input {
    transition: none !important;
  }
}
</style>
