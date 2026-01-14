/**
 * StoryFlow Pro - Tailwind CSS 配置
 * 
 * 使用 UI UX Pro Max 推荐的设计规范:
 * - 字体: Poppins (标题) + Open Sans (正文)
 * - 配色: SaaS 专业蓝紫配色
 * - 风格: Soft UI Evolution + Glassmorphism
 */

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      // 字体 - UI UX Pro Max Modern Professional 推荐
      fontFamily: {
        sans: ['Open Sans', 'system-ui', '-apple-system', 'sans-serif'],
        heading: ['Poppins', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      
      // 扩展颜色 - SaaS 专业配色
      colors: {
        slate: {
          850: '#151e2e',
          950: '#0a0f1a',
        },
        // 品牌主色 - Indigo 系列
        brand: {
          50: '#EEF2FF',
          100: '#E0E7FF',
          200: '#C7D2FE',
          300: '#A5B4FC',
          400: '#818CF8',
          500: '#6366F1',
          600: '#4F46E5',
          700: '#4338CA',
          800: '#3730A3',
          900: '#312E81',
        },
        // CTA 强调色 - Orange
        accent: {
          50: '#FFF7ED',
          100: '#FFEDD5',
          200: '#FED7AA',
          300: '#FDBA74',
          400: '#FB923C',
          500: '#F97316',
          600: '#EA580C',
          700: '#C2410C',
        },
      },
      
      // 阴影 - Soft UI 风格
      boxShadow: {
        'glow': '0 0 20px -5px rgba(79, 70, 229, 0.3)',
        'glow-lg': '0 0 30px -5px rgba(79, 70, 229, 0.4)',
        'glow-success': '0 0 20px -5px rgba(16, 185, 129, 0.3)',
        'glow-warning': '0 0 20px -5px rgba(249, 115, 22, 0.3)',
        'glow-purple': '0 0 20px -5px rgba(139, 92, 246, 0.3)',
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.03)',
        'card': '0 1px 3px rgba(0, 0, 0, 0.02)',
        'card-hover': '0 20px 30px -10px rgba(0, 0, 0, 0.1), 0 10px 15px -5px rgba(0, 0, 0, 0.04)',
        'floating': '0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01)',
        'inner-soft': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.02)',
      },
      
      // 圆角
      borderRadius: {
        'xl': '12px',
        '2xl': '16px',
        '3xl': '20px',
        '4xl': '24px',
      },
      
      // 字体大小
      fontSize: {
        'xxs': ['10px', { lineHeight: '14px' }],
      },
      
      // 动画 - 200-300ms 最佳体验
      animation: {
        'shimmer': 'shimmer 2s infinite linear',
        'pulse-slow': 'pulse 3s infinite',
        'spin-slow': 'spin 2s linear infinite',
        'bounce-subtle': 'bounce-subtle 2s infinite',
        'fade-in': 'fade-in 0.3s ease-out',
        'fade-in-up': 'fade-in-up 0.4s ease-out',
        'slide-up': 'slide-up 0.3s ease-out',
        'slide-down': 'slide-down 0.3s ease-out',
        'scale-in': 'scale-in 0.2s ease-out',
        'aurora': 'aurora 15s ease-in-out infinite',
      },
      
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        'bounce-subtle': {
          '0%, 100%': { transform: 'translateY(-5%)' },
          '50%': { transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-down': {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'scale-in': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        'aurora': {
          '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
          '25%': { transform: 'translate(30px, -30px) scale(1.1)' },
          '50%': { transform: 'translate(-20px, 20px) scale(0.95)' },
          '75%': { transform: 'translate(20px, 10px) scale(1.05)' },
        },
      },
      
      // 过渡时间
      transitionDuration: {
        '250': '250ms',
      },
      
      // 过渡函数 - ease-out 推荐
      transitionTimingFunction: {
        'out-expo': 'cubic-bezier(0.19, 1, 0.22, 1)',
        'spring': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
        'out': 'cubic-bezier(0.25, 0.8, 0.25, 1)',
      },
      
      // 背景图
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'shimmer': 'linear-gradient(to right, #f6f7f8 0%, #e2e8f0 20%, #f6f7f8 40%, #f6f7f8 100%)',
        'aurora': 'linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899)',
      },
      
      // 宽高比
      aspectRatio: {
        'video': '16 / 9',
        'square': '1 / 1',
        'portrait': '3 / 4',
        'vertical': '9 / 16',
      },
    },
  },
  plugins: [],
}
