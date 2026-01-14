/**
 * StatusBadge 组件单元测试
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatusBadge from '../StatusBadge.vue'

describe('StatusBadge', () => {
  it('应该渲染正确的状态文本', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'completed' },
    })

    expect(wrapper.text()).toContain('Rendered')
  })

  it('应该应用正确的样式类', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'completed' },
    })

    expect(wrapper.classes()).toContain('text-emerald-600')
    expect(wrapper.classes()).toContain('bg-emerald-50')
  })

  it('应该显示 processing 状态', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'processing' },
    })

    expect(wrapper.text()).toContain('Processing')
    expect(wrapper.classes()).toContain('text-orange-600')
  })

  it('应该显示 failed 状态', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'failed' },
    })

    expect(wrapper.text()).toContain('Failed')
    expect(wrapper.classes()).toContain('text-red-600')
  })

  it('应该显示 pending 状态', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'pending' },
    })

    expect(wrapper.text()).toContain('Pending')
    expect(wrapper.classes()).toContain('text-slate-500')
  })

  it('应该显示 draft 状态', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'draft' },
    })

    expect(wrapper.text()).toContain('Draft')
    expect(wrapper.classes()).toContain('text-yellow-700')
  })

  it('showDot 为 true 时应该显示状态点', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'completed', showDot: true },
    })

    expect(wrapper.find('.status-dot').exists()).toBe(true)
  })

  it('showDot 为 false 时不应该显示状态点', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'completed', showDot: false },
    })

    expect(wrapper.find('.status-dot').exists()).toBe(false)
  })

  it('应该支持自定义文本', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'completed', text: 'Custom Text' },
    })

    expect(wrapper.text()).toContain('Custom Text')
  })

  it('processing 状态应该有动画效果', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'processing', showDot: true },
    })

    const dot = wrapper.find('.status-dot')
    expect(dot.classes()).toContain('animate-pulse')
  })
})

