import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import SelectorRoles from '@/components/layout/selector-roles.vue'
import { useAuthStore } from '@/stores/auth'

// Mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } }
  ]
})

// Mock auth store
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

describe('SelectorRoles Component', () => {
  let mockAuthStore

  beforeEach(async () => {
    setActivePinia(createPinia())

    mockAuthStore = {
      user: {
        roles: ['Administrador', 'Entrenador']
      },
      rolesSelector: {
        Administrador: true,
        Entrenador: true
      },
      activeRole: 'Administrador',
      setActiveRole: vi.fn().mockResolvedValue({ success: true }),
      userDetail: null
    }

    useAuthStore.mockReturnValue(mockAuthStore)

    await router.push('/')
  })

  const createWrapper = () => {
    return mount(SelectorRoles, {
      global: {
        plugins: [router]
      }
    })
  }

  it('should render when roles are available', () => {
    const wrapper = createWrapper()

    expect(wrapper.find('.selector-roles').exists()).toBe(true)
  })

  it('should not render when no roles available', () => {
    mockAuthStore.rolesSelector = {}
    mockAuthStore.user.roles = []

    const wrapper = createWrapper()

    expect(wrapper.find('.selector-roles').exists()).toBe(false)
  })

  it('should render select element with roles', () => {
    const wrapper = createWrapper()

    const select = wrapper.find('select')

    expect(select.exists()).toBe(true)
    expect(select.element.options.length).toBeGreaterThan(0)
  })

  it('should call setActiveRole when select changes', async () => {
    const wrapper = createWrapper()

    const select = wrapper.find('select')
    await select.setValue('Entrenador')
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // The component calls setActiveRole asynchronously
    expect(mockAuthStore.setActiveRole).toHaveBeenCalled()
  })

  it('should display current active role', () => {
    mockAuthStore.activeRole = 'Entrenador'

    const wrapper = createWrapper()

    const select = wrapper.find('select')

    expect(select.element.value).toBe('Entrenador')
  })
})

