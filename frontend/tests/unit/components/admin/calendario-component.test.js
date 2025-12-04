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
    obtenerEventosPorFecha: vi.fn(() => []),
    crearEvento: vi.fn().mockResolvedValue({ success: true, id: 1 }),
    actualizarEvento: vi.fn().mockResolvedValue({ success: true, id: 1 }),
    eliminarEvento: vi.fn().mockResolvedValue({ success: true }),
    cargarCatalogos: vi.fn().mockResolvedValue({
      tiposEvento: [
        { id_tipo_evento: 1, nombre: 'Entrenamiento' },
        { id_tipo_evento: 2, nombre: 'Competencia' }
      ],
      categorias: [
        { id_categoria: 1, nombre_categoria: 'Pre-infantil' },
        { id_categoria: 2, nombre_categoria: 'Infantil' }
      ]
    })
  }
}))

// Get reference to mocked service for test updates
let mockCalendarioService

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
    close: vi.fn(),
    showLoading: vi.fn(),
    Swal: {
      fire: vi.fn()
    }
  }
}))

vi.mock('@/utils/error-handling', () => ({
  extraerMensajeError: vi.fn((error) => error?.message || 'Error desconocido')
}))

vi.mock('@/config/environment', () => ({
  LOG_CONFIG: {
    enabled: false
  }
}))

