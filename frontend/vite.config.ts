import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
      },
    },
    
    // 定义全局变量
    define: {
      __APP_VERSION__: JSON.stringify(env.npm_package_version || '1.0.0'),
    },
    
    // 依赖优化
    optimizeDeps: {
      include: [
        'dayjs',
        'dayjs/plugin/customParseFormat',
        'dayjs/plugin/advancedFormat',
        'dayjs/plugin/localeData',
        'dayjs/plugin/weekOfYear',
        'dayjs/plugin/weekYear',
        'dayjs/plugin/dayOfYear',
        'dayjs/plugin/isSameOrAfter',
        'dayjs/plugin/isSameOrBefore',
      ],
    },
    
    // 开发服务器配置
    server: {
      port: 3000,
      host: true, // 监听所有地址
      proxy: {
        '/api': {
          target: env.VITE_API_PROXY_TARGET || 'http://localhost:8000',
          changeOrigin: true,
        },
        '/ws': {
          target: env.VITE_WS_PROXY_TARGET || 'ws://localhost:8000',
          ws: true,
        },
      },
    },
    
    // 构建配置
    build: {
      outDir: 'dist',
      sourcemap: mode === 'development',
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: mode === 'production',
          drop_debugger: true,
        },
      },
      rollupOptions: {
        output: {
          // 分块策略
          manualChunks: {
            'vendor': ['vue', 'vue-router', 'pinia'],
            'element-plus': ['element-plus'],
            'utils': ['axios', 'dayjs'],
          },
        },
      },
      // 资产大小警告阈值
      chunkSizeWarningLimit: 1000,
    },
    
    // CSS 配置
    css: {
      devSourcemap: true,
    },
  }
})
