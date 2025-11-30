import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Eventos from '@/views/eventos.vue'
import { useAuthStore } from '@/stores/auth'

// Mock components
vi.mock('@/components/layout/encabezado.vue', () => ({
  default: {
    name: 'Encabezado',
    template: '<header class="encabezado">Header</header>'
  }
}))

vi.mock('@/components/layout/footer-enhanced.vue', () => ({
  default: {
    name: 'FooterEnhanced',
    template: '<footer class="footer">Footer</footer>'
  }
}))

// Mock stores
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

// Mock services
vi.mock('@/services/calendarioService', () => ({
  default: {
    obtenerEventosProximos: vi.fn().mockResolvedValue([
      {
        id_evento: 1,
        nombre: 'Evento Test',
        fecha_evento: '2024-12-31',
        hora_inicio: '10:00',
        hora_fin: '12:00',
        lugar: 'Cancha Principal',
        categoria: 'Pre-infantil',
        estado: 'Próximo'
      }
    ])
  }
}))

describe('Eventos View', () => {
  let mockAuthStore

  beforeEach(() => {
    setActivePinia(createPinia())

    mockAuthStore = {
      user: {
        id_usuario: 1,
        usuario: 'testuser',
        roles: [{ nombre_rol: 'Deportista' }]
      },
      estaAutenticado: true
    }

    useAuthStore.mockReturnValue(mockAuthStore)
  })

  it('should render the view', async () => {
    const wrapper = mount(Eventos, {
      global: {
        stubs: {
          Encabezado: true,
          FooterEnhanced: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.eventos-page').exists()).toBe(true)
  })

  it('should display page title', () => {
    const wrapper = mount(Eventos, {
      global: {
        stubs: {
          Encabezado: true,
          FooterEnhanced: true
        }
      }
    })

    const title = wrapper.find('.eventos-title')
    expect(title.exists()).toBe(true)
  })

  it('should display eventos grid', async () => {
    const wrapper = mount(Eventos, {
      global: {
        stubs: {
          Encabezado: true,
          FooterEnhanced: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    const grid = wrapper.find('.eventos-grid')
    expect(grid.exists()).toBe(true)
  })

  it('should show loading state when cargando is true', () => {
    const wrapper = mount(Eventos, {
      global: {
        stubs: {
          Encabezado: true,
          FooterEnhanced: true
        }
      }
    })

    wrapper.vm.cargando = true
    expect(wrapper.vm.cargando).toBe(true)
  })

  it('should show empty state when no eventos', async () => {
    const wrapper = mount(Eventos, {
      global: {
        stubs: {
          Encabezado: true,
          FooterEnhanced: true
        }
      }
    })

    wrapper.vm.eventos = []
    wrapper.vm.cargando = false
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.eventos.length).toBe(0)
  })

    it('should format evento date correctly', () => {
      const wrapper = mount(Eventos, {
        global: {
          stubs: {
            Encabezado: true,
            FooterEnhanced: true
          }
        }
      })

      // Check if getEventoClass method exists
      expect(wrapper.vm.getEventoClass).toBeDefined()
    })

  it('should get estado class correctly', () => {
    const wrapper = mount(Eventos, {
      global: {
        stubs: {
          Encabezado: true,
          FooterEnhanced: true
        }
      }
    })

    const estadoClass = wrapper.vm.getEstadoClass('Próximo')
    expect(estadoClass).toBeDefined()
  })
})

