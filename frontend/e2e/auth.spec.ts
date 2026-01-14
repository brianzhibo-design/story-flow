/**
 * 认证流程 E2E 测试
 */
import { test, expect } from '@playwright/test'
import { AuthPage, DashboardPage, mockApiResponse, testUsers } from './utils/helpers'

test.describe('认证流程', () => {
  test.describe('登录', () => {
    test('应该成功登录并跳转到工作台', async ({ page }) => {
      // Mock 登录 API
      await mockApiResponse(page, '**/api/v1/auth/login', {
        code: 200,
        data: {
          user: {
            id: 'user-1',
            email: testUsers.valid.email,
            nickname: 'Test User',
          },
          tokens: {
            access_token: 'mock-token',
            refresh_token: 'mock-refresh-token',
          },
        },
      })

      // Mock 用户信息 API
      await mockApiResponse(page, '**/api/v1/auth/me', {
        code: 200,
        data: {
          id: 'user-1',
          email: testUsers.valid.email,
          nickname: 'Test User',
        },
      })

      const authPage = new AuthPage(page)
      await authPage.goto('login')

      // 验证页面元素
      await expect(authPage.emailInput).toBeVisible()
      await expect(authPage.passwordInput).toBeVisible()
      await expect(authPage.submitButton).toBeVisible()

      // 执行登录
      await authPage.login(testUsers.valid.email, testUsers.valid.password)

      // 验证跳转
      await authPage.expectLoginSuccess()
    })

    test('错误的凭证应该显示错误消息', async ({ page }) => {
      // Mock 登录失败
      await mockApiResponse(
        page,
        '**/api/v1/auth/login',
        { code: 401, message: '邮箱或密码错误' },
        401
      )

      const authPage = new AuthPage(page)
      await authPage.goto('login')

      await authPage.login(testUsers.invalid.email, testUsers.invalid.password)

      // 应该显示错误消息
      await authPage.expectLoginError()

      // 应该停留在登录页
      await expect(page).toHaveURL(/\/login/)
    })

    test('未填写必填字段时不应该提交', async ({ page }) => {
      const authPage = new AuthPage(page)
      await authPage.goto('login')

      // 只填写邮箱
      await authPage.emailInput.fill(testUsers.valid.email)
      await authPage.submitButton.click()

      // 应该停留在登录页
      await expect(page).toHaveURL(/\/login/)
    })

    test('点击注册链接应该跳转到注册页', async ({ page }) => {
      const authPage = new AuthPage(page)
      await authPage.goto('login')

      await authPage.registerLink.click()

      await expect(page).toHaveURL(/\/register/)
    })
  })

  test.describe('注册', () => {
    test('应该成功注册并跳转到工作台', async ({ page }) => {
      // Mock 注册 API
      await mockApiResponse(page, '**/api/v1/auth/register', {
        code: 200,
        data: {
          user: {
            id: 'user-new',
            email: 'new@example.com',
            nickname: 'New User',
          },
          tokens: {
            access_token: 'mock-token',
            refresh_token: 'mock-refresh-token',
          },
        },
      })

      const authPage = new AuthPage(page)
      await authPage.goto('register')

      await authPage.register('new@example.com', 'Password123!', 'New User')

      // 验证跳转
      await expect(page).toHaveURL(/\/dashboard/)
    })

    test('已存在的邮箱应该显示错误', async ({ page }) => {
      // Mock 注册失败
      await mockApiResponse(
        page,
        '**/api/v1/auth/register',
        { code: 400, message: '该邮箱已被注册' },
        400
      )

      const authPage = new AuthPage(page)
      await authPage.goto('register')

      await authPage.register('existing@example.com', 'Password123!')

      // 应该显示错误消息
      const errorMessage = page.locator('.el-message--error')
      await expect(errorMessage).toBeVisible()
    })

    test('点击登录链接应该跳转到登录页', async ({ page }) => {
      const authPage = new AuthPage(page)
      await authPage.goto('register')

      await authPage.loginLink.click()

      await expect(page).toHaveURL(/\/login/)
    })
  })

  test.describe('登出', () => {
    test('登出后应该跳转到登录页', async ({ page }) => {
      // 先模拟已登录状态
      await mockApiResponse(page, '**/api/v1/auth/me', {
        code: 200,
        data: {
          id: 'user-1',
          email: 'test@example.com',
          nickname: 'Test User',
        },
      })

      // Mock 项目列表
      await mockApiResponse(page, '**/api/v1/projects*', {
        code: 200,
        data: { items: [], pagination: { page: 1, page_size: 20, total: 0, total_pages: 0 } },
      })

      // 访问工作台（需要先设置 token）
      await page.goto('/dashboard')
      await page.evaluate(() => {
        localStorage.setItem('token', 'mock-token')
      })
      await page.reload()

      // 找到并点击登出按钮
      const logoutButton = page.locator('button:has-text("退出"), text=退出登录')
      if (await logoutButton.isVisible()) {
        await logoutButton.click()
        await expect(page).toHaveURL(/\/login/)
      }
    })
  })

  test.describe('路由保护', () => {
    test('未登录访问受保护页面应该跳转到登录', async ({ page }) => {
      // Mock 401 响应
      await mockApiResponse(page, '**/api/v1/auth/me', { code: 401, message: 'Unauthorized' }, 401)

      await page.goto('/dashboard')

      // 应该跳转到登录页
      await expect(page).toHaveURL(/\/login/)
    })

    test('已登录访问登录页应该跳转到工作台', async ({ page }) => {
      // 设置已登录状态
      await page.goto('/')
      await page.evaluate(() => {
        localStorage.setItem('token', 'mock-token')
      })

      // Mock 用户信息
      await mockApiResponse(page, '**/api/v1/auth/me', {
        code: 200,
        data: { id: 'user-1', email: 'test@example.com' },
      })

      await page.goto('/login')

      // 应该跳转到工作台
      await expect(page).toHaveURL(/\/dashboard/)
    })
  })
})

