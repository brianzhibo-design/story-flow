/**
 * ESLint 配置
 * 
 * 规则说明:
 * - 使用 Vue 3 推荐规则
 * - 使用 TypeScript 推荐规则
 * - 与 Prettier 兼容
 */
module.exports = {
  root: true,
  env: {
    browser: true,
    es2022: true,
    node: true,
  },
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    ecmaVersion: 2022,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:vue/vue3-recommended',
    'prettier',
  ],
  plugins: ['@typescript-eslint', 'vue'],
  rules: {
    // Vue 规则
    'vue/multi-word-component-names': 'off', // 允许单词组件名
    'vue/no-v-html': 'off', // 允许 v-html
    'vue/require-default-prop': 'off', // 不强制 props 默认值
    'vue/require-prop-types': 'off', // 使用 TypeScript 类型
    'vue/component-definition-name-casing': ['error', 'PascalCase'],
    'vue/html-self-closing': ['error', {
      html: { void: 'always', normal: 'never', component: 'always' },
      svg: 'always',
      math: 'always',
    }],
    
    // TypeScript 规则
    '@typescript-eslint/no-explicit-any': 'warn', // any 类型警告
    '@typescript-eslint/explicit-function-return-type': 'off', // 不强制返回类型
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-unused-vars': ['warn', { 
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_',
    }],
    '@typescript-eslint/no-non-null-assertion': 'off', // 允许非空断言
    '@typescript-eslint/ban-ts-comment': 'off', // 允许 ts 注释
    
    // 通用规则
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'prefer-const': 'error',
    'no-var': 'error',
    'object-shorthand': 'error',
    'prefer-template': 'error',
  },
  ignorePatterns: [
    'dist',
    'node_modules',
    '*.d.ts',
    'vite.config.ts',
  ],
}

