/**
 * 请求缓存组合式函数
 * 
 * 提供简单的请求缓存功能，避免重复请求
 */
import { ref, shallowRef } from 'vue'

// ==================== 缓存存储 ====================

interface CacheEntry<T> {
  data: T
  timestamp: number
  promise?: Promise<T>
}

const cache = new Map<string, CacheEntry<unknown>>()

// ==================== 配置 ====================

const DEFAULT_TTL = 5 * 60 * 1000  // 5分钟
const DEFAULT_STALE_TTL = 30 * 1000  // 30秒内返回缓存数据，同时后台刷新

// ==================== 工具函数 ====================

/**
 * 生成缓存键
 */
export function createCacheKey(prefix: string, params?: Record<string, unknown>): string {
  if (!params) return prefix
  return `${prefix}:${JSON.stringify(params)}`
}

/**
 * 清除指定前缀的缓存
 */
export function invalidateCache(prefix: string) {
  for (const key of cache.keys()) {
    if (key.startsWith(prefix)) {
      cache.delete(key)
    }
  }
}

/**
 * 清除所有缓存
 */
export function clearAllCache() {
  cache.clear()
}

// ==================== 主函数 ====================

interface UseCachedQueryOptions<T> {
  /** 缓存时间 (毫秒) */
  ttl?: number
  /** 初始数据 */
  initialData?: T
  /** 是否在挂载时自动获取 */
  immediate?: boolean
  /** 数据变换函数 */
  transform?: (data: unknown) => T
  /** 成功回调 */
  onSuccess?: (data: T) => void
  /** 错误回调 */
  onError?: (error: Error) => void
}

export function useCachedQuery<T>(
  key: string,
  fetcher: () => Promise<T>,
  options: UseCachedQueryOptions<T> = {}
) {
  const {
    ttl = DEFAULT_TTL,
    initialData,
    immediate = true,
    transform,
    onSuccess,
    onError,
  } = options
  
  // ==================== 状态 ====================
  
  const data = shallowRef<T | null>(initialData ?? null)
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const lastUpdated = ref<Date | null>(null)
  
  // ==================== 方法 ====================
  
  /**
   * 检查缓存是否有效
   */
  function isCacheValid(): boolean {
    const entry = cache.get(key)
    if (!entry) return false
    return Date.now() - entry.timestamp < ttl
  }
  
  /**
   * 检查缓存是否过期但仍可用 (stale-while-revalidate)
   */
  function isCacheStale(): boolean {
    const entry = cache.get(key)
    if (!entry) return false
    const age = Date.now() - entry.timestamp
    return age >= ttl && age < ttl + DEFAULT_STALE_TTL
  }
  
  /**
   * 获取数据
   */
  async function fetch(force = false): Promise<T | null> {
    // 检查有效缓存
    if (!force && isCacheValid()) {
      const entry = cache.get(key) as CacheEntry<T>
      data.value = transform ? transform(entry.data) : entry.data
      return data.value
    }
    
    // stale-while-revalidate: 返回过期数据，同时后台刷新
    if (!force && isCacheStale()) {
      const entry = cache.get(key) as CacheEntry<T>
      data.value = transform ? transform(entry.data) : entry.data
      
      // 后台刷新，不阻塞
      fetchFromNetwork().catch(console.error)
      
      return data.value
    }
    
    return fetchFromNetwork()
  }
  
  /**
   * 从网络获取数据
   */
  async function fetchFromNetwork(): Promise<T | null> {
    // 检查是否有进行中的请求
    const existing = cache.get(key)
    if (existing?.promise) {
      return existing.promise as Promise<T>
    }
    
    loading.value = true
    error.value = null
    
    const promise = fetcher()
    
    // 缓存 Promise，避免重复请求
    cache.set(key, {
      data: existing?.data ?? null,
      timestamp: existing?.timestamp ?? 0,
      promise,
    })
    
    try {
      const result = await promise
      const transformedData = transform ? transform(result) : result
      
      // 更新缓存
      cache.set(key, {
        data: transformedData,
        timestamp: Date.now(),
      })
      
      data.value = transformedData
      lastUpdated.value = new Date()
      
      onSuccess?.(transformedData)
      
      return transformedData
    } catch (err) {
      const e = err as Error
      error.value = e
      onError?.(e)
      
      // 移除失败的缓存
      cache.delete(key)
      
      return null
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 刷新数据 (强制获取)
   */
  async function refresh(): Promise<T | null> {
    return fetch(true)
  }
  
  /**
   * 使缓存失效
   */
  function invalidate() {
    cache.delete(key)
  }
  
  /**
   * 手动设置数据 (乐观更新)
   */
  function setData(newData: T) {
    data.value = newData
    cache.set(key, {
      data: newData,
      timestamp: Date.now(),
    })
  }
  
  // 自动获取
  if (immediate) {
    fetch()
  }
  
  return {
    // 状态
    data,
    loading,
    error,
    lastUpdated,
    
    // 方法
    fetch,
    refresh,
    invalidate,
    setData,
    isCacheValid,
  }
}

