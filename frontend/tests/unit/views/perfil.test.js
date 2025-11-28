import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import perfil from '@/views/perfil.vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

// Mock components
vi.mock('@/components/layout/encabezado.vue', () => ({
  default: {
    name: 'Encabezado',
    template: '<header class="encabezado">Header</header>'
  }
}))

// Mock stores
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

// Mock router
vi.mock('vue-router', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn()
  }))
}))

// Mock services
vi.mock('@/services/usuariosService', () => ({
  default: {
    obtenerUsuarioPorId: vi.fn()
  }
}))

describe('PerfilView', () => {
  let mockAuthStore
  let mockRouter

  beforeEach(() => {
    setActivePinia(createPinia())

    mockAuthStore = {
      user: {
        id_usuario: 1,
        usuario: 'testuser',
        estado: true,
        persona: {
          nombre_completo: 'Test User',
          correo_electronico: 'test@example.com'
        },
        roles: ['Administrador']
      }
    }

    mockRouter = {
      push: vi.fn()
    }

    useAuthStore.mockReturnValue(mockAuthStore)
    useRouter.mockReturnValue(mockRouter)
  })

  it('should render the view', () => {
    const wrapper = mount(perfil, {
      global: {
        stubs: {
          Encabezado: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.perfil-page').exists()).toBe(true)
  })

  it('should render perfil container', () => {
    const wrapper = mount(perfil, {
      global: {
        stubs: {
          Encabezado: true
        }
      }
    })

    expect(wrapper.find('.perfil-container').exists()).toBe(true)
  })

  it('should render perfil header', () => {
    const wrapper = mount(perfil, {
      global: {
        stubs: {
          Encabezado: true
        }
      }
    })

    expect(wrapper.find('.perfil-header').exists()).toBe(true)
    expect(wrapper.find('.perfil-title').exists()).toBe(true)
  })

  it('should show loading state when isLoading is true', async () => {
    const wrapper = mount(perfil, {
      global: {
        stubs: {
          Encabezado: true
        }
      }
    })

    await wrapper.setData({ isLoading: true })

    expect(wrapper.find('.skeleton').exists()).toBe(true)
  })

  it('should show empty state when usuario is null', async () => {
    mockAuthStore.user = null

    const wrapper = mount(perfil, {
      global: {
        stubs: {
          Encabezado: true
        }
      }
    })

    await wrapper.setData({ isLoading: false, usuario: null })

    expect(wrapper.find('.empty-state').exists()).toBe(true)
  })
})

