/**
 * 视觉回归测试
 */
import { test, expect } from '@playwright/test'
import { AuthPage, DashboardPage, mockApiResponse } from './utils/helpers'

test.describe('视觉回归测试', () => {
  test.describe('首页', () => {
    test('首页应该匹配快照', async ({ page }) => {
      await page.goto('/')
      await page.waitForLoadState('networkidle')

      await expect(page).toHaveScreenshot('home-page.png', {
        fullPage: true,
        animations: 'disabled',
      })
    })

    test('首页移动端视图', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 812 })
      await page.goto('/')
      await page.waitForLoadState('networkidle')

      await expect(page).toHaveScreenshot('home-page-mobile.png', {
        fullPage: true,
        animations: 'disabled',
      })
    })
  })

  test.describe('登录页', () => {
    test('登录页应该匹配快照', async ({ page }) => {
      const authPage = new AuthPage(page)
      await authPage.goto('login')

      await expect(page).toHaveScreenshot('login-page.png', {
        fullPage: true,
        animations: 'disabled',
      })
    })

    test('登录页移动端视图', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 812 })
      const authPage = new AuthPage(page)
      await authPage.goto('login')

      await expect(page).toHaveScreenshot('login-page-mobile.png', {
        fullPage: true,
        animations: 'disabled',
      })
    })
  })

  test.describe('注册页', () => {
    test('注册页应该匹配快照', async ({ page }) => {
      const authPage = new AuthPage(page)
      await authPage.goto('register')

      await expect(page).toHaveScreenshot('register-page.png', {
        fullPage: true,
        animations: 'disabled',
      })
    })
  })

  test.describe('工作台', () => {
    test.beforeEach(async ({ page }) => {
      // Mock 用户认证
      await mockApiResponse(page, '**/api/v1/auth/me', {
        code: 200,
        data: { id: 'user-1', email: 'test@example.com', nickname: 'Test User' },
      })

      // 设置 token
      await page.goto('/')
      await page.evaluate(() => {
        localStorage.setItem('token', 'mock-token')
      })
    })

    test('工作台空状态', async ({ page }) => {
      await mockApiResponse(page, '**/api/v1/projects*', {
        code: 200,
        data: { items: [], pagination: { page: 1, page_size: 20, total: 0, total_pages: 0 } },
      })

      await mockApiResponse(page, '**/api/v1/quota/status', {
        code: 200,
        data: { credits: { used: 0, total: 100, remaining: 100 } },
      })

      const dashboard = new DashboardPage(page)
      await dashboard.goto()

      await expect(page).toHaveScreenshot('dashboard-empty.png', {
        fullPage: true,
        animations: 'disabled',
      })
    })

    test('工作台有项目', async ({ page }) => {
      await mockApiResponse(page, '**/api/v1/projects*', {
        code: 200,
        data: {
          items: [
            { id: 'p1', title: 'My First Project', status: 'completed', scene_count: 5 },
            { id: 'p2', title: 'Work in Progress', status: 'processing', scene_count: 3 },
            { id: 'p3', title: 'Draft Project', status: 'draft', scene_count: 0 },
          ],
          pagination: { page: 1, page_size: 20, total: 3, total_pages: 1 },
        },
      })

      await mockApiResponse(page, '**/api/v1/quota/status', {
        code: 200,
        data: { credits: { used: 50, total: 100, remaining: 50 } },
      })

      const dashboard = new DashboardPage(page)
      await dashboard.goto()

      await expect(page).toHaveScreenshot('dashboard-with-projects.png', {
        fullPage: true,
        animations: 'disabled',
      })
    })
  })

  test.describe('组件视觉测试', () => {
    test('状态徽章组件', async ({ page }) => {
      // 创建一个展示所有状态徽章的测试页面
      await page.setContent(`
        <!DOCTYPE html>
        <html>
          <head>
            <style>
              body { 
                font-family: Inter, sans-serif; 
                padding: 24px; 
                background: #f8fafc;
              }
              .badge-row {
                display: flex;
                gap: 12px;
                margin-bottom: 16px;
              }
              .badge {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                font-size: 10px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                padding: 2px 8px;
                border-radius: 9999px;
                border: 1px solid;
              }
              .badge-completed { color: #059669; background: #ecfdf5; border-color: #d1fae5; }
              .badge-processing { color: #ea580c; background: #fff7ed; border-color: #fed7aa; }
              .badge-pending { color: #64748b; background: #f8fafc; border-color: #e2e8f0; }
              .badge-failed { color: #dc2626; background: #fef2f2; border-color: #fecaca; }
              .badge-draft { color: #a16207; background: #fefce8; border-color: #fef08a; }
            </style>
          </head>
          <body>
            <h2>Status Badges</h2>
            <div class="badge-row">
              <span class="badge badge-completed">● Rendered</span>
              <span class="badge badge-processing">● Processing</span>
              <span class="badge badge-pending">● Pending</span>
              <span class="badge badge-failed">● Failed</span>
              <span class="badge badge-draft">● Draft</span>
            </div>
          </body>
        </html>
      `)

      await expect(page).toHaveScreenshot('status-badges.png')
    })
  })
})

