/**
 * API Mock 模块
 * 
 * 适配新的 API 响应结构（响应已解包，直接返回 data）
 */
import { vi } from 'vitest'
import {
  createMockUser,
  createMockProject,
  createMockScene,
  createMockTask,
} from '../utils'
import type { User, Project, Scene, Task } from '@/api'

// ==================== Auth API Mock ====================

export const mockAuthApi = {
  login: vi.fn().mockResolvedValue({
    user: createMockUser(),
    tokens: {
      access_token: 'mock-access-token',
      refresh_token: 'mock-refresh-token',
      token_type: 'bearer',
      expires_in: 3600,
    },
  }),

  register: vi.fn().mockResolvedValue({
    user: createMockUser(),
    tokens: {
      access_token: 'mock-access-token',
      refresh_token: 'mock-refresh-token',
      token_type: 'bearer',
      expires_in: 3600,
    },
  }),

  refresh: vi.fn().mockResolvedValue({
    access_token: 'mock-new-access-token',
    refresh_token: 'mock-new-refresh-token',
  }),

  me: vi.fn().mockResolvedValue(createMockUser()),

  logout: vi.fn().mockResolvedValue(undefined),

  changePassword: vi.fn().mockResolvedValue(undefined),

  updateProfile: vi.fn().mockResolvedValue(createMockUser()),
}

// ==================== Projects API Mock ====================

const mockProjects: Project[] = [
  createMockProject({ id: 'project-1', title: 'Project 1', status: 'draft' }),
  createMockProject({ id: 'project-2', title: 'Project 2', status: 'completed' }),
  createMockProject({ id: 'project-3', title: 'Project 3', status: 'processing' }),
]

const mockScenes: Scene[] = [
  createMockScene({ id: 'scene-1', scene_index: 1, status: 'completed' }),
  createMockScene({ id: 'scene-2', scene_index: 2, status: 'pending' }),
  createMockScene({ id: 'scene-3', scene_index: 3, status: 'pending' }),
]

export const mockProjectsApi = {
  list: vi.fn().mockResolvedValue({
    items: mockProjects,
    pagination: {
      page: 1,
      page_size: 20,
      total: mockProjects.length,
      total_pages: 1,
    },
  }),

  detail: vi.fn().mockResolvedValue({
    ...createMockProject({ id: 'project-1' }),
    scenes: mockScenes,
  }),

  create: vi.fn().mockImplementation((data: Partial<Project>) =>
    Promise.resolve(createMockProject(data))
  ),

  update: vi.fn().mockImplementation((id: string, data: Partial<Project>) =>
    Promise.resolve(createMockProject({ id, ...data }))
  ),

  delete: vi.fn().mockResolvedValue(undefined),

  generate: vi.fn().mockResolvedValue({ task_id: 'task-123', task_ids: ['task-123'] }),

  getScenes: vi.fn().mockResolvedValue(mockScenes),

  updateScene: vi.fn().mockImplementation((id: string, data: Partial<Scene>) =>
    Promise.resolve(createMockScene({ id, ...data }))
  ),

  reorderScenes: vi.fn().mockResolvedValue(undefined),

  regenerateImage: vi.fn().mockResolvedValue({ task_id: 'task-image-123' }),

  regenerateVideo: vi.fn().mockResolvedValue({ task_id: 'task-video-123' }),
}

// ==================== Tasks API Mock ====================

const mockTasks: Task[] = [
  createMockTask({ id: 'task-1', type: 'storyboard', status: 'completed' }),
  createMockTask({ id: 'task-2', type: 'image', status: 'running', progress: 50 }),
]

export const mockTasksApi = {
  list: vi.fn().mockResolvedValue(mockTasks),

  detail: vi.fn().mockResolvedValue(mockTasks[0]),

  cancel: vi.fn().mockResolvedValue(undefined),

  retry: vi.fn().mockResolvedValue({ task_id: 'task-retry-123' }),
}

// ==================== Quota API Mock ====================

export const mockQuotaApi = {
  status: vi.fn().mockResolvedValue({
    plan: 'free',
    credits: {
      used: 50,
      total: 100,
      remaining: 50,
    },
    daily_usage: {
      image_generation: 5,
      video_generation: 2,
    },
    limits: {
      daily_credits: 10,
      monthly_credits: 100,
      max_projects: 3,
      image_generation: 10,
      video_generation: 3,
    },
    reset_at: new Date(Date.now() + 86400000).toISOString(),
  }),

  getPlans: vi.fn().mockResolvedValue([
    { id: 'free', name: '免费版', limits: {}, price: 0 },
    { id: 'premium', name: '专业版', limits: {}, price: 99 },
  ]),

  upgradePlan: vi.fn().mockResolvedValue(undefined),
}

// ==================== Subscription API Mock ====================

