/**
 * 统一请求封装
 * 
 * 特性:
 * - 统一响应解包
 * - Token 自动刷新
 * - 错误统一处理
 * - 支持 RESTful API
 * - 类型安全
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { storage } from './storage'
import router from '@/router'

// ==================== 类型定义 ====================

/** API 响应格式 */
interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

/** 分页数据格式 */
export interface PaginatedData<T> {
  items: T[]
  pagination: {
    page: number
    page_size: number
    total: number
    total_pages: number
  }
}

/** 分页参数 */
export interface PaginationParams {
  page?: number
  page_size?: number
  [key: string]: any
}

// ==================== 创建实例 ====================

const instance: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ==================== Token 刷新机制 ====================

let isRefreshing = false
let pendingRequests: Array<(token: string) => void> = []

function onTokenRefreshed(token: string) {
  pendingRequests.forEach((callback) => callback(token))
  pendingRequests = []
}

function addPendingRequest(callback: (token: string) => void) {
  pendingRequests.push(callback)
}

// ==================== 请求拦截器 ====================

instance.interceptors.request.use(
  (config) => {
    const token = storage.getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ==================== 响应拦截器 ====================

instance.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const responseData = response.data
    
    // 如果响应不是标准格式，直接返回
    if (typeof responseData !== 'object' || responseData === null) {
      return responseData as any
    }
    
    const { code, message, data } = responseData

    // 业务错误处理
    if (code !== undefined && code !== 0 && code !== 200) {
      ElMessage.error(message || '请求失败')
      return Promise.reject(new Error(message))
    }

    // 返回解包后的数据
    return (data !== undefined ? data : responseData) as any
  },
  async (error) => {
    const { response, config } = error

    // 401 处理 - Token 过期
    if (response?.status === 401 && !config._retry) {
      // 如果已经在刷新中，将请求加入队列
      if (isRefreshing) {
        return new Promise((resolve) => {
          addPendingRequest((token) => {
            config.headers.Authorization = `Bearer ${token}`
            resolve(instance(config))
          })
        })
      }

      config._retry = true
      isRefreshing = true

      try {
        const refreshToken = storage.getRefreshToken()
        if (!refreshToken) {
          throw new Error('No refresh token')
        }

        // 调用刷新接口
        const refreshResponse = await axios.post<ApiResponse<{
          access_token: string
          refresh_token: string
        }>>(`${instance.defaults.baseURL}/auth/refresh`, {
          refresh_token: refreshToken,
        })

        const tokens = refreshResponse.data.data
        const { access_token, refresh_token } = tokens

        // 存储新 Token
        storage.setToken(access_token)
        storage.setRefreshToken(refresh_token)

        // 通知等待中的请求
        onTokenRefreshed(access_token)

        // 重试原请求
        config.headers.Authorization = `Bearer ${access_token}`
        return instance(config)
      } catch (refreshError) {
        // 刷新失败，清除登录状态
        storage.clear()
        router.push('/login')
        return Promise.reject(error)
      } finally {
        isRefreshing = false
      }
    }

    // 其他错误处理
    const message = response?.data?.message || error.message || '网络错误'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// ==================== 统一 API 调用方法 ====================

export const api = {
  /**
   * GET 请求
   */
  get<T = any>(url: string, params?: object, config?: AxiosRequestConfig): Promise<T> {
    return instance.get(url, { params, ...config })
  },

  /**
   * POST 请求
   */
  post<T = any>(url: string, data?: object, config?: AxiosRequestConfig): Promise<T> {
    return instance.post(url, data, config)
  },

  /**
   * PUT 请求
   */
  put<T = any>(url: string, data?: object, config?: AxiosRequestConfig): Promise<T> {
    return instance.put(url, data, config)
  },

  /**
   * PATCH 请求
   */
  patch<T = any>(url: string, data?: object, config?: AxiosRequestConfig): Promise<T> {
    return instance.patch(url, data, config)
  },

  /**
   * DELETE 请求
   */
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return instance.delete(url, config)
  },

  /**
   * 分页查询 (GET)
   */
  paginate<T = any>(url: string, params?: PaginationParams): Promise<PaginatedData<T>> {
    return instance.get(url, { params })
  },

  /**
   * 上传文件
   */
  upload<T = any>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<T> {
    const formData = new FormData()
    formData.append('file', file)

    return instance.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
  },
}

// 导出实例（用于特殊场景）
export const request = instance

export default api
