/**
 * 测试工具函数
 */
import { mount, shallowMount, type MountingOptions, type VueWrapper } from '@vue/test-utils'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'
import { createPinia, setActivePinia, type Pinia } from 'pinia'
import ElementPlus from 'element-plus'
import type { Component } from 'vue'
import type { User, Project, Scene, Task } from '@/api'

// ==================== Mock 数据工厂 ====================

let idCounter = 0

/**
 * 生成唯一 ID
 */
export function generateId(): string {
  return `test-id-${++idCounter}`
}

/**
 * 重置 ID 计数器
 */
export function resetIdCounter(): void {
  idCounter = 0
}

/**
 * 创建 Mock 用户
 */
export function createMockUser(overrides: Partial<User> = {}): User {
  return {
    id: generateId(),
    email: 'test@example.com',
    nickname: 'Test User',
    avatar_url: null,
    role: 'user',
    status: 'active',
    created_at: new Date().toISOString(),
    ...overrides,
  }
}

/**
 * 创建 Mock 项目
 */
export function createMockProject(overrides: Partial<Project> = {}): Project {
  return {
    id: generateId(),
    title: 'Test Project',
    description: 'A test project description',
    story_text: 'Once upon a time...',
    status: 'draft',
    scene_count: 0,
    total_duration: 0,
    thumbnail_url: null,
    final_video_url: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides,
  }
}

/**
 * 创建 Mock 场景
 */
export function createMockScene(overrides: Partial<Scene> = {}): Scene {
  return {
    id: generateId(),
    project_id: generateId(),
    scene_index: 1,
    text: 'A scene description',
    scene_description: 'Visual description of the scene',
    characters: [],
    props: [],
    camera_type: 'medium shot',
    mood: 'neutral',
    image_prompt: null,
    negative_prompt: null,
    image_url: null,
    video_url: null,
    duration: 5,
    status: 'pending',
    ...overrides,
  }
}

/**
 * 创建 Mock 任务
 */
export function createMockTask(overrides: Partial<Task> = {}): Task {
  return {
    id: generateId(),
    project_id: generateId(),
    scene_id: null,
    type: 'storyboard',
    status: 'pending',
    progress: 0,
    progress_message: null,
    error_message: null,
    created_at: new Date().toISOString(),
    ...overrides,
  }
}

// ==================== 组件挂载工具 ====================

interface MountOptions<T> extends MountingOptions<T> {
  withRouter?: boolean
  withPinia?: boolean
  initialRoute?: string
  routes?: Array<{ path: string; component: Component; name?: string }>
}

/**
 * 创建测试路由
 */
export function createTestRouter(
  routes: Array<{ path: string; component: Component; name?: string }> = []
): Router {
  const defaultRoutes = [
    { path: '/', component: { template: '<div>Home</div>' }, name: 'Home' },
    { path: '/login', component: { template: '<div>Login</div>' }, name: 'Login' },
    { path: '/dashboard', component: { template: '<div>Dashboard</div>' }, name: 'Dashboard' },
    { path: '/projects/:id', component: { template: '<div>Project</div>' }, name: 'ProjectEditor' },
    ...routes,
  ]

  return createRouter({
    history: createMemoryHistory(),
    routes: defaultRoutes,
  })
}

/**
 * 创建测试 Pinia
 */
export function createTestPinia(): Pinia {
  const pinia = createPinia()
  setActivePinia(pinia)
  return pinia
}

/**
 * 完整挂载组件
 */
export async function mountComponent<T extends Component>(
  component: T,
  options: MountOptions<T> = {}
): Promise<VueWrapper<InstanceType<T>>> {
  const {
    withRouter = false,
    withPinia = true,
    initialRoute = '/',
    routes = [],
    ...mountOptions
  } = options

  const plugins: unknown[] = [ElementPlus]

  if (withPinia) {
    plugins.push(createTestPinia())
  }

  let router: Router | undefined

  if (withRouter) {
    router = createTestRouter(routes)
    await router.push(initialRoute)
    await router.isReady()
    plugins.push(router)
  }

  const wrapper = mount(component, {
    global: {
      plugins,
      stubs: {
        teleport: true,
        ...(mountOptions.global?.stubs || {}),
      },
      ...mountOptions.global,
    },
    ...mountOptions,
  } as MountingOptions<T>)

  return wrapper as VueWrapper<InstanceType<T>>
}

/**
 * 浅层挂载组件
 */
export function shallowMountComponent<T extends Component>(
  component: T,
  options: MountOptions<T> = {}
): VueWrapper<InstanceType<T>> {
  const { withPinia = true, ...mountOptions } = options

  const plugins: unknown[] = [ElementPlus]

  if (withPinia) {
    plugins.push(createTestPinia())
  }

  return shallowMount(component, {
    global: {
      plugins,
      stubs: {
        teleport: true,
        ...(mountOptions.global?.stubs || {}),
      },
      ...mountOptions.global,
    },
    ...mountOptions,
  } as MountingOptions<T>) as VueWrapper<InstanceType<T>>
}

// ==================== 异步工具 ====================

/**
 * 等待所有 Promise 完成
 */
export async function flushPromises(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

/**
 * 等待指定时间
 */
export async function wait(ms: number): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * 等待条件满足
 */
export async function waitFor(
  condition: () => boolean,
  timeout = 5000,
  interval = 50
): Promise<void> {
  const startTime = Date.now()
  
  while (!condition()) {
    if (Date.now() - startTime > timeout) {
      throw new Error('waitFor timeout')
    }
    await wait(interval)
  }
}

// ==================== 断言工具 ====================

/**
 * 检查元素是否存在
 */
export function expectElementExists(wrapper: VueWrapper, selector: string): void {
  expect(wrapper.find(selector).exists()).toBe(true)
}

/**
 * 检查元素是否不存在
 */
export function expectElementNotExists(wrapper: VueWrapper, selector: string): void {
  expect(wrapper.find(selector).exists()).toBe(false)
}

/**
 * 检查文本内容
 */
export function expectTextContent(wrapper: VueWrapper, selector: string, text: string): void {
  expect(wrapper.find(selector).text()).toContain(text)
}

// ==================== 事件工具 ====================

/**
 * 触发输入事件
 */
export async function typeInput(
  wrapper: VueWrapper,
  selector: string,
  value: string
): Promise<void> {
  const input = wrapper.find(selector)
  await input.setValue(value)
}

/**
 * 触发点击事件
 */
export async function clickElement(wrapper: VueWrapper, selector: string): Promise<void> {
  const element = wrapper.find(selector)
  await element.trigger('click')
}

/**
 * 触发表单提交
 */
export async function submitForm(wrapper: VueWrapper, selector = 'form'): Promise<void> {
  const form = wrapper.find(selector)
  await form.trigger('submit')
}

