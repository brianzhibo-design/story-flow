/**
 * 应用入口
 * 
 * 初始化 Vue 应用及所有插件
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import './styles/main.css'

// 插件
import { persistPlugin } from './stores/plugins/persist'

// 指令
import { vLazy } from './directives'

// ==================== 创建应用 ====================

const app = createApp(App)

// ==================== Pinia 状态管理 ====================

const pinia = createPinia()
pinia.use(persistPlugin)
app.use(pinia)

// ==================== 路由 ====================

app.use(router)

// ==================== Element Plus ====================

app.use(ElementPlus)

// 全局注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// ==================== 自定义指令 ====================

app.directive('lazy', vLazy)

// ==================== 全局错误处理 ====================

app.config.errorHandler = (err, instance, info) => {
  console.error('[Vue Error]', err)
  console.error('[Error Info]', info)
  
  // 可以在这里添加错误上报逻辑
  // errorReporter.captureException(err, { extra: { info } })
}

app.config.warnHandler = (msg, instance, trace) => {
  if (import.meta.env.DEV) {
    console.warn('[Vue Warn]', msg)
    console.warn('[Trace]', trace)
  }
}

// ==================== 挂载应用 ====================

app.mount('#app')
