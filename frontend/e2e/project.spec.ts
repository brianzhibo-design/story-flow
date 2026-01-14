/**
 * 项目流程 E2E 测试
 */
import { test, expect } from '@playwright/test'
import {
  DashboardPage,
  ProjectEditorPage,
  ProjectCreatePage,
  mockApiResponse,
  testProjects,
} from './utils/helpers'

// 设置已登录状态
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

test.describe('项目列表', () => {
  test('应该显示项目列表', async ({ page }) => {
    // Mock 项目列表
    await mockApiResponse(page, '**/api/v1/projects*', {
      code: 200,
      data: {
        items: [
          { id: 'p1', title: 'Project 1', status: 'draft', scene_count: 0 },
          { id: 'p2', title: 'Project 2', status: 'completed', scene_count: 5 },
        ],
        pagination: { page: 1, page_size: 20, total: 2, total_pages: 1 },
      },
    })

    const dashboard = new DashboardPage(page)
    await dashboard.goto()

    await dashboard.expectProjectCount(2)
  })

  test('空项目列表应该显示空状态', async ({ page }) => {
    // Mock 空项目列表
    await mockApiResponse(page, '**/api/v1/projects*', {
      code: 200,
      data: {
        items: [],
        pagination: { page: 1, page_size: 20, total: 0, total_pages: 0 },
      },
    })

    const dashboard = new DashboardPage(page)
    await dashboard.goto()

    await expect(dashboard.emptyState).toBeVisible()
  })

  test('搜索应该过滤项目', async ({ page }) => {
    // Mock 项目列表
    await mockApiResponse(page, '**/api/v1/projects*', {
      code: 200,
      data: {
        items: [
          { id: 'p1', title: 'My Project', status: 'draft', scene_count: 0 },
          { id: 'p2', title: 'Another One', status: 'completed', scene_count: 5 },
        ],
        pagination: { page: 1, page_size: 20, total: 2, total_pages: 1 },
      },
    })

    const dashboard = new DashboardPage(page)
    await dashboard.goto()

    await dashboard.searchProjects('My')

    // 搜索是前端过滤，所以需要等待结果
    await page.waitForTimeout(600)
  })
})

test.describe('创建项目', () => {
  test('应该成功创建项目', async ({ page }) => {
    // Mock 创建项目 API
    await mockApiResponse(page, '**/api/v1/projects', {
      code: 200,
      data: {
        id: 'new-project-id',
        title: testProjects.sample.title,
        story_text: testProjects.sample.storyText,
        status: 'draft',
        scene_count: 0,
      },
    })

    // Mock 项目详情
    await mockApiResponse(page, '**/api/v1/projects/new-project-id', {
      code: 200,
      data: {
        id: 'new-project-id',
        title: testProjects.sample.title,
        story_text: testProjects.sample.storyText,
        status: 'draft',
        scenes: [],
      },
    })

    const createPage = new ProjectCreatePage(page)
    await createPage.goto()

    await createPage.createProject(testProjects.sample.title, testProjects.sample.storyText)
  })

  test('未填写必填字段不应该提交', async ({ page }) => {
    const createPage = new ProjectCreatePage(page)
    await createPage.goto()

    // 只填写标题
    await createPage.titleInput.fill(testProjects.sample.title)
    await createPage.submit()

    // 应该停留在创建页
    await expect(page).toHaveURL(/\/projects\/create/)
  })
})

test.describe('项目编辑', () => {
  test('应该显示项目详情', async ({ page }) => {
    // Mock 项目详情
    await mockApiResponse(page, '**/api/v1/projects/test-project', {
      code: 200,
      data: {
        id: 'test-project',
        title: 'Test Project',
        story_text: 'Story content...',
        status: 'draft',
        scenes: [
          { id: 's1', scene_index: 1, text: 'Scene 1', status: 'pending' },
          { id: 's2', scene_index: 2, text: 'Scene 2', status: 'pending' },
        ],
      },
    })

    const editor = new ProjectEditorPage(page)
    await editor.goto('test-project')

    await expect(editor.projectTitle).toContainText('Test Project')
    await editor.expectSceneCount(2)
  })

  test('草稿项目应该显示生成按钮', async ({ page }) => {
    // Mock 项目详情
    await mockApiResponse(page, '**/api/v1/projects/draft-project', {
      code: 200,
      data: {
        id: 'draft-project',
        title: 'Draft Project',
        status: 'draft',
        scenes: [],
      },
    })

    const editor = new ProjectEditorPage(page)
    await editor.goto('draft-project')

    await expect(editor.generateButton).toBeVisible()
  })

  test('已完成项目应该显示导出按钮', async ({ page }) => {
    // Mock 项目详情
    await mockApiResponse(page, '**/api/v1/projects/completed-project', {
      code: 200,
      data: {
        id: 'completed-project',
        title: 'Completed Project',
        status: 'completed',
        scenes: [
          { id: 's1', scene_index: 1, status: 'completed', video_url: 'http://example.com/v.mp4' },
        ],
      },
    })

    const editor = new ProjectEditorPage(page)
    await editor.goto('completed-project')

    await expect(editor.exportButton).toBeVisible()
  })

  test('点击返回应该回到工作台', async ({ page }) => {
    // Mock 项目详情
    await mockApiResponse(page, '**/api/v1/projects/test-project', {
      code: 200,
      data: {
        id: 'test-project',
        title: 'Test Project',
        status: 'draft',
        scenes: [],
      },
    })

    // Mock 项目列表
    await mockApiResponse(page, '**/api/v1/projects*', {
      code: 200,
      data: { items: [], pagination: { page: 1, page_size: 20, total: 0, total_pages: 0 } },
    })

    const editor = new ProjectEditorPage(page)
    await editor.goto('test-project')

    await editor.goBack()
  })
})

test.describe('生成流程', () => {
  test('应该能够触发生成', async ({ page }) => {
    // Mock 项目详情
    await mockApiResponse(page, '**/api/v1/projects/gen-project', {
      code: 200,
      data: {
        id: 'gen-project',
        title: 'Generate Project',
        status: 'draft',
        scenes: [],
      },
    })

    // Mock 生成 API
    await mockApiResponse(page, '**/api/v1/projects/gen-project/generate', {
      code: 200,
      data: { task_id: 'task-123' },
    })

    const editor = new ProjectEditorPage(page)
    await editor.goto('gen-project')

    await editor.startGeneration()

    // 验证消息提示
    const successMessage = page.locator('.el-message--success')
    await expect(successMessage).toBeVisible()
  })
})

