/**
 * Pinia 状态持久化插件
 * 
 * 功能:
 * - 自动将指定状态保存到 localStorage
 * - 页面刷新后自动恢复状态
 * - 支持部分状态持久化
 * - 支持自定义序列化/反序列化
 */
import { watch, toRaw } from 'vue'
import type { PiniaPluginContext } from 'pinia'

// ==================== 配置 ====================

/** 默认排除的敏感字段 */
const DEFAULT_EXCLUDE_KEYS = ['password', 'token', 'refreshToken', 'secret']

// ==================== 类型定义 ====================

interface PersistOptions {
  /** 是否启用持久化 (默认 false) */
  enabled?: boolean
  /** 自定义存储 key (默认 `pinia_${store.$id}`) */
  key?: string
  /** 需要持久化的状态路径 (默认全部) */
  paths?: string[]
  /** 需要排除的状态路径 */
  excludePaths?: string[]
  /** 需要排除的敏感字段名 (默认排除 password, token 等) */
  excludeKeys?: string[]
  /** 自定义序列化函数 */
  serialize?: (state: unknown) => string
  /** 自定义反序列化函数 */
  deserialize?: (value: string) => unknown
  /** 存储介质 (默认 localStorage) */
  storage?: Storage
  /** 防抖延迟 (毫秒) */
  debounce?: number
}

// 扩展 Pinia store 选项
declare module 'pinia' {
  export interface DefineStoreOptionsBase<S, Store> {
    persist?: PersistOptions | boolean
  }
}

// ==================== 工具函数 ====================

/**
 * 获取嵌套对象的值
 */
function getNestedValue(obj: Record<string, unknown>, path: string): unknown {
  return path.split('.').reduce((acc: unknown, key) => {
    if (acc && typeof acc === 'object' && key in acc) {
      return (acc as Record<string, unknown>)[key]
    }
    return undefined
  }, obj)
}

/**
 * 设置嵌套对象的值
 */
function setNestedValue(obj: Record<string, unknown>, path: string, value: unknown): void {
  const keys = path.split('.')
  const lastKey = keys.pop()!
  const target = keys.reduce((acc: Record<string, unknown>, key) => {
    if (!(key in acc)) {
      acc[key] = {}
    }
    return acc[key] as Record<string, unknown>
  }, obj)
  target[lastKey] = value
}

/**
 * 过滤敏感字段 (递归)
 */
function filterSensitiveKeys(
  obj: Record<string, unknown>,
  excludeKeys: string[]
): Record<string, unknown> {
  const result: Record<string, unknown> = {}
  
  for (const [key, value] of Object.entries(obj)) {
    // 跳过敏感字段
    if (excludeKeys.some(k => key.toLowerCase().includes(k.toLowerCase()))) {
      continue
    }
    
    // 递归处理嵌套对象
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      result[key] = filterSensitiveKeys(value as Record<string, unknown>, excludeKeys)
    } else {
      result[key] = value
    }
  }
  
  return result
}

/**
 * 根据 paths 过滤状态
 */
function filterState(
  state: Record<string, unknown>,
  paths?: string[],
  excludePaths?: string[],
  excludeKeys: string[] = DEFAULT_EXCLUDE_KEYS
): Record<string, unknown> {
  let result: Record<string, unknown> = {}
  
  if (paths) {
    // 只保留指定的路径
    for (const path of paths) {
      const value = getNestedValue(state, path)
      if (value !== undefined) {
        setNestedValue(result, path, value)
      }
    }
  } else {
    // 复制所有状态
    result = { ...state }
    
    // 排除指定路径
    if (excludePaths) {
      for (const path of excludePaths) {
        const keys = path.split('.')
        let target: unknown = result
        for (let i = 0; i < keys.length - 1; i++) {
          target = (target as Record<string, unknown>)[keys[i]]
          if (!target) break
        }
        if (target && typeof target === 'object') {
          delete (target as Record<string, unknown>)[keys[keys.length - 1]]
        }
      }
    }
  }
  
  // 过滤敏感字段
  result = filterSensitiveKeys(result, excludeKeys)
  
  return result
}

/**
 * 防抖函数
 */
function debounce<T extends (...args: unknown[]) => void>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout> | null = null
  return (...args: Parameters<T>) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}

// ==================== 插件主体 ====================

export function createPersistPlugin() {
  return ({ store, options }: PiniaPluginContext) => {
    const persistConfig = options.persist
    
    // 如果没有配置持久化，跳过
    if (!persistConfig) return
    
    // 解析配置
    const config: PersistOptions = persistConfig === true ? { enabled: true } : persistConfig
    if (!config.enabled) return
    
    const {
      key = `pinia_${store.$id}`,
      paths,
      excludePaths,
      excludeKeys = DEFAULT_EXCLUDE_KEYS,
      serialize = JSON.stringify,
      deserialize = JSON.parse,
      storage = localStorage,
      debounce: debounceMs = 100,
    } = config
    
    // ==================== 恢复状态 ====================
    
    try {
      const saved = storage.getItem(key)
      if (saved) {
        const parsed = deserialize(saved) as Record<string, unknown>
        store.$patch(parsed)
        console.log(`[Persist] Restored state for "${store.$id}"`)
      }
    } catch (e) {
      console.error(`[Persist] Failed to restore state for "${store.$id}":`, e)
      storage.removeItem(key)
    }
    
    // ==================== 监听并保存状态 ====================
    
    const saveState = debounce(() => {
      try {
        const state = filterState(toRaw(store.$state), paths, excludePaths, excludeKeys)
        storage.setItem(key, serialize(state))
      } catch (e) {
        console.error(`[Persist] Failed to save state for "${store.$id}":`, e)
      }
    }, debounceMs)
    
    watch(
      () => store.$state,
      saveState,
      { deep: true }
    )
    
    // ==================== 添加 $reset 钩子 ====================
    
    const originalReset = store.$reset?.bind(store)
    if (originalReset) {
      store.$reset = () => {
        originalReset()
        storage.removeItem(key)
      }
    }
  }
}

// 导出默认实例
export const persistPlugin = createPersistPlugin()

