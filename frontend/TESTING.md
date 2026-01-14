# StoryFlow 测试指南

本文档介绍项目的测试配置和使用方法。

## 📋 目录

- [测试架构](#测试架构)
- [单元测试 (Vitest)](#单元测试-vitest)
- [E2E 测试 (Playwright)](#e2e-测试-playwright)
- [测试命令](#测试命令)
- [编写测试](#编写测试)

---

## 测试架构

```
frontend/
├── src/
│   ├── test/                          # 单元测试配置
│   │   ├── setup.ts                   # 全局测试设置
│   │   ├── utils.ts                   # 测试工具函数
│   │   ├── mocks/
│   │   │   └── api.ts                 # API Mock
│   │   └── index.ts                   # 统一导出
│   ├── stores/__tests__/              # Store 测试
│   ├── composables/__tests__/         # Composables 测试
│   └── components/**/__tests__/       # 组件测试
├── e2e/                               # E2E 测试
│   ├── utils/
│   │   └── helpers.ts                 # E2E 工具函数和页面对象
│   ├── auth.spec.ts                   # 认证流程测试
│   ├── project.spec.ts                # 项目流程测试
│   └── visual.spec.ts                 # 视觉回归测试
├── vitest.config.ts                   # Vitest 配置
└── playwright.config.ts               # Playwright 配置
```

---

## 单元测试 (Vitest)

### 配置说明

- **测试环境**: jsdom (模拟浏览器环境)
- **全局 API**: describe, it, expect
- **覆盖率阈值**: 60%

### 测试工具

**Mock 数据工厂**:

```typescript
import { createMockUser, createMockProject, createMockScene } from '@/test'

const user = createMockUser({ email: 'test@example.com' })
const project = createMockProject({ status: 'completed' })
const scene = createMockScene({ scene_index: 1 })
```

**API Mock**:

```typescript
import { mockAuthApi, mockProjectsApi } from '@/test'

vi.mock('@/api', () => ({
  authApi: mockAuthApi,
  projectsApi: mockProjectsApi,
}))
```

**组件挂载**:

```typescript
import { mountComponent, shallowMountComponent } from '@/test'

// 完整挂载（含路由）
const wrapper = await mountComponent(MyComponent, {
  withRouter: true,
  initialRoute: '/dashboard',
})

// 浅层挂载
const wrapper = shallowMountComponent(MyComponent, {
  props: { title: 'Test' },
})
```

---

## E2E 测试 (Playwright)

### 配置说明

- **基础 URL**: http://localhost:3000
- **浏览器**: Chromium, Firefox, WebKit
- **移动端**: Pixel 5, iPhone 12

### 页面对象模式

```typescript
import { AuthPage, DashboardPage, ProjectEditorPage } from './utils/helpers'

test('should login and create project', async ({ page }) => {
  const authPage = new AuthPage(page)
  await authPage.goto('login')
  await authPage.login('test@example.com', 'password')
  await authPage.expectLoginSuccess()

  const dashboard = new DashboardPage(page)
  await dashboard.createProject()
})
```

### Mock API 响应

```typescript
import { mockApiResponse } from './utils/helpers'

await mockApiResponse(page, '**/api/v1/projects', {
  code: 200,
  data: [{ id: '1', title: 'Test Project' }],
})
```

---

## 测试命令

### 单元测试

```bash
# 运行所有单元测试
npm run test

# 运行一次（CI 模式）
npm run test:run

# 交互式 UI
npm run test:ui

# 生成覆盖率报告
npm run test:coverage

# 监听模式（开发时）
npm run test -- --watch
```

### E2E 测试

```bash
# 运行所有 E2E 测试
npm run test:e2e

# 交互式 UI
npm run test:e2e:ui

# 调试模式
npm run test:e2e:debug

# 查看测试报告
npm run test:e2e:report

# 指定浏览器
npx playwright test --project=chromium

# 运行特定文件
npx playwright test e2e/auth.spec.ts

# 更新截图基线
npx playwright test --update-snapshots
```

### 全部测试

```bash
# 运行单元测试 + E2E 测试
npm run test:all
```

---

## 编写测试

### 单元测试示例

**Store 测试**:

```typescript
// src/stores/__tests__/user.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/stores/user'

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should login successfully', async () => {
    const store = useUserStore()
    await store.doLogin({ email: 'test@example.com', password: 'password' })
    expect(store.isLoggedIn).toBe(true)
  })
})
```

**组件测试**:

```typescript
// src/components/__tests__/StatusBadge.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatusBadge from '@/components/common/StatusBadge.vue'

describe('StatusBadge', () => {
  it('should render correct status text', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'completed' },
    })
    expect(wrapper.text()).toContain('Rendered')
  })
})
```

### E2E 测试示例

```typescript
// e2e/example.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Example Flow', () => {
  test('should complete user journey', async ({ page }) => {
    // 1. 访问首页
    await page.goto('/')
    
    // 2. 点击登录
    await page.click('text=登录')
    
    // 3. 填写表单
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'password')
    
    // 4. 提交
    await page.click('button[type="submit"]')
    
    // 5. 验证结果
    await expect(page).toHaveURL('/dashboard')
  })
})
```

---

## 最佳实践

1. **测试命名**: 使用描述性名称，如 `should login successfully with valid credentials`

2. **测试隔离**: 每个测试应独立运行，不依赖其他测试

3. **Mock 策略**:
   - 单元测试：Mock 外部依赖（API、路由）
   - E2E 测试：尽量使用真实环境，必要时 Mock API

4. **覆盖率目标**:
   - 核心业务逻辑：80%+
   - 工具函数：90%+
   - 组件：60%+

5. **E2E 选择器**: 优先使用 `data-testid`，避免依赖样式类名

---

*文档更新时间: 2025-01-01*

