/**
 * 图片懒加载指令
 * 
 * 使用方式:
 * <img v-lazy="imageUrl" />
 * <img v-lazy="{ src: imageUrl, placeholder: placeholderUrl }" />
 * 
 * 功能:
 * - 使用 IntersectionObserver 实现懒加载
 * - 支持占位图
 * - 支持加载动画
 * - 支持加载失败处理
 */
import type { Directive, DirectiveBinding } from 'vue'

// ==================== 类型定义 ====================

interface LazyImageOptions {
  src: string
  placeholder?: string
  error?: string
  threshold?: number
  rootMargin?: string
}

type LazyImageValue = string | LazyImageOptions

// ==================== 配置 ====================

const DEFAULT_PLACEHOLDER = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200"%3E%3Crect fill="%23f0f0f0" width="300" height="200"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%23999" font-size="14"%3E加载中...%3C/text%3E%3C/svg%3E'

const DEFAULT_ERROR_IMAGE = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200"%3E%3Crect fill="%23f5f5f5" width="300" height="200"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" fill="%23999" font-size="14"%3E加载失败%3C/text%3E%3C/svg%3E'

// ==================== 观察者实例 ====================

const observerMap = new Map<HTMLElement, IntersectionObserver>()

// ==================== 工具函数 ====================

function parseValue(value: LazyImageValue): LazyImageOptions {
  if (typeof value === 'string') {
    return { src: value }
  }
  return value
}

function loadImage(el: HTMLImageElement, src: string, errorSrc: string) {
  // 添加加载动画类
  el.classList.add('lazy-loading')
  
  // 创建临时图片用于预加载
  const img = new Image()
  
  img.onload = () => {
    el.src = src
    el.classList.remove('lazy-loading')
    el.classList.add('lazy-loaded')
  }
  
  img.onerror = () => {
    el.src = errorSrc
    el.classList.remove('lazy-loading')
    el.classList.add('lazy-error')
  }
  
  img.src = src
}

// ==================== 指令定义 ====================

export const vLazy: Directive<HTMLImageElement, LazyImageValue> = {
  mounted(el: HTMLImageElement, binding: DirectiveBinding<LazyImageValue>) {
    const options = parseValue(binding.value)
    const {
      src,
      placeholder = DEFAULT_PLACEHOLDER,
      error = DEFAULT_ERROR_IMAGE,
      threshold = 0.1,
      rootMargin = '100px',
    } = options
    
    // 设置占位图
    el.src = placeholder
    el.classList.add('lazy-image')
    
    // 创建 IntersectionObserver
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            loadImage(el, src, error)
            observer.unobserve(el)
            observerMap.delete(el)
          }
        })
      },
      {
        threshold,
        rootMargin,
      }
    )
    
    observer.observe(el)
    observerMap.set(el, observer)
  },
  
  updated(el: HTMLImageElement, binding: DirectiveBinding<LazyImageValue>) {
    const oldOptions = parseValue(binding.oldValue as LazyImageValue)
    const newOptions = parseValue(binding.value)
    
    // 如果 src 变化，重新加载
    if (oldOptions.src !== newOptions.src) {
      const observer = observerMap.get(el)
      if (observer) {
        observer.unobserve(el)
      }
      
      el.classList.remove('lazy-loaded', 'lazy-error')
      loadImage(el, newOptions.src, newOptions.error || DEFAULT_ERROR_IMAGE)
    }
  },
  
  unmounted(el: HTMLImageElement) {
    const observer = observerMap.get(el)
    if (observer) {
      observer.unobserve(el)
      observerMap.delete(el)
    }
  },
}

// ==================== 样式注入 ====================

const style = document.createElement('style')
style.textContent = `
  .lazy-image {
    transition: opacity 0.3s ease;
  }
  
  .lazy-loading {
    opacity: 0.5;
  }
  
  .lazy-loaded {
    opacity: 1;
  }
  
  .lazy-error {
    opacity: 0.7;
    filter: grayscale(100%);
  }
`
document.head.appendChild(style)

export default vLazy

