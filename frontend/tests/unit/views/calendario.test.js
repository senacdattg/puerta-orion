import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import CalendarioView from '@/views/calendario.vue'
import { useAuthStore } from '@/stores/auth'

// Mock components
vi.mock('@/components/layout/encabezado.vue', () => ({
  default: {
    name: 'Encabezado',
    template: '<header class="encabezado">Header</header>'
  }
}))

vi.mock('@/components/layout/pie.vue', () => ({
  default: {
    name: 'Pie',
    template: '<footer class="pie">Footer</footer>'
  }
}))

vi.mock('@/components/admin/calendario-component.vue', () => ({
  default: {
    name: 'CalendarioComponent',
    template: '<div class="calendario-component">Calendar</div>',
    props: ['rol']
  }
}))

// Mock stores
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

describe('CalendarioView', () => {
  let mockAuthStore

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    mockAuthStore = {
      user: {
        id_usuario: 1,
        roles: [{ nombre_rol: 'Deportista' }]
      }
    }

    useAuthStore.mockReturnValue(mockAuthStore)
  })

  it('should render component', () => {
    const wrapper = mount(CalendarioView, {
      global: {
        stubs: {
          Encabezado: true,
          Pie: true,
          CalendarioComponent: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('main').exists()).toBe(true)
  })

  it('should compute rolUsuario correctly for Deportista', () => {
    const wrapper = mount(CalendarioView, {
      global: {
        stubs: {
          Encabezado: true,
          Pie: true,
          CalendarioComponent: true
        }
      }
    })

    expect(wrapper.vm.rolUsuario).toBe('Deportista')
  })

  it('should compute rolUsuario correctly for SuperAdmin', () => {
    mockAuthStore.user.roles = [{ nombre_rol: 'SuperAdmin' }]

    const wrapper = mount(CalendarioView, {
      global: {
        stubs: {
          Encabezado: true,
          Pie: true,
          CalendarioComponent: true
        }
      }
    })

    expect(wrapper.vm.rolUsuario).toBe('SuperAdmin')
  })

  it('should compute rolUsuario correctly for Administrador', () => {
    mockAuthStore.user.roles = [{ nombre_rol: 'Administrador' }]

    const wrapper = mount(CalendarioView, {
      global: {
        stubs: {
          Encabezado: true,
          Pie: true,
          CalendarioComponent: true
        }
      }
    })

    expect(wrapper.vm.rolUsuario).toBe('Administrador')
  })

  it('should default to Usuario when no roles', () => {
    mockAuthStore.user.roles = []

    const wrapper = mount(CalendarioView, {
      global: {
        stubs: {
          Encabezado: true,
          Pie: true,
          CalendarioComponent: true
        }
      }
    })

    expect(wrapper.vm.rolUsuario).toBe('Usuario')
  })

  it('should default to Usuario when user is null', () => {
    mockAuthStore.user = null

    const wrapper = mount(CalendarioView, {
      global: {
        stubs: {
          Encabezado: true,
          Pie: true,
          CalendarioComponent: true
        }
      }
    })

    expect(wrapper.vm.rolUsuario).toBe('Usuario')
  })

  it('should pass rol prop to CalendarioComponent', () => {
    mockAuthStore.user.roles = [{ nombre_rol: 'Entrenador' }]

    const wrapper = mount(CalendarioView, {
      global: {
        stubs: {
          Encabezado: true,
          Pie: true
        }
      }
    })

    const calendarioComponent = wrapper.findComponent({ name: 'CalendarioComponent' })
    expect(calendarioComponent.exists()).toBe(true)
    expect(calendarioComponent.props('rol')).toBe('Entrenador')
  })
})


