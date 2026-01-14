# StoryFlow 前端代码总结

> 本文档总结了 StoryFlow AI 视频创作平台前端代码的完整架构、技术栈和实现细节。

## 📋 目录

- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [核心模块](#核心模块)
  - [入口配置](#入口配置)
  - [路由系统](#路由系统)
  - [状态管理](#状态管理)
  - [API 层](#api-层)
  - [组合式函数](#组合式函数)
  - [视图页面](#视图页面)
  - [组件](#组件)
  - [类型定义](#类型定义)
  - [样式系统](#样式系统)
- [已知问题](#已知问题)
- [优化建议](#优化建议)

---

## 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | Vue 3 | ^3.4.0 |
| 构建工具 | Vite | ^5.0.10 |
| 语言 | TypeScript | ^5.3.3 |
| 路由 | Vue Router | ^4.2.5 |
| 状态管理 | Pinia | ^2.1.7 |
| HTTP 客户端 | Axios | ^1.6.2 |
| UI 组件库 | Element Plus | ^2.4.4 |
| CSS 框架 | Tailwind CSS | ^3.4.0 |
| 日期处理 | Day.js | ^1.11.10 |
| 工具库 | Lodash-es | ^4.17.21 |

---

## 项目结构

```
frontend/
├── index.html                 # HTML 入口
├── package.json               # 依赖配置
├── vite.config.ts             # Vite 配置
├── tailwind.config.js         # Tailwind 配置
├── postcss.config.js          # PostCSS 配置
├── tsconfig.json              # TypeScript 配置
└── src/
    ├── main.ts                # 应用入口
    ├── App.vue                # 根组件
    ├── api/                   # API 封装层
    │   ├── index.ts           # API 入口导出
    │   ├── auth.ts            # 认证 API
    │   ├── projects.ts        # 项目 API
    │   ├── tasks.ts           # 任务 API
    │   ├── quota.ts           # 配额 API
    │   ├── subscription.ts    # 订阅 API
    │   ├── payment.ts         # 支付 API
    │   └── share.ts           # 分享协作 API
    ├── components/            # 可复用组件
    │   ├── common/            # 通用组件
    │   │   └── QuotaIndicator.vue
    │   ├── editor/            # 编辑器组件
    │   │   └── SceneCard.vue
    │   ├── subscription/      # 订阅相关组件
    │   │   ├── PlanCard.vue
    │   │   └── UsageBar.vue
    │   ├── share/             # 分享协作组件
    │   │   └── ShareDialog.vue
    │   └── project/           # 项目相关组件 (空)
    ├── composables/           # 组合式函数
    │   ├── useAuth.ts         # 认证逻辑
    │   └── useWebSocket.ts    # WebSocket 连接
    ├── router/                # 路由配置
    │   └── index.ts
    ├── stores/                # Pinia 状态管理
    │   ├── index.ts           # Store 导出
    │   ├── user.ts            # 用户状态
    │   ├── project.ts         # 项目状态
    │   └── subscription.ts    # 订阅状态
    ├── styles/                # 样式文件
    │   └── main.css           # 主样式 (Tailwind)
    ├── types/                 # TypeScript 类型
    │   └── index.ts
    ├── utils/                 # 工具函数
    │   ├── request.ts         # Axios 封装
    │   └── storage.ts         # 本地存储封装
    └── views/                 # 页面视图
        ├── Home.vue           # 首页
        ├── Login.vue          # 登录页
        ├── Register.vue       # 注册页
        ├── Dashboard.vue      # 工作台
        ├── ProjectCreate.vue  # 创建项目
        ├── ProjectEditor.vue  # 项目编辑器
        ├── QuotaPage.vue      # 配额管理
        ├── Pricing.vue        # 定价页面
        ├── Payment.vue        # 支付页面
        ├── PaymentResult.vue  # 支付结果
        ├── Subscription.vue   # 订阅管理
        ├── SharedProject.vue  # 分享项目查看
        └── NotFound.vue       # 404 页面
```

---

## 核心模块

### 入口配置

#### `main.ts` - 应用入口

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import './styles/main.css'

const app = createApp(App)

// 全局注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
```

#### `App.vue` - 根组件

```vue
<template>
  <el-config-provider :locale="zhCn">
    <router-view />
  </el-config-provider>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { useUserStore } from '@/stores'

const userStore = useUserStore()

onMounted(() => {
  userStore.init()  // 从 localStorage 恢复用户状态
})
</script>
```

#### `vite.config.ts` - Vite 配置

```typescript
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  optimizeDeps: {
    include: ['dayjs', 'dayjs/plugin/...'],  // 预构建 dayjs 插件
  },
  server: {
    port: 3000,
    proxy: {
      '/api': { target: 'http://localhost:8001', changeOrigin: true },
      '/ws': { target: 'ws://localhost:8001', ws: true },
    },
  },
})
```

---

### 路由系统

#### 路由配置 (`router/index.ts`)

**路由列表**：

| 路径 | 名称 | 组件 | 需认证 | 说明 |
|------|------|------|--------|------|
| `/` | Home | Home.vue | ❌ | 首页 |
| `/login` | Login | Login.vue | ❌ (guest) | 登录 |
| `/register` | Register | Register.vue | ❌ (guest) | 注册 |
| `/dashboard` | Dashboard | Dashboard.vue | ✅ | 工作台 |
| `/projects/create` | ProjectCreate | ProjectCreate.vue | ✅ | 创建项目 |
| `/projects/:id` | ProjectEditor | ProjectEditor.vue | ✅ | 编辑项目 |
| `/quota` | Quota | QuotaPage.vue | ✅ | 配额管理 |
| `/pricing` | Pricing | Pricing.vue | ❌ | 定价方案 |
| `/payment` | Payment | Payment.vue | ✅ | 支付 |
| `/payment/success` | PaymentSuccess | PaymentResult.vue | ✅ | 支付成功 |
| `/payment/expired` | PaymentExpired | PaymentResult.vue | ✅ | 订单过期 |
| `/subscription` | Subscription | Subscription.vue | ✅ | 订阅管理 |
| `/s/:shareCode` | SharedProject | SharedProject.vue | ❌ | 分享项目 |
| `/:pathMatch(.*)*` | NotFound | NotFound.vue | ❌ | 404 |

**路由守卫逻辑**：

```typescript
router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  document.title = `${to.meta.title} - AI视频创作平台`
  
  // 需要登录的页面 → 未登录则跳转登录
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  // 已登录用户访问登录/注册页 → 跳转工作台
  if (to.meta.guest && userStore.isLoggedIn) {
    next({ name: 'Dashboard' })
    return
  }
  
  next()
})
```

---

### 状态管理

#### 1. `user.ts` - 用户状态

```typescript
export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const quota = ref<UserQuota | null>(null)
  const token = ref<string | null>(storage.getToken())
  
  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  
  // 方法
  async function doLogin(params: LoginParams) { ... }
  async function doRegister(params: RegisterParams) { ... }
  async function fetchUser() { ... }
  function logout() { ... }
  function init() { ... }  // 从 localStorage 恢复
  
  return { user, quota, token, isLoggedIn, isAdmin, doLogin, doRegister, fetchUser, logout, init }
})
```

**注意事项**：
- 后端响应格式: `{ data: { user, tokens } }`
- Axios 响应: `{ data: { data: { ... } } }`
- 需要使用 `res.data?.data || res.data` 兼容处理

#### 2. `project.ts` - 项目状态

```typescript
export const useProjectStore = defineStore('project', () => {
  // 状态
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const scenes = ref<Scene[]>([])
  const tasks = ref<Task[]>([])
  const loading = ref(false)
  const pagination = ref({ page: 1, page_size: 20, total: 0, total_pages: 0 })
  
  // 计算属性
  const isProcessing = computed(() => currentProject.value?.status === 'processing')
  const completedScenes = computed(() => scenes.value.filter(s => s.status === 'completed'))
  const progress = computed(() => ...)
  
  // 方法
  async function fetchProjects(page = 1) { ... }
  async function fetchProject(id: string) { ... }
  async function create(params: CreateProjectParams) { ... }
  async function update(id: string, params: Partial<Project>) { ... }
  async function remove(id: string) { ... }
  async function generate(id: string, steps?: string[]) { ... }
  function updateScene(sceneId: string, updates: Partial<Scene>) { ... }  // WebSocket 推送更新
  function updateTask(taskId: string, updates: Partial<Task>) { ... }
  function clearCurrent() { ... }
  
  return { ... }
})
```

#### 3. `subscription.ts` - 订阅状态

```typescript
export const useSubscriptionStore = defineStore('subscription', {
  state: (): SubscriptionState => ({
    plans: [],
    currentSubscription: null,
    usage: null,
    loading: false,
    initialized: false
  }),
  
  getters: {
    planType(): string { ... },           // 当前计划类型
    currentPlan(): SubscriptionPlan | null { ... },
    isPaid(): boolean { ... },             // 是否付费用户
    isPro(): boolean { ... },              // 是否专业版
    isEnterprise(): boolean { ... },
    isActive(): boolean { ... },           // 订阅是否有效
    daysRemaining(): number { ... },       // 剩余天数
    hasFeature(): (feature: string) => boolean { ... },  // 功能检查
    quotaRemaining(): (type: string) => number { ... },  // 配额剩余
    quotaPercentage(): (type: string) => number { ... }  // 使用百分比
  },
  
  actions: {
    async fetchPlans() { ... },
    async fetchCurrent() { ... },
    async fetchUsage() { ... },
    async checkQuota(type: string, amount: number = 1) { ... },
    async init() { ... },
    async refresh() { ... },
    reset() { ... }
  }
})
```

---

### API 层

#### 请求封装 (`utils/request.ts`)

```typescript
const request: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截器 - 自动添加 Token
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 错误处理
request.interceptors.response.use(
  (response) => response,  // 直接返回完整响应
  (error) => {
    // 401: Token 过期 → 跳转登录
    // 403: 无权限
    // 404: 资源不存在
    // 429: 请求频繁
    // 500: 服务器错误
    // 其他: 网络错误
  }
)
```

#### API 模块

| 模块 | 文件 | 主要功能 |
|------|------|----------|
| 认证 | `auth.ts` | login, register, refreshToken, getCurrentUser, changePassword |
| 项目 | `projects.ts` | getProjects, getProject, createProject, updateProject, deleteProject, generateProject |
| 任务 | `tasks.ts` | getProjectTasks, getTask, cancelTask, retryTask |
| 配额 | `quota.ts` | getStatus, getPlans, upgradePlan |
| 订阅 | `subscription.ts` | getPlans, getCurrent, subscribe, cancel, getUsage, checkQuota |
| 支付 | `payment.ts` | createOrder, queryOrder, getPrice, getMethods |
| 分享 | `share.ts` | create, list, delete, access, addCollaborator, getCollaborators, createComment, ... |

**API 类型定义示例**：

```typescript
// 订阅计划
interface SubscriptionPlan {
  id: string
  name: string
  type: 'free' | 'basic' | 'pro' | 'enterprise'
  price_monthly: number
  price_yearly: number
  limits: {
    projects: number
    scenes_per_project: number
    storage_gb: number
    llm_tokens: number
    image_count: number
    video_count: number
    // ...
  }
  features: {
    can_export_hd: boolean
    can_remove_watermark: boolean
    can_use_premium_voices: boolean
    can_collaborate: boolean
    priority_queue: boolean
    api_access: boolean
  }
}
```

---

### 组合式函数

#### `useAuth.ts` - 认证逻辑

```typescript
export function useAuth() {
  const router = useRouter()
  const userStore = useUserStore()
  
  const isLoggedIn = computed(() => userStore.isLoggedIn)
  const user = computed(() => userStore.user)
  
  async function login(email: string, password: string) {
    await userStore.doLogin({ email, password })
    ElMessage.success('登录成功')
    const redirect = router.currentRoute.value.query.redirect as string
    router.push(redirect || '/dashboard')
  }
  
  async function register(email: string, password: string, nickname?: string) {
    await userStore.doRegister({ email, password, nickname })
    ElMessage.success('注册成功')
    router.push('/dashboard')
  }
  
  function logout() {
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
  
  return { isLoggedIn, user, login, register, logout }
}
```

#### `useWebSocket.ts` - WebSocket 连接

```typescript
export function useWebSocket(projectId: string) {
  const socket = ref<WebSocket | null>(null)
  const connected = ref(false)
  const lastMessage = ref<TaskProgressMessage | null>(null)
  const projectStore = useProjectStore()
  
  function connect() {
    const token = storage.getToken()
    const wsUrl = `${protocol}//${host}/api/v1/ws/tasks/${projectId}?token=${token}`
    
    const ws = new WebSocket(wsUrl)
    
    ws.onmessage = (event) => {
      const message: TaskProgressMessage = JSON.parse(event.data)
      handleMessage(message)
    }
    
    ws.onclose = () => {
      // 3秒后自动重连
      setTimeout(() => connect(), 3000)
    }
    
    // 30秒心跳
    setInterval(() => ws.send(JSON.stringify({ type: 'ping' })), 30000)
  }
  
  function handleMessage(message: TaskProgressMessage) {
    // 更新任务状态
    projectStore.updateTask(message.task_id, { ... })
    
    // 任务完成时更新分镜
    if (message.status === 'completed' && message.result) {
      if (message.type === 'image') {
        projectStore.updateScene(result.scene_id, { image_url: result.image_url })
      }
      if (message.type === 'video') {
        projectStore.updateScene(result.scene_id, { video_url: result.video_url })
      }
    }
  }
  
  onMounted(() => connect())
  onUnmounted(() => disconnect())
  
  return { connected, lastMessage, connect, disconnect }
}
```

---

### 视图页面

#### 1. Home.vue - 首页

- 全屏渐变背景
- Hero 区域展示产品介绍
- 根据登录状态显示不同按钮

#### 2. Login.vue / Register.vue - 认证页面

- 居中卡片式表单
- 使用 Element Plus Form 组件
- 表单验证 (邮箱格式、密码长度)
- 调用 `useAuth()` 处理认证

#### 3. Dashboard.vue - 工作台

- 顶部导航栏 (Logo, 配额指示器, 用户菜单)
- 欢迎区域
- 快捷操作卡片 (创建项目, 项目统计)
- 项目列表 (支持搜索、状态筛选)
- 分页

**特点**：
- 深色渐变背景 (`from-slate-900 via-slate-800 to-slate-900`)
- 毛玻璃效果 (`backdrop-blur-xl`)
- 响应式网格布局

#### 4. ProjectEditor.vue - 项目编辑器

- 顶部导航 (返回按钮, 项目标题, 状态标签, 生成/导出按钮)
- 主内容区:
  - 左侧: 分镜列表 (`SceneCard` 组件)
  - 右侧: 信息面板 (项目统计, 故事文本, 任务队列)
- 进度条 (生成进度)
- WebSocket 实时更新

#### 5. Pricing.vue - 定价页面

- 月付/年付切换
- 4 个套餐卡片 (`PlanCard` 组件)
- 功能对比表格
- FAQ 折叠面板

#### 6. Payment.vue - 支付页面

- 订单确认信息
- 支付方式选择 (支付宝/微信)
- 微信支付二维码展示
- 支付状态轮询

---

### 组件

#### 1. `QuotaIndicator.vue` - 配额指示器

```vue
<!-- 显示在顶部导航栏的圆形进度条 -->
<el-progress type="circle" :percentage="percentage" :width="32" />
<div>{{ remaining }} 积分</div>
```

#### 2. `SceneCard.vue` - 分镜卡片

```vue
<!-- 单个分镜的展示卡片 -->
<div class="card">
  <div class="flex gap-6">
    <!-- 左侧: 图片/视频预览 -->
    <div v-if="scene.video_url">视频播放器</div>
    <div v-else-if="scene.image_url">图片 + 悬浮重新生成按钮</div>
    <div v-else>占位符 + 状态文字</div>
    
    <!-- 右侧: 分镜信息 -->
    <div>
      <span>分镜序号</span>
      <el-tag>镜头类型</el-tag>
      <el-tag>情绪</el-tag>
      <p>旁白文本</p>
      <p>场景描述</p>
      <el-tag v-for="角色">{{ 角色 }}</el-tag>
      <el-tag v-for="道具">{{ 道具 }}</el-tag>
    </div>
  </div>
</div>
```

#### 3. `PlanCard.vue` - 订阅计划卡片

- 热门标签
- 计划名称和描述
- 价格显示 (支持月付/年付切换, 折扣展示)
- 配额列表
- 功能列表 (勾选/禁用)
- 操作按钮 (当前计划/升级/联系销售)

#### 4. `UsageBar.vue` - 使用量进度条

```vue
<el-progress :percentage="percentage" :status="status" />
<span>{{ used }} / {{ limit }} {{ unit }}</span>
```

#### 5. `ShareDialog.vue` - 分享对话框

- 权限类型选择 (仅查看/可评论/可编辑)
- 密码保护开关
- 有效期选择
- 高级选项 (允许下载)
- 已创建分享链接列表

---

### 类型定义

```typescript
// 用户
interface User {
  id: string
  email: string
  nickname: string | null
  avatar_url: string | null
  role: string
  status: string
  created_at: string
}

// 用户配额
interface UserQuota {
  plan_type: string
  total_credits: number
  used_credits: number
  remaining_credits: number
  storyboard_quota: number
  storyboard_used: number
  image_quota: number
  image_used: number
  video_quota: number
  video_used: number
}

// 项目
interface Project {
  id: string
  title: string
  description: string | null
  story_text: string
  status: 'draft' | 'processing' | 'completed' | 'failed'
  scene_count: number
  total_duration: number
  thumbnail_url: string | null
  final_video_url: string | null
  created_at: string
  updated_at: string
}

// 分镜
interface Scene {
  id: string
  project_id: string
  scene_index: number
  text: string
  scene_description: string | null
  characters: string[]
  props: string[]
  camera_type: string | null
  mood: string | null
  image_prompt: string | null
  negative_prompt: string | null
  image_url: string | null
  video_url: string | null
  duration: number | null
  status: 'pending' | 'generating' | 'completed' | 'failed'
}

// 任务
interface Task {
  id: string
  project_id: string
  scene_id: string | null
  type: 'storyboard' | 'image' | 'video' | 'compose'
  status: 'pending' | 'queued' | 'running' | 'completed' | 'failed'
  progress: number
  progress_message: string | null
  error_message: string | null
  created_at: string
}

// API 响应
interface ApiResponse<T> {
  code: number
  message: string
  data: T
  meta?: { request_id: string; timestamp: string }
}

interface PaginatedResponse<T> {
  code: number
  message: string
  data: {
    items: T[]
    pagination: { page: number; page_size: number; total: number; total_pages: number }
  }
}

// WebSocket 消息
interface TaskProgressMessage {
  task_id: string
  type: string
  status: string
  progress: number
  message: string
  result?: Record<string, unknown>
  error?: string
}
```

---

### 样式系统

#### Tailwind CSS 配置

```css
/* main.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 自定义类 */
.btn-primary { @apply bg-primary-600 text-white px-4 py-2 rounded-lg ... }
.btn-secondary { @apply bg-gray-200 text-gray-800 ... }
.card { @apply bg-white rounded-xl shadow-sm border border-gray-100 p-6 }

/* Element Plus 主题覆盖 */
.el-button--primary {
  --el-button-bg-color: #0284c7;
  --el-button-border-color: #0284c7;
  --el-button-hover-bg-color: #0369a1;
}
```

#### 设计规范

- **颜色**：使用 Tailwind 默认色板 + primary 自定义色
- **圆角**：`rounded-lg` (8px), `rounded-xl` (12px), `rounded-2xl` (16px)
- **阴影**：`shadow-sm`, `shadow-xl`
- **渐变**：`bg-gradient-to-br from-primary-500 to-primary-700`
- **毛玻璃**：`backdrop-blur-xl bg-black/20`
- **过渡**：`transition-colors`, `transition-all`

---

## 已知问题

### 1. 页面跳转 Bug
- 问题描述：部分页面跳转存在问题
- 可能原因：
  - 路由守卫逻辑
  - 异步状态初始化
  - Token 验证失败

### 2. API 响应处理
- 问题描述：后端响应格式嵌套 (`res.data.data`)
- 现有处理：`const data = res.data?.data || res.data`
- 建议：统一在 Axios 拦截器中解包

### 3. dayjs 导入问题
- 问题描述：ESM 模块兼容性问题
- 已修复：在 `vite.config.ts` 中添加 `optimizeDeps.include`

### 4. 空组件目录
- `components/project/` 目录为空
- 建议：添加项目相关组件或删除空目录

---

## 优化建议

### 1. 代码质量

- [ ] 添加 ESLint + Prettier 配置
- [ ] 添加 TypeScript 严格模式
- [ ] 添加单元测试 (Vitest)
- [ ] 添加 E2E 测试 (Playwright)

### 2. 性能优化

- [ ] 路由懒加载 (已实现 ✅)
- [ ] 组件懒加载
- [ ] 图片懒加载
- [ ] 虚拟滚动 (大量分镜时)
- [ ] API 请求缓存

### 3. 用户体验

- [ ] 添加骨架屏
- [ ] 添加全局加载状态
- [ ] 改进错误提示
- [ ] 添加离线支持 (PWA)

### 4. 架构改进

- [ ] 统一 API 响应解包
- [ ] 添加请求重试机制
- [ ] Token 自动刷新
- [ ] 统一状态持久化
- [ ] 添加日志系统

### 5. 功能完善

- [ ] 完善项目创建流程
- [ ] 添加分镜拖拽排序
- [ ] 添加分镜编辑功能
- [ ] 完善支付流程
- [ ] 添加用户设置页面

---

## 附录

### 本地开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

### 环境变量

通过 `vite.config.ts` 配置代理，无需额外环境变量。生产环境需配置实际 API 地址。

### 后端 API 地址

- 开发环境：`http://localhost:8001/api/v1`
- WebSocket：`ws://localhost:8001/api/v1/ws/tasks/:projectId`

---

*文档生成时间: 2025-01-01*
*前端框架版本: Vue 3.4.0*

