import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright E2E 测试配置
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // 测试文件目录
  testDir: './e2e',

  // 测试文件匹配
  testMatch: '**/*.spec.ts',

  // 完全并行运行测试
  fullyParallel: true,

  // CI 环境下禁止 .only
  forbidOnly: !!process.env.CI,

  // CI 环境下重试次数
  retries: process.env.CI ? 2 : 0,

  // 并行工作进程数
  workers: process.env.CI ? 1 : undefined,

  // 报告器
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'playwright-report/results.json' }],
  ],

  // 全局测试超时
  timeout: 30 * 1000,

  // 断言超时
  expect: {
    timeout: 5000,
  },

  // 共享配置
  use: {
    // 基础 URL
    baseURL: 'http://localhost:3000',

    // 收集失败测试的 trace
    trace: 'on-first-retry',

    // 截图
    screenshot: 'only-on-failure',

    // 视频录制
    video: 'on-first-retry',

    // 视口大小
    viewport: { width: 1280, height: 720 },

    // 地理位置
    locale: 'zh-CN',
    timezoneId: 'Asia/Shanghai',

    // 忽略 HTTPS 错误
    ignoreHTTPSErrors: true,

    // 操作超时
    actionTimeout: 10000,
    navigationTimeout: 15000,
  },

  // 项目配置（不同浏览器）
  projects: [
    // 桌面浏览器
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    // 移动端浏览器
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // 开发服务器
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },

  // 输出目录
  outputDir: 'test-results',
})

