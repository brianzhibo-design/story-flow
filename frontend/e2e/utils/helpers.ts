/**
 * E2E 测试工具函数和页面对象
 */
import { type Page, type Locator, expect } from '@playwright/test'

// ==================== 页面对象基类 ====================

export abstract class BasePage {
  constructor(protected page: Page) {}

  async waitForPageLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle')
  }

  async takeScreenshot(name: string): Promise<void> {
    await this.page.screenshot({ path: `test-results/screenshots/${name}.png` })
  }
}

// ==================== 认证页面对象 ====================

export class AuthPage extends BasePage {
  // 定位器
  get emailInput(): Locator {
    return this.page.locator('input[type="email"]')
  }

  get passwordInput(): Locator {
    return this.page.locator('input[type="password"]').first()
  }

  get confirmPasswordInput(): Locator {
    return this.page.locator('input[type="password"]').last()
  }

  get nicknameInput(): Locator {
    return this.page.locator('input[placeholder*="昵称"]')
  }

  get submitButton(): Locator {
    return this.page.locator('button[type="submit"]')
  }

  get loginLink(): Locator {
    return this.page.locator('a[href="/login"]')
  }

  get registerLink(): Locator {
    return this.page.locator('a[href="/register"]')
  }

  // 方法
  async goto(type: 'login' | 'register'): Promise<void> {
    await this.page.goto(`/${type}`)
    await this.waitForPageLoad()
  }

  async login(email: string, password: string): Promise<void> {
    await this.emailInput.fill(email)
    await this.passwordInput.fill(password)
    await this.submitButton.click()
  }

  async register(email: string, password: string, nickname?: string): Promise<void> {
    await this.emailInput.fill(email)
    if (nickname) {
      await this.nicknameInput.fill(nickname)
    }
    await this.passwordInput.fill(password)
    await this.confirmPasswordInput.fill(password)
    await this.submitButton.click()
  }

  async expectLoginSuccess(): Promise<void> {
    await expect(this.page).toHaveURL(/\/dashboard/)
  }

  async expectLoginError(message?: string): Promise<void> {
    const errorMessage = this.page.locator('.el-message--error')
    await expect(errorMessage).toBeVisible()
    if (message) {
      await expect(errorMessage).toContainText(message)
    }
  }
}

// ==================== 工作台页面对象 ====================

export class DashboardPage extends BasePage {
  // 定位器
  get createProjectButton(): Locator {
    return this.page.locator('button:has-text("New Project"), a:has-text("创建新项目")')
  }

  get projectCards(): Locator {
    return this.page.locator('.project-card')
  }

  get searchInput(): Locator {
    return this.page.locator('input[placeholder*="搜索"]')
  }

  get statusFilter(): Locator {
    return this.page.locator('.el-select')
  }

  get emptyState(): Locator {
    return this.page.locator('.empty-state')
  }

  get welcomeMessage(): Locator {
    return this.page.locator('h2:has-text("欢迎回来")')
  }

  // 方法
  async goto(): Promise<void> {
    await this.page.goto('/dashboard')
    await this.waitForPageLoad()
  }

  async createProject(): Promise<void> {
    await this.createProjectButton.click()
    await expect(this.page).toHaveURL(/\/projects\/create/)
  }

  async searchProjects(query: string): Promise<void> {
    await this.searchInput.fill(query)
    await this.page.waitForTimeout(500) // 等待搜索去抖
  }

  async filterByStatus(status: string): Promise<void> {
    await this.statusFilter.click()
    await this.page.locator(`.el-select-dropdown__item:has-text("${status}")`).click()
  }

  async openProject(index = 0): Promise<void> {
    await this.projectCards.nth(index).click()
    await expect(this.page).toHaveURL(/\/projects\//)
  }

  async expectProjectCount(count: number): Promise<void> {
    await expect(this.projectCards).toHaveCount(count)
  }
}

// ==================== 项目编辑器页面对象 ====================

export class ProjectEditorPage extends BasePage {
  // 定位器
  get projectTitle(): Locator {
    return this.page.locator('h1')
  }