export const mockSubscriptionApi = {
  plans: vi.fn().mockResolvedValue([
    {
      type: 'free',
      name: '免费版',
      price_monthly: 0,
      price_yearly: 0,
      projects_limit: 3,
      scenes_per_project: 10,
      storage_gb: 1,
      llm_tokens: 10000,
      image_count: 50,
      video_count: 10,
      video_duration: 60,
      tts_chars: 5000,
      can_export_hd: false,
      can_remove_watermark: false,
      can_use_premium_voices: false,
      can_collaborate: false,
      priority_queue: false,
      api_access: false,
    },
  ]),

  getCurrent: vi.fn().mockResolvedValue({
    plan: { type: 'free', name: '免费版' },
    subscription: null,
    limits: {
      projects: 3,
      scenes_per_project: 10,
      storage_gb: 1,
      llm_tokens: 10000,
      image_count: 50,
      video_count: 10,
      video_duration: 60,
      tts_chars: 5000,
    },
    features: {
      can_export_hd: false,
      can_remove_watermark: false,
      can_use_premium_voices: false,
      can_collaborate: false,
      priority_queue: false,
      api_access: false,
    },
  }),

  subscribe: vi.fn().mockResolvedValue({
    subscription_id: 'sub-123',
    plan_type: 'pro',
    period_end: new Date(Date.now() + 30 * 86400000).toISOString(),
  }),

  cancel: vi.fn().mockResolvedValue({
    cancelled_at: new Date().toISOString(),
    valid_until: new Date(Date.now() + 30 * 86400000).toISOString(),
  }),

  getUsage: vi.fn().mockResolvedValue({
    llm_tokens: { used: 1000, limit: 10000, remaining: 9000, percentage: 10 },
    image_gen: { used: 10, limit: 50, remaining: 40, percentage: 20 },
    video_gen: { used: 2, limit: 10, remaining: 8, percentage: 20 },
    video_duration: { used: 30, limit: 60, remaining: 30, percentage: 50 },
    tts: { used: 500, limit: 5000, remaining: 4500, percentage: 10 },
    storage: { used: 0.1, limit: 1, remaining: 0.9, percentage: 10 },
  }),

  checkQuota: vi.fn().mockResolvedValue({
    allowed: true,
    remaining: 40,
    limit: 50,
    used: 10,
  }),

  getUsageHistory: vi.fn().mockResolvedValue({
    records: [],
  }),
}

// ==================== Payment API Mock ====================

export const mockPaymentApi = {
  methods: vi.fn().mockResolvedValue([
    { id: 'alipay', name: '支付宝', icon: 'alipay', description: '支持花呗', enabled: true },
    { id: 'wechat', name: '微信支付', icon: 'wechat', description: '扫码支付', enabled: true },
  ]),

  getPrice: vi.fn().mockResolvedValue({
    original_price: 99,
    final_price: 99,
    discount: 0,
    saved: 0,
  }),

  createOrder: vi.fn().mockResolvedValue({
    order_no: 'ORDER-123',
    amount: 99,
    pay_url: 'https://example.com/pay',
  }),

  queryOrder: vi.fn().mockResolvedValue({
    order_no: 'ORDER-123',
    amount: 99,
    status: 'pending',
  }),
}

// ==================== Share API Mock ====================

export const mockShareApi = {
  create: vi.fn().mockResolvedValue({
    share_code: 'abc123',
    share_url: 'https://storyflow.com/s/abc123',
    share_type: 'view',
    expires_at: null,
    has_password: false,
  }),

  list: vi.fn().mockResolvedValue([]),

  delete: vi.fn().mockResolvedValue(undefined),

  access: vi.fn().mockResolvedValue({
    project: { id: 'project-1', title: 'Test Project', style: 'default' },
    permissions: {
      type: 'view',
      can_view: true,
      can_comment: false,
      can_edit: false,
      can_download: false,
    },
  }),
}

// ==================== 工具函数 ====================

/**
 * 重置所有 Mock
 */
export function resetAllMocks(): void {
  Object.values(mockAuthApi).forEach((mock) => mock.mockClear())
  Object.values(mockProjectsApi).forEach((mock) => mock.mockClear())
  Object.values(mockTasksApi).forEach((mock) => mock.mockClear())
  Object.values(mockQuotaApi).forEach((mock) => mock.mockClear())
  Object.values(mockSubscriptionApi).forEach((mock) => mock.mockClear())
  Object.values(mockPaymentApi).forEach((mock) => mock.mockClear())
  Object.values(mockShareApi).forEach((mock) => mock.mockClear())
}

/**
 * 设置 API 错误响应
 */
export function mockApiError(
  mockFn: ReturnType<typeof vi.fn>,
  message = 'API Error',
  code = 500
): void {
  mockFn.mockRejectedValueOnce({
    response: {
      status: code,
      data: { message, code },
    },
  })
}

/**
 * 设置用户登录状态
 */
export function mockLoggedInUser(user: Partial<User> = {}): User {
  const mockUser = createMockUser(user)
  mockAuthApi.me.mockResolvedValue(mockUser)
  return mockUser
}

/**
 * 设置未登录状态
 */
export function mockLoggedOutUser(): void {
  mockAuthApi.me.mockRejectedValue({
    response: { status: 401 },
  })
}

// ==================== 导出完整的 Mock 对象 ====================

export const apiMocks = {
  auth: mockAuthApi,
  projects: mockProjectsApi,
  tasks: mockTasksApi,
  quota: mockQuotaApi,
  subscription: mockSubscriptionApi,
  payment: mockPaymentApi,
  share: mockShareApi,
}
