/**
 * EmptyState 组件单元测试
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EmptyState from '../EmptyState.vue'
import ElementPlus from 'element-plus'

describe('EmptyState', () => {
  const globalConfig = {
    plugins: [ElementPlus],
    stubs: {
      'el-icon': {
        template: '<span class="el-icon"><slot /></span>',
      },
    },
  }

  it('应该渲染标题', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'No items found' },
      global: globalConfig,
    })

    expect(wrapper.find('h3').text()).toBe('No items found')
  })

  it('应该渲染描述', () => {
    const wrapper = mount(EmptyState, {
      props: {
        title: 'No items found',
        description: 'Create your first item',
      },
      global: globalConfig,
    })

    expect(wrapper.find('p').text()).toBe('Create your first item')
  })

  it('没有描述时不应该渲染 p 标签', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'No items found' },
      global: globalConfig,
    })

    expect(wrapper.find('p').exists()).toBe(false)
  })

  it('应该渲染默认图标', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'No items found' },
      global: globalConfig,
    })

    expect(wrapper.find('.el-icon').exists()).toBe(true)
  })

  it('应该渲染自定义图片', () => {
    const wrapper = mount(EmptyState, {
      props: {
        title: 'No items found',
        image: 'http://example.com/image.png',
      },
      global: globalConfig,
    })

    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('http://example.com/image.png')
  })

  it('应该渲染插槽内容', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'No items found' },
      slots: {
        default: '<button class="action-btn">Create Item</button>',
      },
      global: globalConfig,
    })

    expect(wrapper.find('.action-btn').exists()).toBe(true)
    expect(wrapper.find('.action-btn').text()).toBe('Create Item')
  })
})