  get statusBadge(): Locator {
    return this.page.locator('.status-badge, [class*="StatusBadge"]')
  }

  get generateButton(): Locator {
    return this.page.locator('button:has-text("开始生成")')
  }

  get exportButton(): Locator {
    return this.page.locator('button:has-text("Export Video")')
  }

  get sceneCards(): Locator {
    return this.page.locator('.scene-card')
  }

  get progressBar(): Locator {
    return this.page.locator('.el-progress')
  }

  get backButton(): Locator {
    return this.page.locator('button:has(.el-icon-arrow-left), button[title="返回"]')
  }

  // 方法
  async goto(projectId: string): Promise<void> {
    await this.page.goto(`/projects/${projectId}`)
    await this.waitForPageLoad()
  }

  async startGeneration(): Promise<void> {
    await this.generateButton.click()
  }

  async goBack(): Promise<void> {
    await this.backButton.click()
    await expect(this.page).toHaveURL(/\/dashboard/)
  }

  async expectSceneCount(count: number): Promise<void> {
    await expect(this.sceneCards).toHaveCount(count)
  }

  async waitForGeneration(timeout = 60000): Promise<void> {
    await expect(this.progressBar).toBeVisible()
    await expect(this.progressBar).not.toBeVisible({ timeout })
  }
}

// ==================== 项目创建页面对象 ====================

export class ProjectCreatePage extends BasePage {
  // 定位器
  get titleInput(): Locator {
    return this.page.locator('input[name="title"], input[placeholder*="标题"]')
  }

  get storyTextarea(): Locator {
    return this.page.locator('textarea[name="story_text"], textarea[placeholder*="故事"]')
  }

  get submitButton(): Locator {
    return this.page.locator('button[type="submit"], button:has-text("创建")')
  }

  // 方法
  async goto(): Promise<void> {
    await this.page.goto('/projects/create')
    await this.waitForPageLoad()
  }

  async fillForm(title: string, storyText: string): Promise<void> {
    await this.titleInput.fill(title)
    await this.storyTextarea.fill(storyText)
  }

  async submit(): Promise<void> {
    await this.submitButton.click()
  }

  async createProject(title: string, storyText: string): Promise<void> {
    await this.fillForm(title, storyText)
    await this.submit()
    await expect(this.page).toHaveURL(/\/projects\//)
  }
}

// ==================== API Mock 工具 ====================

/**
 * Mock API 响应
 */
export async function mockApiResponse(
  page: Page,
  urlPattern: string,
  response: unknown,
  status = 200
): Promise<void> {
  await page.route(urlPattern, async (route) => {
    await route.fulfill({
      status,
      contentType: 'application/json',
      body: JSON.stringify(response),
    })
  })
}

/**
 * Mock API 错误
 */
export async function mockApiError(
  page: Page,
  urlPattern: string,
  message = 'Internal Server Error',
  status = 500
): Promise<void> {
  await page.route(urlPattern, async (route) => {
    await route.fulfill({
      status,
      contentType: 'application/json',
      body: JSON.stringify({ code: status, message }),
    })
  })
}

/**
 * 等待 API 请求
 */
export async function waitForApiRequest(
  page: Page,
  urlPattern: string,
  method = 'GET'
): Promise<void> {
  await page.waitForRequest(
    (request) =>
      request.url().includes(urlPattern) && request.method() === method
  )
}

/**
 * 等待 API 响应
 */
export async function waitForApiResponse(
  page: Page,
  urlPattern: string
): Promise<void> {
  await page.waitForResponse((response) => response.url().includes(urlPattern))
}

// ==================== 测试数据 ====================

export const testUsers = {
  valid: {
    email: 'test@example.com',
    password: 'Password123!',
  },
  invalid: {
    email: 'invalid@example.com',
    password: 'wrong',
  },
}

export const testProjects = {
  sample: {
    title: 'Test Project',
    storyText: 'Once upon a time, in a land far away, there lived a brave hero...',
  },
}

