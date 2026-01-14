/// <reference types="vitest" />
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    // 测试环境
    environment: 'jsdom',
    
    // 全局 API
    globals: true,
    
    // 测试文件匹配
    include: ['src/**/*.{test,spec}.{js,ts,jsx,tsx}'],
    
    // 排除
    exclude: ['node_modules', 'dist', 'e2e'],
    
    // 覆盖率配置
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      reportsDirectory: './coverage',
      include: ['src/**/*.{ts,vue}'],
      exclude: [
        'src/**/*.d.ts',
        'src/**/*.test.ts',
        'src/**/*.spec.ts',
        'src/main.ts',
        'src/types/**',
      ],
      // 覆盖率阈值
      thresholds: {
        statements: 60,
        branches: 60,
        functions: 60,
        lines: 60,
      },
    },
    
    // 设置文件
    setupFiles: ['./src/test/setup.ts'],
    
    // 依赖优化
    deps: {
      inline: ['element-plus'],
    },
    
    // 模拟
    mockReset: true,
    restoreMocks: true,
    
    // 报告器
    reporters: ['default', 'html'],
    outputFile: {
      html: './test-results/index.html',
    },
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
})