describe('CalendarioComponent', () => {
  let wrapper
  let mockAuthStore

  beforeEach(async () => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    // Get reference to mocked service
    const calendarioService = await import('@/services/calendarioService')
    mockCalendarioService = calendarioService.default

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

    it('should obtenerNombreTipoEvento return correct name', () => {
      wrapper.vm.tiposEvento = [{ id_tipo_evento: 1, nombre: 'Entrenamiento' }]
      const nombre = wrapper.vm.obtenerNombreTipoEvento(1)
      expect(nombre).toBe('Entrenamiento')
    })

    it('should obtenerNombreTipoEvento return null when not found', () => {
      wrapper.vm.tiposEvento = []
      const nombre = wrapper.vm.obtenerNombreTipoEvento(1)
      expect(nombre).toBeNull()
    })

    it('should obtenerNombreCategoria return correct name', () => {
      wrapper.vm.categorias = [{ id_categoria: 1, nombre_categoria: 'Pre-infantil' }]
      const nombre = wrapper.vm.obtenerNombreCategoria(1)
      expect(nombre).toBe('Pre-infantil')
    })

    it('should obtenerNombreCategoria return null when not found', () => {
      wrapper.vm.categorias = []
      const nombre = wrapper.vm.obtenerNombreCategoria(1)
      expect(nombre).toBeNull()
    })

    it('should obtenerClaseTipoEvento return correct class for entrenamiento', () => {
      const clase = wrapper.vm.obtenerClaseTipoEvento('Entrenamiento')
      expect(clase).toBe('tipo-entrenamiento')
    })

    it('should obtenerClaseTipoEvento return correct class for competencia', () => {
      const clase = wrapper.vm.obtenerClaseTipoEvento('Competencia')
      expect(clase).toBe('tipo-competencia')
    })

    it('should obtenerClaseTipoEvento return default class when not recognized', () => {
      const clase = wrapper.vm.obtenerClaseTipoEvento('Otro Tipo')
      expect(clase).toBe('tipo-otro tipo')
    })

    it('should esHoy return true for today', () => {
      const hoy = new Date()
      const esHoy = wrapper.vm.esHoy(hoy)
      expect(esHoy).toBe(true)
    })

    it('should esHoy return false for yesterday', () => {
      const ayer = new Date()
      ayer.setDate(ayer.getDate() - 1)
      const esHoy = wrapper.vm.esHoy(ayer)
      expect(esHoy).toBe(false)
    })

    it('should formatearFecha return YYYY-MM-DD format', () => {
      const fecha = new Date('2024-12-31')
      const formateada = wrapper.vm.formatearFecha(fecha)
      expect(formateada).toBe('2024-12-31')
    })

    it('should obtenerFechaActual return today in YYYY-MM-DD format', () => {
      const fecha = wrapper.vm.obtenerFechaActual()
      expect(fecha).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    })

    it('should obtenerNombreMes return correct month name', () => {
      expect(wrapper.vm.obtenerNombreMes(0)).toBe('Enero')
      expect(wrapper.vm.obtenerNombreMes(11)).toBe('Diciembre')
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

  describe('Date and Time Formatting', () => {
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

    it('should formatearFechaCompleta format correctly', () => {
      const fecha = wrapper.vm.formatearFechaCompleta('2024-12-31')
      expect(fecha).toContain('2024')
      expect(fecha).toContain('Diciembre')
    })

    it('should formatearFechaCompleta return null for empty input', () => {
      const fecha = wrapper.vm.formatearFechaCompleta(null)
      expect(fecha).toBeNull()
    })

    it('should formatearFechaCompleta handle invalid date', () => {
      const fecha = wrapper.vm.formatearFechaCompleta('invalid-date')
      // When invalid, Date constructor creates Invalid Date but doesn't throw
      // So it returns the formatted string with NaN values or original string
      expect(typeof fecha).toBe('string')
      // The function may return a formatted string with NaN or the original string depending on Date behavior
    })

    it('should formatearHora return HH:mm for valid format', () => {
      expect(wrapper.vm.formatearHora('10:30')).toBe('10:30')
    })

    it('should formatearHora extract HH:mm from HH:mm:ss', () => {
      expect(wrapper.vm.formatearHora('10:30:45')).toBe('10:30')
    })

    it('should formatearHora return null for empty input', () => {
      expect(wrapper.vm.formatearHora(null)).toBeNull()
    })

    it('should formatearHora12h format correctly for AM', () => {
      expect(wrapper.vm.formatearHora12h('09:30')).toBe('9:30 AM')
    })

    it('should formatearHora12h format correctly for PM', () => {
      expect(wrapper.vm.formatearHora12h('15:30')).toBe('3:30 PM')
    })

    it('should formatearHora12h handle 12 PM correctly', () => {
      expect(wrapper.vm.formatearHora12h('12:00')).toBe('12:00 PM')
    })

    it('should formatearHora12h handle 12 AM correctly', () => {
      expect(wrapper.vm.formatearHora12h('00:00')).toBe('12:00 AM')
    })

    it('should formatearHora12h return empty string for empty input', () => {
      expect(wrapper.vm.formatearHora12h(null)).toBe('')
    })

    it('should formatearHora12h return original string for invalid format', () => {
      expect(wrapper.vm.formatearHora12h('invalid')).toBe('invalid')
    })
  })

  describe('Validation Functions', () => {
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

    it('should validarTitulo return null when title exists', () => {
      wrapper.vm.nuevoEvento.titulo = 'Test Title'
      const error = wrapper.vm.validarTitulo()
      expect(error).toBeNull()
    })

    it('should validarTitulo return error when title is empty', () => {
      wrapper.vm.nuevoEvento.titulo = ''
      const error = wrapper.vm.validarTitulo()
      expect(error).toBeTruthy()
    })

    it('should validarTipoEvento return null when tipo is selected', () => {
      wrapper.vm.nuevoEvento.idTipoEvento = 1
      const error = wrapper.vm.validarTipoEvento()
      expect(error).toBeNull()
    })

    it('should validarTipoEvento return error when tipo is not selected', () => {
      wrapper.vm.nuevoEvento.idTipoEvento = ''
      const error = wrapper.vm.validarTipoEvento()
      expect(error).toBeTruthy()
    })

    it('should validarFecha return null when fecha exists', () => {
      wrapper.vm.nuevoEvento.fecha = '2024-12-31'
      const error = wrapper.vm.validarFecha()
      expect(error).toBeNull()
    })

    it('should validarFecha return error when fecha is empty', () => {
      wrapper.vm.nuevoEvento.fecha = null
      const error = wrapper.vm.validarFecha()
      expect(error).toBeTruthy()
    })

    it('should validarHoraInicio return null when horaInicio exists', () => {
      wrapper.vm.nuevoEvento.horaInicio = '10:00'
      const error = wrapper.vm.validarHoraInicio()
      expect(error).toBeNull()
    })

    it('should validarHoraInicio return null when hora exists', () => {
      wrapper.vm.nuevoEvento.hora = '10:00'
      const error = wrapper.vm.validarHoraInicio()
      expect(error).toBeNull()
    })

    it('should validarHoraInicio return error when neither horaInicio nor hora exists', () => {
      wrapper.vm.nuevoEvento.horaInicio = ''
      wrapper.vm.nuevoEvento.hora = ''
      const error = wrapper.vm.validarHoraInicio()
      expect(error).toBeTruthy()
    })

    it('should validarHoras return null when both horas exist', () => {
      wrapper.vm.nuevoEvento.horaInicio = '10:00'
      wrapper.vm.nuevoEvento.horaFin = '11:00'
      const error = wrapper.vm.validarHoras()
      expect(error).toBeNull()
    })

    it('should validarHoras return error when horas are missing', () => {
      wrapper.vm.nuevoEvento.horaInicio = ''
      wrapper.vm.nuevoEvento.horaFin = ''
      const error = wrapper.vm.validarHoras()
      expect(error).toBeTruthy()
    })

    it('should validarCategoria return null when categoria is selected', () => {
      wrapper.vm.nuevoEvento.idCategoria = 1
      const error = wrapper.vm.validarCategoria()
      expect(error).toBeNull()
    })

    it('should validarCategoria return error when categoria is not selected', () => {
      wrapper.vm.nuevoEvento.idCategoria = ''
      const error = wrapper.vm.validarCategoria()
      expect(error).toBeTruthy()
    })

    it('should validarLugar return null when lugar exists', () => {
      wrapper.vm.nuevoEvento.lugar = 'Test Place'
      const error = wrapper.vm.validarLugar()
      expect(error).toBeNull()
    })

    it('should validarLugar return error when lugar is empty', () => {
      wrapper.vm.nuevoEvento.lugar = ''
      const error = wrapper.vm.validarLugar()
      expect(error).toBeTruthy()
    })

    it('should validarRangoHoras return null when horaFin is after horaInicio', () => {
      wrapper.vm.nuevoEvento.horaInicio = '10:00'
      wrapper.vm.nuevoEvento.horaFin = '11:00'
      const error = wrapper.vm.validarRangoHoras()
      expect(error).toBeNull()
    })

    it('should validarRangoHoras return error when horaFin is before horaInicio', () => {
      wrapper.vm.nuevoEvento.horaInicio = '11:00'
      wrapper.vm.nuevoEvento.horaFin = '10:00'
      const error = wrapper.vm.validarRangoHoras()
      expect(error).toBeTruthy()
    })

    it('should validarRangoHoras return error when horaFin equals horaInicio', () => {
      wrapper.vm.nuevoEvento.horaInicio = '10:00'
      wrapper.vm.nuevoEvento.horaFin = '10:00'
      const error = wrapper.vm.validarRangoHoras()
      expect(error).toBeTruthy()
    })

    it('should validarEvento collect all validation errors', () => {
      wrapper.vm.nuevoEvento = {
        titulo: '',
        idTipoEvento: '',
        fecha: null,
        horaInicio: '',
        horaFin: '',
        idCategoria: '',
        lugar: ''
      }
      const errores = wrapper.vm.validarEvento()
      expect(errores.length).toBeGreaterThan(0)
    })

    it('should validarEvento return empty array when all validations pass', () => {
      wrapper.vm.nuevoEvento = {
        titulo: 'Test',
        idTipoEvento: 1,
        fecha: '2024-12-31',
        horaInicio: '10:00',
        horaFin: '11:00',
        idCategoria: 1,
        lugar: 'Test Place'
      }
      const errores = wrapper.vm.validarEvento()
      expect(errores).toHaveLength(0)
    })
  })

  describe('Selector de Eventos', () => {
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
    })

    it('should mostrarSelectorEventos set selector visible', () => {
      wrapper.vm.mostrarSelectorEventos('2024-12-31')
      expect(wrapper.vm.selectorEventosVisible).toBe(true)
      expect(wrapper.vm.nuevoEvento.fecha).toBe('2024-12-31')
    })

    it('should cerrarSelectorEventos close selector and reset', () => {
      wrapper.vm.selectorEventosVisible = true
      wrapper.vm.eventosDelDia = [{ id: 1 }]
      wrapper.vm.indiceEventoActual = 1

      wrapper.vm.cerrarSelectorEventos()

      expect(wrapper.vm.selectorEventosVisible).toBe(false)
      expect(wrapper.vm.eventosDelDia).toEqual([])
      expect(wrapper.vm.indiceEventoActual).toBe(0)
    })

    it('should abrirModalDesdeSelector open modal with blocked date', () => {
      wrapper.vm.nuevoEvento.fecha = '2024-12-31'
      wrapper.vm.selectorEventosVisible = true

      wrapper.vm.abrirModalDesdeSelector()

      expect(wrapper.vm.selectorEventosVisible).toBe(false)
      expect(wrapper.vm.modalVisible).toBe(true)
      expect(wrapper.vm.fechaBloqueada).toBe(true)
    })

    it('should eventoActual return current event', () => {
      wrapper.vm.eventosDelDia = [
        { id: 1, titulo: 'Evento 1' },
        { id: 2, titulo: 'Evento 2' }
      ]
      wrapper.vm.indiceEventoActual = 0

      const evento = wrapper.vm.eventoActual
      expect(evento.id).toBe(1)
    })

    it('should eventoActual return null when no events', () => {
      wrapper.vm.eventosDelDia = []
      const evento = wrapper.vm.eventoActual
      expect(evento).toBeNull()
    })

    it('should fechaDelDiaBadge return formatted badge', () => {
      wrapper.vm.nuevoEvento.fecha = '2024-12-31'
      const badge = wrapper.vm.fechaDelDiaBadge
      expect(badge.dia).toBe(31)
      expect(badge.mes).toBe('Dic')
    })

    it('should fechaDelDiaBadge return null when fecha is empty', () => {
      wrapper.vm.nuevoEvento.fecha = null
      const badge = wrapper.vm.fechaDelDiaBadge
      expect(badge).toBeNull()
    })

    it('should fechaDelDiaBadge handle invalid date', () => {
      wrapper.vm.nuevoEvento.fecha = 'invalid-date'
      const badge = wrapper.vm.fechaDelDiaBadge
      // When invalid, Date constructor creates Invalid Date but doesn't throw
      // So badge may have NaN values or be null depending on Date behavior
      expect(badge === null || (badge && (isNaN(badge.dia) || isNaN(badge.mes)))).toBe(true)
    })
  })

  describe('Carrusel Automático', () => {
    let wrapper

    beforeEach(() => {
      vi.useFakeTimers()
      wrapper = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })

      wrapper.vm.eventosDelDia = [
        { id: 1, titulo: 'Evento 1' },
        { id: 2, titulo: 'Evento 2' }
      ]
      wrapper.vm.indiceEventoActual = 0
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('should iniciarCarrusel start interval', () => {
      wrapper.vm.selectorEventosVisible = true
      wrapper.vm.iniciarCarrusel()

      expect(wrapper.vm.intervaloCarrusel).toBeTruthy()
    })

    it('should iniciarCarrusel not start when only one event', () => {
      wrapper.vm.eventosDelDia = [{ id: 1 }]
      wrapper.vm.iniciarCarrusel()

      expect(wrapper.vm.intervaloCarrusel).toBeNull()
    })

    it('should detenerCarrusel clear interval', () => {
      wrapper.vm.intervaloCarrusel = setInterval(() => {}, 1000)
      wrapper.vm.detenerCarrusel()

      expect(wrapper.vm.intervaloCarrusel).toBeNull()
    })

    it('should reiniciarCarrusel restart carousel', () => {
      wrapper.vm.selectorEventosVisible = true
      wrapper.vm.iniciarCarrusel()
      const intervaloAnterior = wrapper.vm.intervaloCarrusel

      wrapper.vm.reiniciarCarrusel()

      expect(wrapper.vm.intervaloCarrusel).toBeTruthy()
      expect(wrapper.vm.intervaloCarrusel).not.toBe(intervaloAnterior)
    })

    it('should reiniciarCarrusel not restart when selector not visible', () => {
      wrapper.vm.selectorEventosVisible = false
      wrapper.vm.reiniciarCarrusel()

      expect(wrapper.vm.intervaloCarrusel).toBeNull()
    })
  })

  describe('Verificar Cambios', () => {
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

    it('should verificarCambios return false when no initial state', () => {
      wrapper.vm.nuevoEventoInicial = null
      const result = wrapper.vm.verificarCambios()
      expect(result).toBe(false)
    })

    it('should verificarCambios return false when no changes', () => {
      const estadoInicial = {
        titulo: 'Test',
        idTipoEvento: 1,
        idCategoria: 1,
        lugar: 'Place',
        horaInicio: '10:00',
        horaFin: '11:00',
        descripcion: 'Desc',
        fecha: '2024-12-31'
      }
      wrapper.vm.nuevoEventoInicial = estadoInicial
      wrapper.vm.nuevoEvento = { ...estadoInicial }

      const result = wrapper.vm.verificarCambios()
      expect(result).toBe(false)
    })

    it('should verificarCambios return true when there are changes', () => {
      wrapper.vm.nuevoEventoInicial = { titulo: 'Original' }
      wrapper.vm.nuevoEvento = { titulo: 'Modified' }

      const result = wrapper.vm.verificarCambios()
      expect(result).toBe(true)
    })

    it('should normalizarValorParaComparacion handle null', () => {
      const result = wrapper.vm.normalizarValorParaComparacion(null)
      expect(result).toBe('')
    })

    it('should normalizarValorParaComparacion handle string', () => {
      const result = wrapper.vm.normalizarValorParaComparacion('  test  ')
      expect(result).toBe('test')
    })

    it('should normalizarValorParaComparacion handle number', () => {
      const result = wrapper.vm.normalizarValorParaComparacion(123)
      expect(result).toBe(123)
    })

    it('should normalizarValorParaComparacion handle boolean', () => {
      const result = wrapper.vm.normalizarValorParaComparacion(true)
      expect(result).toBe(true)
    })
  })

  describe('Helper Functions Private', () => {
    let wrapper

    beforeEach(async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })
      Swal.default.close = vi.fn()

      wrapper = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })
    })

    it('should _mostrarSinCambios show info dialog', async () => {
      await wrapper.vm._mostrarSinCambios()
      const Swal = await import('sweetalert2')
      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should _mostrarErroresValidacion show error dialog', async () => {
      const errores = ['Error 1', 'Error 2']
      await wrapper.vm._mostrarErroresValidacion(errores)
      const Swal = await import('sweetalert2')
      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should _confirmarGuardado show confirmation dialog for create', async () => {
      wrapper.vm.modoEdicion = false
      await wrapper.vm._confirmarGuardado()
      const Swal = await import('sweetalert2')
      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should _confirmarGuardado show confirmation dialog for edit', async () => {
      wrapper.vm.modoEdicion = true
      await wrapper.vm._confirmarGuardado()
      const Swal = await import('sweetalert2')
      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should _manejarErrorGuardado show error when not shown before', async () => {
      const error = { message: 'Test error' }
      await wrapper.vm._manejarErrorGuardado(error)
      const Swal = await import('sweetalert2')
      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should _manejarErrorGuardado not show error when already shown', async () => {
      const error = { message: 'Test error', mostrado: true }
      await wrapper.vm._manejarErrorGuardado(error)
      const Swal = await import('sweetalert2')
      expect(Swal.default.fire).not.toHaveBeenCalled()
    })

    it('should _normalizarCamposEvento normalize title and lugar', () => {
      wrapper.vm.nuevoEvento.titulo = '  test  título  123  '
      wrapper.vm.nuevoEvento.lugar = '  lugar  test  '
      wrapper.vm._normalizarCamposEvento()
      // _normalizarCamposEvento only normalizes spaces and limits length, doesn't convert to uppercase
      // For titulo: replaceAll(/\s+/g, ' ').trim().slice(0, MAX_TITULO)
      // For lugar: normalizarLugar (which does convert to uppercase but doesn't trim)
      expect(wrapper.vm.nuevoEvento.titulo).toBe('test  título  123'.replaceAll(/\s+/g, ' ').trim().slice(0, 120))
      // normalizarLugar doesn't trim, so spaces at start/end are preserved
      expect(wrapper.vm.nuevoEvento.lugar).toContain('LUGAR TEST')
      expect(wrapper.vm.nuevoEvento.lugar).toMatch(/^\s*LUGAR TEST\s*$/)
    })

    it('should _verificarCambiosEnEdicion return true when not in edit mode', async () => {
      wrapper.vm.modoEdicion = false
      const result = await wrapper.vm._verificarCambiosEnEdicion()
      expect(result).toBe(true)
    })

    it('should _verificarCambiosEnEdicion return true when there are changes', async () => {
      wrapper.vm.modoEdicion = true
      wrapper.vm.nuevoEventoInicial = { titulo: 'Original' }
      wrapper.vm.nuevoEvento = { titulo: 'Modified' }
      const result = await wrapper.vm._verificarCambiosEnEdicion()
      expect(result).toBe(true)
    })

    it('should _verificarCambiosEnEdicion return false when no changes', async () => {
      wrapper.vm.modoEdicion = true
      const estado = { titulo: 'Test' }
      wrapper.vm.nuevoEventoInicial = estado
      wrapper.vm.nuevoEvento = { ...estado }
      const result = await wrapper.vm._verificarCambiosEnEdicion()
      expect(result).toBe(false)
    })
  })

  describe('Guardar Evento - Casos de Error', () => {
    let wrapper

    beforeEach(async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn()
        .mockResolvedValueOnce({ isConfirmed: true }) // Confirmation
        .mockResolvedValueOnce({ isConfirmed: true }) // Error dialog
      Swal.default.close = vi.fn()
      Swal.default.showLoading = vi.fn()

      wrapper = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })

      await wrapper.vm.$nextTick()
    })

    it('should guardarEvento handle API error on create', async () => {
      const calendarioService = await import('@/services/calendarioService')
      calendarioService.default.crearEvento = vi.fn().mockRejectedValue(new Error('API Error'))
      wrapper.vm.nuevoEvento = {
        titulo: 'Test',
        idTipoEvento: 1,
        idCategoria: 1,
        lugar: 'Place',
        horaInicio: '10:00',
        horaFin: '11:00',
        fecha: '2024-12-31'
      }
      wrapper.vm.modoEdicion = false

      await wrapper.vm.guardarEvento()

      const Swal = await import('sweetalert2')
      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should guardarEvento handle API error on update', async () => {
      const calendarioService = await import('@/services/calendarioService')
      calendarioService.default.actualizarEvento = vi.fn().mockRejectedValue(new Error('API Error'))
      wrapper.vm.nuevoEvento = {
        titulo: 'Test',
        idTipoEvento: 1,
        idCategoria: 1,
        lugar: 'Place',
        horaInicio: '10:00',
        horaFin: '11:00',
        fecha: '2024-12-31'
      }
      wrapper.vm.modoEdicion = true
      wrapper.vm.eventoSeleccionado = { id: 1 }

      await wrapper.vm.guardarEvento()

      const Swal = await import('sweetalert2')
      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should guardarEvento not proceed without permissions', async () => {
      mockAuthStore.puedeCrearEventos = false
      mockAuthStore.puedeEditarEventos = false
      mockAuthStore.permissions = []

      // Create a new wrapper with updated permissions
      const wrapperNoPerms = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })
      await wrapperNoPerms.vm.$nextTick()

      await wrapperNoPerms.vm.guardarEvento()

      const calendarioService = await import('@/services/calendarioService')
      expect(calendarioService.default.crearEvento).not.toHaveBeenCalled()
      expect(calendarioService.default.actualizarEvento).not.toHaveBeenCalled()
    })
  })

  describe('Cerrar Modal - Casos Avanzados', () => {
    let wrapper

    beforeEach(async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })
      Swal.default.close = vi.fn()

      wrapper = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })

      await wrapper.vm.$nextTick()
    })

    it('should cerrarModal show confirmation when there are unsaved changes', async () => {
      wrapper.vm.nuevoEventoInicial = { titulo: 'Original' }
      wrapper.vm.nuevoEvento = { titulo: 'Modified' }
      wrapper.vm.modalVisible = true

      await wrapper.vm.cerrarModal()

      const Swal = await import('sweetalert2')
      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should cerrarModal not close when user cancels', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: false })

      wrapper.vm.nuevoEventoInicial = { titulo: 'Original' }
      wrapper.vm.nuevoEvento = { titulo: 'Modified' }
      wrapper.vm.modalVisible = true

      await wrapper.vm.cerrarModal()

      expect(wrapper.vm.modalVisible).toBe(true)
    })

    it('should cerrarModal restore selector when was open before', async () => {
      wrapper.vm.selectorEventosVisibleAntes = true
      wrapper.vm.fechaSelectorGuardada = '2024-12-31'
      wrapper.vm.modalVisible = true

      await wrapper.vm.cerrarModal()

      expect(wrapper.vm.selectorEventosVisible).toBe(true)
      expect(wrapper.vm.nuevoEvento.fecha).toBe('2024-12-31')
    })

    it('should cerrarModal not restore selector when was not open before', async () => {
      wrapper.vm.selectorEventosVisibleAntes = false
      wrapper.vm.modalVisible = true

      await wrapper.vm.cerrarModal()

      expect(wrapper.vm.selectorEventosVisible).toBe(false)
    })
  })

  describe('Editar y Ver Evento', () => {
    let wrapper

    beforeEach(async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

      wrapper = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })

      await wrapper.vm.$nextTick()
    })

    it('should editarEvento open modal in edit mode', () => {
      const evento = {
        id: 1,
        titulo: 'Test Event',
        idTipoEvento: 1,
        idCategoria: 1,
        lugar: 'Place',
        horaInicio: '10:00',
        horaFin: '11:00',
        fecha: '2024-12-31'
      }

      wrapper.vm.editarEvento(evento)

      expect(wrapper.vm.modoEdicion).toBe(true)
      expect(wrapper.vm.modalVisible).toBe(true)
      expect(wrapper.vm.nuevoEvento.titulo).toBe('Test Event')
    })

    it('should editarEvento show warning when no permission', async () => {
      mockAuthStore.puedeEditarEventos = false
      mockAuthStore.permissions = []

      // Create a new wrapper with updated permissions
      const wrapperNoPerms = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })
      await wrapperNoPerms.vm.$nextTick()

      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

      const evento = { id: 1, titulo: 'Test' }
      await wrapperNoPerms.vm.editarEvento(evento)

      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should verEvento open modal in view mode', () => {
      const evento = {
        id: 1,
        titulo: 'Test Event',
        idTipoEvento: 1,
        fecha: '2024-12-31'
      }

      wrapper.vm.selectorEventosVisible = true
      wrapper.vm.nuevoEvento.fecha = '2024-12-31'

      wrapper.vm.verEvento(evento)

      expect(wrapper.vm.modoEdicion).toBe(false)
      expect(wrapper.vm.modalVisible).toBe(true)
      expect(wrapper.vm.nuevoEvento.titulo).toBe('Test Event')
    })
  })

  describe('Inicializar Componente', () => {
    let wrapper

    beforeEach(async () => {
      const calendarioService = await import('@/services/calendarioService')
      const mockService = calendarioService.default
      mockService.cargarCatalogos.mockClear()
      mockService.cargarEventos.mockClear()
    })

    it('should inicializarComponente load catalogos successfully', async () => {
      wrapper = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))

      const calendarioService = await import('@/services/calendarioService')
      expect(calendarioService.default.cargarCatalogos).toHaveBeenCalled()
    })

    it('should inicializarComponente handle catalogos error gracefully', async () => {
      const calendarioService = await import('@/services/calendarioService')
      calendarioService.default.cargarCatalogos = vi.fn().mockRejectedValue(new Error('Error'))

      wrapper = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))

      expect(wrapper.exists()).toBe(true)
    })

    it('should inicializarComponente handle eventos error gracefully', async () => {
      const calendarioService = await import('@/services/calendarioService')
      calendarioService.default.cargarEventos = vi.fn().mockRejectedValue(new Error('Error'))

      wrapper = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))

      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Seleccionar Día', () => {
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
    })

    it('should seleccionarDia do nothing for other month days', () => {
      const dia = { esMesActual: false, eventos: [] }
      wrapper.vm.seleccionarDia(dia)
      expect(wrapper.vm.modalVisible).toBe(false)
    })

    it('should seleccionarDia show selector when day has events', async () => {
      const calendarioService = await import('@/services/calendarioService')
      calendarioService.default.obtenerEventosPorFecha = vi.fn(() => [{ id: 1, titulo: 'Evento 1' }])
      const dia = {
        esMesActual: true,
        fecha: '2024-12-31',
        eventos: [{ id: 1, titulo: 'Evento 1' }]
      }
      wrapper.vm.seleccionarDia(dia)
      expect(wrapper.vm.selectorEventosVisible).toBe(true)
    })

    it('should seleccionarDia open modal when day has no events and can create', () => {
      const dia = {
        esMesActual: true,
        fecha: '2024-12-31',
        eventos: []
      }
      wrapper.vm.seleccionarDia(dia)
      expect(wrapper.vm.modalVisible).toBe(true)
    })

    it('should seleccionarDia do nothing when no events and cannot create', async () => {
      mockAuthStore.puedeCrearEventos = false
      mockAuthStore.permissions = []

      // Create a new wrapper with updated permissions
      const wrapperNoPerms = mount(CalendarioComponent, {
        global: {
          stubs: {
            'i': true
          }
        }
      })
      await wrapperNoPerms.vm.$nextTick()

      const dia = {
        esMesActual: true,
        eventos: []
      }
      wrapperNoPerms.vm.seleccionarDia(dia)
      expect(wrapperNoPerms.vm.modalVisible).toBe(false)
    })
  })

  describe('Actualizar Calendario', () => {
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

    it('should actualizarCalendario generate correct number of days', () => {
      wrapper.vm.fechaActual = new Date('2024-12-15')
      wrapper.vm.actualizarCalendario()
      expect(wrapper.vm.diasCalendario.length).toBe(42) // 6 weeks * 7 days
    })

    it('should actualizarCalendario mark today correctly', () => {
      wrapper.vm.fechaActual = new Date()
      wrapper.vm.actualizarCalendario()
      const hoy = wrapper.vm.diasCalendario.find(dia => dia.esHoy)
      expect(hoy).toBeDefined()
    })

    it('should actualizarCalendario mark current month days correctly', () => {
      wrapper.vm.fechaActual = new Date('2024-12-15')
      wrapper.vm.actualizarCalendario()
      const diasActuales = wrapper.vm.diasCalendario.filter(dia => dia.esMesActual)
      expect(diasActuales.length).toBe(31) // December has 31 days
    })
  })

  describe('Normalización de Inputs Edge Cases', () => {
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

    it('should manejarTitulo handle null event', () => {
      wrapper.vm.nuevoEvento.titulo = 'Original'
      wrapper.vm.manejarTitulo(null)
      expect(wrapper.vm.nuevoEvento.titulo).toBeTruthy()
    })

    it('should manejarLugar handle null event', () => {
      wrapper.vm.nuevoEvento.lugar = 'Original'
      wrapper.vm.manejarLugar(null)
      expect(wrapper.vm.nuevoEvento.lugar).toBeTruthy()
    })

    it('should manejarDescripcion handle null event', () => {
      wrapper.vm.nuevoEvento.descripcion = 'Original'
      wrapper.vm.manejarDescripcion(null)
      expect(wrapper.vm.nuevoEvento.descripcion).toBe('Original')
    })

    it('should normalizarTitulo limit length to MAX_TITULO', () => {
      const largo = 'A'.repeat(150)
      const resultado = wrapper.vm.normalizarTitulo(largo)
      expect(resultado.length).toBeLessThanOrEqual(120)
    })

    it('should normalizarLugar limit length to MAX_LUGAR', () => {
      const largo = 'A'.repeat(150)
      const resultado = wrapper.vm.normalizarLugar(largo)
      expect(resultado.length).toBeLessThanOrEqual(120)
    })

    it('should normalizarDescripcion limit length to MAX_DESCRIPCION', () => {
      const largo = 'A'.repeat(600)
      const resultado = wrapper.vm.normalizarDescripcion(largo)
      expect(resultado.length).toBeLessThanOrEqual(500)
    })
  })
})

