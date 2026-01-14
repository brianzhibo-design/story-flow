/**
 * API 模块统一导出
 */

// 基础请求方法
export { api, request } from '@/utils/request'
export type { PaginatedData, PaginationParams } from '@/utils/request'

// 认证模块
export { authApi } from './auth'
export type { 
  LoginParams, 
  RegisterParams, 
  AuthResponse, 
  User,
  ChangePasswordParams,
  UpdateProfileParams,
} from './auth'

// 项目模块
export { projectsApi } from './projects'
export type { 
  Project, 
  Scene, 
  CreateProjectParams, 
  UpdateProjectParams,
  ListProjectsParams,
  UpdateSceneParams,
} from './projects'

// 任务模块
export { tasksApi } from './tasks'
export type { Task } from './tasks'

// 订阅模块
export { subscriptionApi } from './subscription'
export type { 
  SubscriptionPlan, 
  UserSubscription, 
  UsageSummary,
  SubscribeParams,
  CheckQuotaResult,
} from './subscription'

// 配额模块
export { quotaApi } from './quota'
export type { 
  Quota,
  Plan,
} from './quota'

// 支付模块
export { paymentApi } from './payment'
export type { 
  PaymentMethod, 
  PriceInfo,
  CreateOrderParams, 
  Order,
} from './payment'

// 分享模块
export { shareApi } from './share'
export type { 
  Share, 
  CreateShareParams,
  SharedProject,
  Collaborator,
  AddCollaboratorParams,
  Comment,
  CreateCommentParams,
} from './share'
