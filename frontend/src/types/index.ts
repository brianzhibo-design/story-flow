// 用户相关
export interface User {
  id: string
  email: string
  nickname: string | null
  avatar_url: string | null
  role: string
  status: string
  created_at: string
}

// ==================== 配额相关（匹配后端 quota_service.py） ====================

/**
 * 配额状态 - 匹配 GET /quota/status 响应
 */
export interface QuotaStatus {
  plan: string
  credits: {
    used: number
    total: number
    remaining: number
  }
  daily_usage: Record<string, number>
  limits: PlanLimits
  reset_at: string | null
}

/**
 * 套餐限制配置
 */
export interface PlanLimits {
  daily_credits: number
  monthly_credits: number
  max_projects: number
  max_scenes_per_project: number
  image_generation: number
  video_generation: number
  audio_generation: number
}

// ==================== 订阅相关（匹配后端 subscription_service.py） ====================

/**
 * 订阅计划 - 匹配 GET /subscription/plans 响应
 */
export interface SubscriptionPlan {
  type: string
  name: string
  description?: string
  price_monthly: number
  price_yearly: number
  projects_limit: number
  scenes_per_project: number
  storage_gb: number
  llm_tokens: number
  image_count: number
  video_count: number
  video_duration: number
  tts_chars: number
  can_export_hd: boolean
  can_remove_watermark: boolean
  can_use_premium_voices: boolean
  can_collaborate: boolean
  priority_queue: boolean
  api_access: boolean
}

/**
 * 当前订阅状态 - 匹配 GET /subscription/current 响应
 */
export interface SubscriptionCurrent {
  plan: {
    type: string
    name: string
  }
  subscription: {
    status: string
    billing_cycle: string | null
    current_period_start: string | null
    current_period_end: string | null
    auto_renew: boolean
  } | null
  limits: {
    projects: number
    scenes_per_project: number
    storage_gb: number
    llm_tokens: number
    image_count: number
    video_count: number
    video_duration: number
    tts_chars: number
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

/**
 * 使用量项 - 匹配 GET /subscription/usage 响应中的每个字段
 */
export interface UsageItem {
  used: number
  limit: number
  remaining: number
  percentage: number
}

/**
 * 使用量摘要 - 匹配 GET /subscription/usage 响应
 */
export interface UsageSummary {
  llm_tokens: UsageItem
  image_gen: UsageItem
  video_gen: UsageItem
  video_duration: UsageItem
  tts: UsageItem
  storage: UsageItem
}

/**
 * 配额检查结果 - 匹配 GET /subscription/check/{usage_type} 响应
 */
export interface QuotaCheckResult {
  allowed: boolean
  remaining: number
  limit: number
  used: number
}

// 保留向后兼容的旧类型别名
export type Quota = QuotaStatus
export type Subscription = SubscriptionCurrent
export type Usage = UsageSummary

// 项目相关
export interface Project {
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

// 分镜相关
export interface Scene {
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

// 任务相关
export interface Task {
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
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
  meta?: {
    request_id: string
    timestamp: string
  }
}

export interface PaginatedResponse<T> {
  code: number
  message: string
  data: {
    items: T[]
    pagination: {
      page: number
      page_size: number
      total: number
      total_pages: number
    }
  }
}

// WebSocket 消息
export interface TaskProgressMessage {
  task_id: string
  type: string
  status: string
  progress: number
  message: string
  result?: Record<string, unknown>
  error?: string
}

