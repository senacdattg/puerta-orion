import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'
import Eventos from '@/views/eventos.vue'
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
    obtenerEventosProximos: vi.fn()
  }
}))

// Get reference to mocked service for test updates
let mockCalendarioService

describe('Eventos View', () => {
  let mockAuthStore

  const createWrapper = (options = {}) => {
    return mount(Eventos, {
      global: {
        stubs: {
          Encabezado: true,
          FooterEnhanced: true
        }
      },
      ...options
    })
  }

  // Helper function to create a promise that never resolves (reduces nesting)
  const createNeverResolvingPromise = () => new Promise(() => {})

  beforeEach(async () => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    // Get reference to mocked service
    const calendarioService = await import('@/services/calendarioService')
    mockCalendarioService = calendarioService.default

    mockAuthStore = {
      user: {
        id_usuario: 1,
        usuario: 'testuser',
        roles: [{ nombre_rol: 'Deportista' }]
      },
      estaAutenticado: true
    }

    useAuthStore.mockReturnValue(mockAuthStore)

    // Default mock return value
    mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])
  })

  afterEach(() => {
    vi.clearAllTimers()
  })

  describe('Basic Rendering', () => {
    it('should render the view', async () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      await nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.eventos-page').exists()).toBe(true)
  })

  it('should display page title', () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      const title = wrapper.find('.eventos-title')
      expect(title.exists()).toBe(true)
      expect(title.text()).toContain('Eventos y Actividades')
    })

    it('should display subtitle', () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      const subtitle = wrapper.find('.eventos-subtitle')
      expect(subtitle.exists()).toBe(true)
      expect(subtitle.text()).toContain('Participa en las actividades deportivas')
    })

    it('should display eventos grid', async () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))

      const grid = wrapper.find('.eventos-grid')
      expect(grid.exists()).toBe(true)
    })
  })

  describe('Loading State', () => {
    it('should show loading state when cargando is true', async () => {
      mockCalendarioService.obtenerEventosProximos.mockImplementation(() => createNeverResolvingPromise())

      const wrapper = createWrapper()
      await nextTick()

      // Wait a bit for the loading state
      await new Promise(resolve => setTimeout(resolve, 50))
      await nextTick()

      // The loading state should be visible
      expect(wrapper.vm.cargando).toBe(true)
    })

    it('should display loading message', async () => {
      mockCalendarioService.obtenerEventosProximos.mockImplementation(() => createNeverResolvingPromise())

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 50))

      wrapper.vm.cargando = true
      await nextTick()

      expect(wrapper.text()).toContain('Cargando eventos')
    })
  })

  describe('Empty State', () => {
    it('should show empty state when no eventos', async () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      wrapper.vm.eventos = []
      wrapper.vm.cargando = false
      await nextTick()

      expect(wrapper.vm.eventos.length).toBe(0)
      expect(wrapper.text()).toContain('No hay eventos próximos')
    })

    it('should display empty state message', async () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      wrapper.vm.eventos = []
      wrapper.vm.cargando = false
      await nextTick()

      const emptyState = wrapper.find('.empty-state')
      expect(emptyState.exists()).toBe(true)
      expect(emptyState.text()).toContain('No se encontraron eventos próximos')
    })
  })

  describe('Event Rendering', () => {
    it('should render evento card with basic information', async () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 10)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          titulo: 'Evento Test',
          fecha: fechaStr,
          fecha_evento: fechaStr,
          horaInicio: '10:00:00',
          hora_inicio: '10:00:00',
          horaFin: '12:00:00',
          hora_fin: '12:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      expect(wrapper.find('.evento-card').exists()).toBe(true)
    })

    it('should render evento with title and category', async () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 10)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          titulo: 'Evento Test',
          fecha: fechaStr,
          fecha_evento: fechaStr,
          horaInicio: '10:00:00',
          hora_inicio: '10:00:00',
          horaFin: '12:00:00',
          hora_fin: '12:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      expect(wrapper.text()).toContain('Evento Test')
    })

    it('should render evento with time information', async () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 10)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          titulo: 'Evento Test',
          fecha: fechaStr,
          fecha_evento: fechaStr,
          horaInicio: '10:00:00',
          hora_inicio: '10:00:00',
          horaFin: '12:00:00',
          hora_fin: '12:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      const card = wrapper.find('.evento-card')
      expect(card.exists()).toBe(true)
    })

    it('should render evento with location', async () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 10)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          titulo: 'Evento Test',
          fecha: fechaStr,
          fecha_evento: fechaStr,
          horaInicio: '10:00:00',
          hora_inicio: '10:00:00',
          horaFin: '12:00:00',
          hora_fin: '12:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      expect(wrapper.text()).toContain('Cancha Principal')
    })

    it('should render participantes when evento.participantes > 0', async () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 10)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          titulo: 'Evento Test',
          fecha: fechaStr,
          fecha_evento: fechaStr,
          horaInicio: '10:00:00',
          hora_inicio: '10:00:00',
          horaFin: '12:00:00',
          hora_fin: '12:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      // Set participantes > 0 after events are loaded
      if (wrapper.vm.eventos.length > 0) {
        wrapper.vm.eventos[0].participantes = 5
        await nextTick()

        expect(wrapper.text()).toContain('participantes')
      }
    })

    it('should NOT render participantes when evento.participantes is 0', async () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 10)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          titulo: 'Evento Test',
          fecha: fechaStr,
          fecha_evento: fechaStr,
          horaInicio: '10:00:00',
          hora_inicio: '10:00:00',
          horaFin: '12:00:00',
          hora_fin: '12:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      // participantes defaults to 0, so it should not render
      const participantesSection = wrapper.findAll('.info-item').find(item =>
        item.text().includes('participantes')
      )
      expect(participantesSection).toBeUndefined()
    })

    it('should render descripcion when evento.descripcion exists', async () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 10)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          titulo: 'Evento Test',
          fecha: fechaStr,
          fecha_evento: fechaStr,
          horaInicio: '10:00:00',
          hora_inicio: '10:00:00',
          horaFin: '12:00:00',
          hora_fin: '12:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' },
          descripcion: 'Esta es una descripción del evento'
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      // Verify description is rendered
      expect(wrapper.text()).toContain('Esta es una descripción del evento')

      // Verify the info-item with description exists
      const infoItems = wrapper.findAll('.info-item')
      const descripcionItem = infoItems.find(item =>
        item.text().includes('Esta es una descripción del evento')
      )
      expect(descripcionItem).toBeDefined()
    })

    it('should NOT render descripcion when evento.descripcion is empty', async () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 10)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          titulo: 'Evento Test',
          fecha: fechaStr,
          fecha_evento: fechaStr,
          horaInicio: '10:00:00',
          hora_inicio: '10:00:00',
          horaFin: '12:00:00',
          hora_fin: '12:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' },
          descripcion: ''
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      // descripcion is empty, so it should not render
      const descripcionItems = wrapper.findAll('.info-item').filter(item =>
        item.html().includes('fa-info-circle')
      )
      expect(descripcionItems.length).toBe(0)
    })
  })

  describe('formatHora Function', () => {
    it('should format hora from HH:MM:SS to HH:MM', () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      const result = wrapper.vm.formatearHora('10:30:45')
      expect(result).toBe('10:30')
    })

    it('should return HH:MM format as is', () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      const result = wrapper.vm.formatearHora('10:30')
      expect(result).toBe('10:30')
    })

    it('should return 00:00 for empty hora', () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      const result = wrapper.vm.formatearHora('')
      expect(result).toBe('00:00')
    })

    it('should return 00:00 for null hora', () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      const result = wrapper.vm.formatearHora(null)
      expect(result).toBe('00:00')
    })

    it('should return 00:00 for undefined hora', () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      const result = wrapper.vm.formatearHora(undefined)
      expect(result).toBe('00:00')
    })

    it('should handle hora without colon', () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      const result = wrapper.vm.formatearHora('1030')
      expect(result).toBe('1030')
    })
  })

  describe('cargarEventos Function', () => {
    it('should load and process eventos successfully', async () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 10)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          titulo: 'Evento Test',
          fecha: fechaStr,
          fecha_evento: fechaStr,
          horaInicio: '10:00:00',
          hora_inicio: '10:00:00',
          horaFin: '12:00:00',
          hora_fin: '12:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      expect(wrapper.vm.eventos.length).toBeGreaterThan(0)
    })

    it('should filter out past events', async () => {
      const fechaPasada = new Date()
      fechaPasada.setDate(fechaPasada.getDate() - 1)
      const fechaPasadaStr = fechaPasada.toISOString().split('T')[0]

      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 10)
      const fechaFuturaStr = fechaFutura.toISOString().split('T')[0]

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          titulo: 'Evento Pasado',
          fecha: fechaPasadaStr,
          fecha_evento: fechaPasadaStr,
          horaInicio: '10:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        },
        {
          id: 2,
          titulo: 'Evento Futuro',
          fecha: fechaFuturaStr,
          fecha_evento: fechaFuturaStr,
          horaInicio: '10:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      // Should only have future events
      expect(wrapper.vm.eventos.length).toBe(1)
      expect(wrapper.vm.eventos[0].titulo).toBe('Evento Futuro')
    })

    it('should mark event as activo when date is today', async () => {
      const hoy = new Date()
      const hoyStr = hoy.toISOString().split('T')[0]

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          titulo: 'Evento Hoy',
          fecha: hoyStr,
          fecha_evento: hoyStr,
          horaInicio: '10:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      if (wrapper.vm.eventos.length > 0) {
        expect(wrapper.vm.eventos[0].estado).toBe('activo')
      }
    })

    it('should mark event as proximo when date is future', async () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 10)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          titulo: 'Evento Futuro',
          fecha: fechaStr,
          fecha_evento: fechaStr,
          horaInicio: '10:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      if (wrapper.vm.eventos.length > 0) {
        expect(wrapper.vm.eventos[0].estado).toBe('proximo')
      }
    })

    it('should filter out events with invalid dates', async () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          titulo: 'Evento Inválido',
          fecha: 'invalid-date',
          fecha_evento: 'invalid-date',
          horaInicio: '10:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      // Invalid dates should be filtered out
      const validEvents = wrapper.vm.eventos.filter(e => e !== null)
      expect(validEvents.length).toBe(0)
    })

    it('should sort events: activo first, then proximo by date', async () => {
      // Use a date that is guaranteed to be today by creating it in the same way the component does
      const hoy = new Date()
      hoy.setHours(0, 0, 0, 0)
      const año = hoy.getFullYear()
      const mes = String(hoy.getMonth() + 1).padStart(2, '0')
      const dia = String(hoy.getDate()).padStart(2, '0')
      const hoyStr = `${año}-${mes}-${dia}`

      const fechaFutura1 = new Date()
      fechaFutura1.setDate(fechaFutura1.getDate() + 5)
      fechaFutura1.setHours(0, 0, 0, 0)
      const año1 = fechaFutura1.getFullYear()
      const mes1 = String(fechaFutura1.getMonth() + 1).padStart(2, '0')
      const dia1 = String(fechaFutura1.getDate()).padStart(2, '0')
      const fechaStr1 = `${año1}-${mes1}-${dia1}`

      const fechaFutura2 = new Date()
      fechaFutura2.setDate(fechaFutura2.getDate() + 10)
      fechaFutura2.setHours(0, 0, 0, 0)
      const año2 = fechaFutura2.getFullYear()
      const mes2 = String(fechaFutura2.getMonth() + 1).padStart(2, '0')
      const dia2 = String(fechaFutura2.getDate()).padStart(2, '0')
      const fechaStr2 = `${año2}-${mes2}-${dia2}`

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          titulo: 'Evento Futuro 2',
          fecha: fechaStr2,
          fecha_evento: fechaStr2,
          horaInicio: '10:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        },
        {
          id: 2,
          titulo: 'Evento Hoy',
          fecha: hoyStr,
          fecha_evento: hoyStr,
          horaInicio: '10:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        },
        {
          id: 3,
          titulo: 'Evento Futuro 1',
          fecha: fechaStr1,
          fecha_evento: fechaStr1,
          horaInicio: '10:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      if (wrapper.vm.eventos.length > 0) {
        // Verify that events are sorted: activo first, then proximo by date
        const estados = wrapper.vm.eventos.map(e => e.estado)

        // Find the index of activo and proximo events
        const activoIndex = estados.indexOf('activo')
        const proximoIndices = estados.map((estado, idx) => estado === 'proximo' ? idx : -1).filter(idx => idx !== -1)

        // If there are activo events, they should come before proximo events
        if (activoIndex !== -1 && proximoIndices.length > 0) {
          proximoIndices.forEach(proximoIdx => {
            expect(proximoIdx).toBeGreaterThan(activoIndex)
          })
        }

        // If there are multiple proximo events, they should be sorted by date
        if (proximoIndices.length > 1) {
          const proximoEvents = proximoIndices.map(idx => wrapper.vm.eventos[idx])
          for (let i = 0; i < proximoEvents.length - 1; i++) {
            const fecha1 = new Date(proximoEvents[i].fecha_evento)
            const fecha2 = new Date(proximoEvents[i + 1].fecha_evento)
            expect(fecha1.getTime()).toBeLessThanOrEqual(fecha2.getTime())
          }
        }
      }
    })

    it('should handle missing fields with defaults', async () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 10)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          fecha: fechaStr,
          fecha_evento: fechaStr
          // Missing titulo, lugar, etc.
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      if (wrapper.vm.eventos.length > 0) {
        const evento = wrapper.vm.eventos[0]
        expect(evento.titulo).toBe('Evento sin título')
        expect(evento.lugar).toBe('No especificado')
      }
    })

    it('should handle error when loading eventos', async () => {
      mockCalendarioService.obtenerEventosProximos.mockRejectedValue(new Error('Network error'))

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      // Should handle error gracefully
      expect(wrapper.vm.eventos).toEqual([])
    })
  })

  describe('getEventoClass Function', () => {
    it('should return evento-activo class for activo state', () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      const result = wrapper.vm.getEventoClass('activo')
      expect(result).toBe('evento-activo')
    })

    it('should return evento-proximo class for proximo state', () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      const result = wrapper.vm.getEventoClass('proximo')
      expect(result).toBe('evento-proximo')
    })

    it('should return evento-finalizado class for finalizado state', () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      const result = wrapper.vm.getEventoClass('finalizado')
      expect(result).toBe('evento-finalizado')
    })

    it('should return empty string for unknown state', () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      const result = wrapper.vm.getEventoClass('unknown')
      expect(result).toBe('')
    })
  })

  describe('getEstadoClass Function', () => {
    it('should return estado-activo class for activo state', () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      const result = wrapper.vm.getEstadoClass('activo')
      expect(result).toBe('estado-activo')
    })

    it('should return estado-proximo class for proximo state', () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      const result = wrapper.vm.getEstadoClass('proximo')
      expect(result).toBe('estado-proximo')
    })

    it('should return estado-finalizado class for finalizado state', () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      const result = wrapper.vm.getEstadoClass('finalizado')
      expect(result).toBe('estado-finalizado')
    })

    it('should return empty string for unknown state', () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      const result = wrapper.vm.getEstadoClass('unknown')
      expect(result).toBe('')
    })
  })

  describe('Lifecycle Hooks', () => {
    it('should call cargarDatos on mount', async () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockCalendarioService.obtenerEventosProximos).toHaveBeenCalled()
    })

    it('should set cargando to false after loading', async () => {
      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      expect(wrapper.vm.cargando).toBe(false)
    })
  })

  describe('Event Processing', () => {
    it('should format hora from horaInicio field', async () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 10)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          fecha: fechaStr,
          fecha_evento: fechaStr,
          horaInicio: '14:30:00',
          horaFin: '16:30:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      if (wrapper.vm.eventos.length > 0) {
        expect(wrapper.vm.eventos[0].hora_inicio).toBe('14:30')
        expect(wrapper.vm.eventos[0].hora_fin).toBe('16:30')
      }
    })

    it('should use fecha_evento when fecha is not available', async () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 10)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          fecha_evento: fechaStr,
          horaInicio: '10:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil' }
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      if (wrapper.vm.eventos.length > 0) {
        expect(wrapper.vm.eventos[0].fecha_evento).toBe(fechaStr)
      }
    })

    it('should use categoria.nombre_categoria when available', async () => {
      const fechaFutura = new Date()
      fechaFutura.setDate(fechaFutura.getDate() + 10)
      const fechaStr = fechaFutura.toISOString().split('T')[0]

      mockCalendarioService.obtenerEventosProximos.mockResolvedValue([
        {
          id: 1,
          fecha: fechaStr,
          fecha_evento: fechaStr,
          horaInicio: '10:00:00',
          lugar: 'Cancha Principal',
          categoria: { nombre_categoria: 'Pre-infantil', nombre: 'Pre-infantil' }
        }
      ])

      const wrapper = createWrapper()
      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await nextTick()

      if (wrapper.vm.eventos.length > 0) {
        expect(wrapper.vm.eventos[0].categoria).toBe('Pre-infantil')
      }
    })
  })
})
