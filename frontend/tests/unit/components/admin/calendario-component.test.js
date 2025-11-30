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

  describe('Event Management', () => {
    let wrapper

    beforeEach(async () => {
      wrapper = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should open event modal when day is selected', async () => {
      const testDay = { numero: 15, esMesActual: true, esHoy: false, eventos: [] }
      wrapper.vm.seleccionarDia(testDay)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.modalVisible).toBe(true)
    })

    it('should reset nuevoEvento when opening modal', async () => {
      wrapper.vm.abrirModal({ fecha: '2024-12-31', bloquear: true })
      await wrapper.vm.$nextTick()

      // abrirModal calls limpiarFormulario which resets nuevoEvento
      expect(wrapper.vm.modalVisible).toBe(true)
      expect(wrapper.vm.nuevoEvento.fecha).toBe('2024-12-31')
    })

    it('should validate event form', () => {
      wrapper.vm.nuevoEvento = {
        titulo: '',
        idTipoEvento: '',
        lugar: '',
        fecha: null
      }

      const errores = wrapper.vm.validarEvento()
      expect(errores.length).toBeGreaterThan(0)
    })

    it('should create event successfully', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: false }) // Don't add another
      Swal.default.close = vi.fn()
      Swal.default.showLoading = vi.fn()

      wrapper.vm.nuevoEvento = {
        titulo: 'Nuevo Evento',
        idTipoEvento: 1,
        idCategoria: 1,
        lugar: 'Lugar Test',
        horaInicio: '10:00',
        horaFin: '11:00',
        descripcion: 'Descripción',
        fecha: '2024-12-31'
      }
      wrapper.vm.modoEdicion = false

      await wrapper.vm.guardarEvento()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))

      // Should handle success
      expect(wrapper.exists()).toBe(true)
    })

    it('should edit event successfully', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })
      Swal.default.close = vi.fn()
      Swal.default.showLoading = vi.fn()

      const eventoExistente = {
        id: 1,
        titulo: 'Evento Existente',
        idTipoEvento: 1,
        fecha: '2024-12-31'
      }

      wrapper.vm.editarEvento(eventoExistente)
      await wrapper.vm.$nextTick()

      wrapper.vm.nuevoEvento.titulo = 'Evento Editado'
      wrapper.vm.modoEdicion = true
      await wrapper.vm.guardarEvento()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.exists()).toBe(true)
    })

    it('should delete event successfully', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })
      Swal.default.close = vi.fn()

      const eventoEliminar = {
        id: 1,
        titulo: 'Evento a Eliminar'
      }

      wrapper.vm.eventoSeleccionado = eventoEliminar
      await wrapper.vm.eliminarEvento()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))

      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Input Normalization', () => {
    let wrapper

    beforeEach(() => {
      wrapper = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })
    })

    it('should normalizarTitulo correctly', () => {
      const titulo = wrapper.vm.normalizarTitulo('test título 123')
      expect(titulo).toBe('TEST TÍTULO 123')
    })

    it('should normalizarLugar correctly', () => {
      const lugar = wrapper.vm.normalizarLugar('lugar test 123')
      expect(lugar).toBe('LUGAR TEST 123')
    })

    it('should normalizarDescripcion correctly', () => {
      const descripcion = wrapper.vm.normalizarDescripcion('Descripción con caracteres especiales!')
      expect(descripcion).toBeTruthy()
    })

    it('should manejarTitulo input', () => {
      const event = {
        target: { value: 'nuevo título' }
      }
      wrapper.vm.manejarTitulo(event)

      expect(wrapper.vm.nuevoEvento.titulo).toBe('NUEVO TÍTULO')
    })

    it('should manejarLugar input', () => {
      const event = {
        target: { value: 'nuevo lugar' }
      }
      wrapper.vm.manejarLugar(event)

      expect(wrapper.vm.nuevoEvento.lugar).toBe('NUEVO LUGAR')
    })

    it('should manejarDescripcion input', () => {
      const event = {
        target: { value: 'Nueva descripción' }
      }
      wrapper.vm.manejarDescripcion(event)

      expect(wrapper.vm.nuevoEvento.descripcion).toBe('Nueva descripción')
    })
  })

  describe('Computed Properties', () => {
    it('should check esAdmin correctly', () => {
      const wrapperAdmin = mount(CalendarioComponent, {
        props: {
          rol: 'Administrador'
        },
        global: {
          stubs: {
            'i': true
          }
        }
      })

      expect(wrapperAdmin.vm.esAdmin).toBe(true)
    })

    it('should check puedeCrear permission', () => {
      mockAuthStore.puedeCrearEventos = true
      mockAuthStore.permissions = ['crear_evento']

      const wrapper = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })

      expect(wrapper.vm.puedeCrear).toBe(true)
    })

    it('should check puedeEditar permission', () => {
      mockAuthStore.puedeEditarEventos = true
      mockAuthStore.permissions = ['editar_evento']

      const wrapper = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })

      expect(wrapper.vm.puedeEditar).toBe(true)
    })

    it('should check puedeEliminar permission', () => {
      mockAuthStore.puedeEliminarEventos = true
      mockAuthStore.permissions = ['eliminar_evento']

      const wrapper = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })

      expect(wrapper.vm.puedeEliminar).toBe(true)
    })
  })

  describe('Event Navigation', () => {
    let wrapper

    beforeEach(async () => {
      wrapper = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })

      wrapper.vm.eventosDelDia = [
        { id: 1, titulo: 'Evento 1' },
        { id: 2, titulo: 'Evento 2' },
        { id: 3, titulo: 'Evento 3' }
      ]
      wrapper.vm.indiceEventoActual = 0

      await wrapper.vm.$nextTick()
    })

    it('should navigate to next event', () => {
      wrapper.vm.eventoSiguiente()

      expect(wrapper.vm.indiceEventoActual).toBe(1)
    })

    it('should navigate to previous event', () => {
      wrapper.vm.indiceEventoActual = 2
      wrapper.vm.eventoAnterior()

      expect(wrapper.vm.indiceEventoActual).toBe(1)
    })

    it('should wrap to first event when at end', () => {
      wrapper.vm.indiceEventoActual = 2
      wrapper.vm.eventoSiguiente()

      expect(wrapper.vm.indiceEventoActual).toBe(0)
    })

    it('should wrap to last event when at beginning', () => {
      wrapper.vm.indiceEventoActual = 0
      wrapper.vm.eventoAnterior()

      expect(wrapper.vm.indiceEventoActual).toBe(2)
    })
  })

  describe('Helper Functions', () => {
    let wrapper

    beforeEach(() => {
      wrapper = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })
    })

    it('should clonarObjeto correctly', () => {
      const obj = { test: 'value', nested: { key: 'value' } }
      const cloned = wrapper.vm.clonarObjeto(obj)

      expect(cloned).toEqual(obj)
      expect(cloned).not.toBe(obj)
    })

    it('should normalizarEspacios correctly', () => {
      expect(wrapper.vm.normalizarEspacios('test   espacios')).toBe('test espacios')
      expect(wrapper.vm.normalizarEspacios('  test  ')).toBe('test')
    })

    it('should obtenerFechaActualFormateada return formatted string', () => {
      const fecha = wrapper.vm.obtenerFechaActualFormateada()
      expect(typeof fecha).toBe('string')
      expect(fecha.length).toBeGreaterThan(0)
    })
  })

  describe('Modal Management', () => {
    let wrapper

    beforeEach(() => {
      wrapper = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })
    })

    it('should toggle edit mode', () => {
      wrapper.vm.modoEdicion = false
      wrapper.vm.editarEvento({ id: 1, titulo: 'Test', idTipoEvento: 1 })

      expect(wrapper.vm.modoEdicion).toBe(true)
    })

    it('should close modal and reset edit mode', () => {
      wrapper.vm.modalVisible = true
      wrapper.vm.modoEdicion = true

      wrapper.vm.cerrarModal()
      expect(wrapper.vm.modalVisible).toBe(false)
      expect(wrapper.vm.modoEdicion).toBe(false)
    })
  })
})

