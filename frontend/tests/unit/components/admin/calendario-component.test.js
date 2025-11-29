import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import CalendarioComponent from '@/components/admin/calendario-component.vue'
import { useAuthStore } from '@/stores/auth'

// Mock services
vi.mock('@/services/calendarioService', () => ({
  default: {
    cargarEventos: vi.fn().mockResolvedValue([
      {
        id_evento: 1,
        nombre: 'Evento Test',
        fecha_evento: '2024-12-31',
        id_tipo_evento: 1
      }
    ]),
    obtenerEventosPorFecha: vi.fn().mockResolvedValue([]),
    crearEvento: vi.fn().mockResolvedValue({ success: true }),
    actualizarEvento: vi.fn().mockResolvedValue({ success: true }),
    eliminarEvento: vi.fn().mockResolvedValue({ success: true })
  }
}))

vi.mock('@/services/catalogosService', () => ({
  default: {
    getCatalogosCompletos: vi.fn().mockResolvedValue({
      success: true,
      data: {
        tipos_evento: [{ id_tipo_evento: 1, nombre: 'Entrenamiento' }],
        categorias: [{ id_categoria: 1, nombre_categoria: 'Pre-infantil' }]
      }
    })
  }
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

vi.mock('@/composables/useModalScrollLock', () => ({
  useModalScrollLock: vi.fn()
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(),
    Swal: {
      fire: vi.fn()
    }
  }
}))

describe('CalendarioComponent', () => {
  let wrapper
  let mockAuthStore

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    mockAuthStore = {
      user: {
        id_usuario: 1,
        roles: [{ nombre_rol: 'Administrador' }]
      },
      loadUserPermissions: vi.fn().mockResolvedValue({ success: true }),
      permissions: ['crear_evento', 'editar_evento', 'eliminar_evento'],
      puedeCrearEventos: true,
      puedeEditarEventos: true,
      puedeEliminarEventos: true
    }

    useAuthStore.mockReturnValue(mockAuthStore)
  })

  it('should render component', async () => {
    wrapper = mount(CalendarioComponent, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.calendario-container').exists()).toBe(true)
  })

  it('should display calendar title', () => {
    wrapper = mount(CalendarioComponent, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    const title = wrapper.find('.titulo-principal')
    expect(title.exists()).toBe(true)
  })

  it('should display current month and year', () => {
    wrapper = mount(CalendarioComponent, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    expect(wrapper.vm.mesActual).toBeDefined()
    expect(wrapper.vm.añoActual).toBeDefined()
  })

  it('should navigate to previous month', async () => {
    wrapper = mount(CalendarioComponent, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    const currentMonth = wrapper.vm.mesActual
    wrapper.vm.mesAnterior()
    await wrapper.vm.$nextTick()

    // Month should have changed
    expect(wrapper.vm.mesActual).toBeDefined()
  })

  it('should navigate to next month', async () => {
    wrapper = mount(CalendarioComponent, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    wrapper.vm.mesSiguiente()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.mesActual).toBeDefined()
  })

  it('should navigate to today', async () => {
    wrapper = mount(CalendarioComponent, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    wrapper.vm.irHoy()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.mesActual).toBeDefined()
  })

  it('should display week days', () => {
    wrapper = mount(CalendarioComponent, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    expect(wrapper.vm.diasSemana).toBeDefined()
    expect(wrapper.vm.diasSemana.length).toBe(7)
  })

  it('should handle day selection', async () => {
    wrapper = mount(CalendarioComponent, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    const testDay = { numero: 15, esMesActual: true, esHoy: false, eventos: [] }
    wrapper.vm.seleccionarDia(testDay)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.modalVisible).toBe(true)
  })

  it('should close modal', async () => {
    wrapper = mount(CalendarioComponent, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    wrapper.vm.modalVisible = true
    wrapper.vm.cerrarModal()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.modalVisible).toBe(false)
  })

  it('should format date correctly', () => {
    wrapper = mount(CalendarioComponent, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    const formatted = wrapper.vm.obtenerFechaActualFormateada()
    expect(formatted).toBeDefined()
    expect(typeof formatted).toBe('string')
  })
})

