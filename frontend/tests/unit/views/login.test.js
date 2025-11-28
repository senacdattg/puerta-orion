import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import login from '@/views/login.vue'

// Mock the Login component
vi.mock('@/components/ui/login.vue', () => ({
  default: {
    name: 'Login',
    template: '<div class="login-component">Login Component</div>'
  }
}))

describe('LoginView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should render the view', () => {
    const wrapper = mount(login)

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('main').exists()).toBe(true)
  })

  it('should render Login component', () => {
    const wrapper = mount(login)

    expect(wrapper.find('.login-component').exists()).toBe(true)
  })

  it('should have correct component name', () => {
    expect(login.name || login.__name).toBe('LoginView')
  })
})

