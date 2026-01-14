/**
 * IconButton 组件单元测试
 */
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import IconButton from '../IconButton.vue'
import ElementPlus from 'element-plus'

describe('IconButton', () => {
  const globalConfig = {
    plugins: [ElementPlus],
    stubs: {
      'el-icon': {
        template: '<span class="el-icon"><slot /></span>',
      },
    },
  }

  it('应该渲染按钮', () => {
    const wrapper = mount(IconButton, {
      props: { icon: 'Edit' },
      global: globalConfig,
    })

    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('应该触发点击事件', async () => {
    const wrapper = mount(IconButton, {
      props: { icon: 'Edit' },
      global: globalConfig,
    })

    await wrapper.find('button').trigger('click')

    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('禁用时不应该触发点击事件', async () => {
    const wrapper = mount(IconButton, {
      props: { icon: 'Edit', disabled: true },
      global: globalConfig,
    })

    await wrapper.find('button').trigger('click')

    expect(wrapper.emitted('click')).toBeFalsy()
  })

  it('应该显示正确的 title', () => {
    const wrapper = mount(IconButton, {
      props: { icon: 'Edit', title: 'Edit Item' },
      global: globalConfig,
    })

    expect(wrapper.find('button').attributes('title')).toBe('Edit Item')
  })

  it('应该应用不同的变体样式', () => {
    const wrapper = mount(IconButton, {
      props: { icon: 'Delete', variant: 'danger' },
      global: globalConfig,
    })

    expect(wrapper.find('button').classes().join(' ')).toContain('hover:text-red-600')
  })

  it('应该应用不同的尺寸', () => {
    const wrapperSm = mount(IconButton, {
      props: { icon: 'Edit', size: 'sm' },
      global: globalConfig,
    })

    const wrapperLg = mount(IconButton, {
      props: { icon: 'Edit', size: 'lg' },
      global: globalConfig,
    })

    expect(wrapperSm.find('button').classes()).toContain('p-1.5')
    expect(wrapperLg.find('button').classes()).toContain('p-2.5')
  })

  it('loading 状态时应该显示加载图标', () => {
    const wrapper = mount(IconButton, {
      props: { icon: 'Edit', loading: true },
      global: globalConfig,
    })

    expect(wrapper.find('.animate-spin').exists()).toBe(true)
  })

  it('loading 状态时不应该触发点击事件', async () => {
    const wrapper = mount(IconButton, {
      props: { icon: 'Edit', loading: true },
      global: globalConfig,
    })

    await wrapper.find('button').trigger('click')

    expect(wrapper.emitted('click')).toBeFalsy()
  })
})

