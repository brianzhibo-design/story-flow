/**
 * Vitest 全局测试设置
 */
import { vi, beforeAll, afterEach, afterAll } from 'vitest'
import { config } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { createPinia, setActivePinia } from 'pinia'

// ==================== Mock 全局对象 ====================

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'sessionStorage', { value: sessionStorageMock })

// Mock scrollTo
window.scrollTo = vi.fn()

// Mock console.error to suppress expected errors in tests
const originalConsoleError = console.error
console.error = (...args: unknown[]) => {
  const message = args[0]
  if (
    typeof message === 'string' &&
    (message.includes('[Vue warn]') || message.includes('Expected error'))
  ) {
    return
  }
  originalConsoleError.apply(console, args)
}

// ==================== Vue Test Utils 配置 ====================

// 配置 Element Plus
config.global.plugins = [ElementPlus]

// 配置全局 stubs
config.global.stubs = {
  teleport: true,
  transition: false,
  'transition-group': false,
}

// 配置全局 mocks
config.global.mocks = {
  $t: (key: string) => key, // i18n mock
}

// ==================== 测试生命周期 ====================

beforeAll(() => {
  // 在所有测试前创建新的 Pinia 实例
  setActivePinia(createPinia())
})

afterEach(() => {
  // 每个测试后清理
  vi.clearAllMocks()
  localStorageMock.clear()
  sessionStorageMock.clear()
})

afterAll(() => {
  // 所有测试后清理
  vi.restoreAllMocks()
})

// ==================== 全局类型扩展 ====================

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace Vi {
    interface Assertion<T> {
      toBeInTheDocument(): T
      toHaveTextContent(text: string): T
      toBeVisible(): T
      toBeDisabled(): T
    }
  }
}

export {}

