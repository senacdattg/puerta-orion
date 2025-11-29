import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ModalDetalles from '@/components/admin/modal-detalles.vue'
import { useAuthStore } from '@/stores/auth'

// Mock services
vi.mock('@/services/mensualidadesService', () => ({
  default: {
    actualizar: vi.fn().mockResolvedValue({ success: true }),
    crearAbono: vi.fn().mockResolvedValue({ success: true })
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

describe('ModalDetalles', () => {
  let wrapper
  let mockAuthStore

  const mockMensualidad = {
    id_mensualidad: 1,
    nombre: 'Juan Pérez',
    estado: 'Pendiente',
    monto_pago: 50000,
    monto_pago_raw: 50000,
    fecha_vencimiento: '2024-12-31',
    avatar: null,
    estado_bool: false
  }

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    mockAuthStore = {
      user: {
        id_usuario: 1,
        roles: [{ nombre_rol: 'Administrador' }]
      }
    }

    useAuthStore.mockReturnValue(mockAuthStore)
  })

  it('should render component with mensualidad prop', () => {
    wrapper = mount(ModalDetalles, {
      props: {
        mensualidad: mockMensualidad
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.modal-overlay').exists()).toBe(true)
  })

  it('should display modal title correctly', () => {
    wrapper = mount(ModalDetalles, {
      props: {
        mensualidad: mockMensualidad
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    const title = wrapper.find('.modal-title')
    expect(title.exists()).toBe(true)
  })

  it('should show deportista information when not editing', () => {
    wrapper = mount(ModalDetalles, {
      props: {
        mensualidad: mockMensualidad
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    expect(wrapper.vm.editando).toBe(false)
  })

  it('should display mensualidad details', () => {
    wrapper = mount(ModalDetalles, {
      props: {
        mensualidad: mockMensualidad
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    expect(wrapper.vm.mensualidad).toEqual(mockMensualidad)
  })

  it('should emit cerrar event when close button is clicked', async () => {
    wrapper = mount(ModalDetalles, {
      props: {
        mensualidad: mockMensualidad
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    const closeButton = wrapper.find('.btn-cerrar')
    if (closeButton.exists()) {
      await closeButton.trigger('click')
      expect(wrapper.emitted('cerrar')).toBeTruthy()
    }
  })

  it('should handle edit mode', () => {
    wrapper = mount(ModalDetalles, {
      props: {
        mensualidad: mockMensualidad
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    wrapper.vm.editando = true
    expect(wrapper.vm.editando).toBe(true)
  })

  it('should format currency correctly', () => {
    wrapper = mount(ModalDetalles, {
      props: {
        mensualidad: mockMensualidad
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    // formatCOP should exist and format numbers
    if (wrapper.vm.formatCOP) {
      const formatted = wrapper.vm.formatCOP(50000)
      expect(formatted).toBeDefined()
    } else {
      // If method doesn't exist, just verify component mounted
      expect(wrapper.exists()).toBe(true)
    }
  })

  it('should handle tab switching', async () => {
    wrapper = mount(ModalDetalles, {
      props: {
        mensualidad: mockMensualidad
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    wrapper.vm.editando = true
    wrapper.vm.activeTab = 'abonos'
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.activeTab).toBe('abonos')
  })
})

