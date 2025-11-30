import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import RegistrarAcudiente from '@/views/registrar-acudiente.vue'

const mockRouter = {
  replace: vi.fn()
}

const mockUseAuthStore = vi.fn()
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockUseAuthStore()
}))

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter
  }
})

describe('RegistrarAcudiente', () => {
  let wrapper
  let router
  let mockAuthStore

  beforeEach(() => {
    vi.clearAllMocks()
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } }
      ]
    })

    mockAuthStore = {
      token: null
    }

    mockUseAuthStore.mockReturnValue(mockAuthStore)
  })

  const createWrapper = () => {
    return mount(RegistrarAcudiente, {
      global: {
        plugins: [router]
      }
    })
  }

  describe('Renderizado básico', () => {
    it('should render component', () => {
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('main').exists()).toBe(true)
    })

    it('should display redirecting message', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Redirigiendo...')
    })
  })

  describe('Redirección', () => {
    it('should redirect to formulario-acudiente-completo when user has token', async () => {
      mockAuthStore.token = 'test-token'
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      expect(mockRouter.replace).toHaveBeenCalledWith('/formulario-acudiente-completo')
    })

    it('should not redirect when user has no token', async () => {
      mockAuthStore.token = null
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      expect(mockRouter.replace).not.toHaveBeenCalled()
    })
  })
})

