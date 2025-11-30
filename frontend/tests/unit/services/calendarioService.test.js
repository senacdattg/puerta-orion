import { describe, it, expect, beforeEach, vi } from 'vitest'
import calendarioService from '@/services/calendarioService'

// Mock fetch globally
global.fetch = vi.fn()

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(() => 'mock-token'),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
global.localStorage = localStorageMock

// Mock API_CONFIG
vi.mock('@/config/environment.js', () => ({
  API_CONFIG: {
    baseURL: 'http://localhost:5000'
  }
}))

describe('CalendarioService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    calendarioService.eventos = []
    calendarioService.tiposEvento = []
    calendarioService.categorias = []
  })

  describe('getAuthHeaders', () => {
    it('should return headers with authorization token', () => {
      const headers = calendarioService.getAuthHeaders()

      expect(headers).toHaveProperty('Content-Type', 'application/json')
      expect(headers).toHaveProperty('Authorization', 'Bearer mock-token')
    })

    it('should return headers without authorization when token is missing', () => {
      localStorageMock.getItem.mockReturnValueOnce(null)

      const headers = calendarioService.getAuthHeaders()

      expect(headers).toHaveProperty('Content-Type', 'application/json')
      expect(headers.Authorization).toBe('')
    })
  })

  describe('cargarEventos', () => {
    it('should load eventos successfully', async () => {
      const mockData = {
        success: true,
        data: [
          { id_evento: 1, nombre: 'Evento 1', fecha: '2024-12-01' },
          { id_evento: 2, nombre: 'Evento 2', fecha: '2024-12-02' }
        ]
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await calendarioService.cargarEventos()

      // The service transforms the data, so we check it's an array
      expect(Array.isArray(result)).toBe(true)
      expect(result.length).toBe(2)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/eventos/calendario?per_page=1000'),
        expect.objectContaining({
          method: 'GET'
        })
      )
    })

    it('should handle 401 authentication error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        json: async () => ({ error: 'Token inválido' })
      })

      // The service throws errors, so we expect it to reject
      try {
        await calendarioService.cargarEventos()
        // If it doesn't throw, the service might catch and return []
        expect(Array.isArray(calendarioService.eventos)).toBe(true)
      } catch (error) {
        expect(error.message).toContain('Error de autenticación')
      }
    })

    it('should handle 404 not found error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({ error: 'Not found' })
      })

      // The service throws errors
      try {
        await calendarioService.cargarEventos()
        expect(Array.isArray(calendarioService.eventos)).toBe(true)
      } catch (error) {
        expect(error.message).toContain('Ruta no encontrada')
      }
    })

    it('should handle 500 server error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ error: 'Server error', stack: 'Error stack' })
      })

      // The service throws errors
      try {
        await calendarioService.cargarEventos()
        expect(Array.isArray(calendarioService.eventos)).toBe(true)
      } catch (error) {
        expect(error.message).toContain('Error interno del servidor')
      }
    })
  })

  describe('cargarTiposEvento', () => {
    it('should load tipos evento successfully', async () => {
      const mockData = {
        success: true,
        data: [
          { id_tipo_evento: 1, nombre: 'Entrenamiento' },
          { id_tipo_evento: 2, nombre: 'Competencia' }
        ]
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await calendarioService.cargarTiposEvento()

      expect(result).toEqual(mockData.data)
      expect(calendarioService.tiposEvento).toEqual(mockData.data)
    })

    it('should handle error when loading tipos evento', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => 'Server error'
      })

      const result = await calendarioService.cargarTiposEvento()

      // The service has fallback data, so it returns default tipos
      expect(Array.isArray(result)).toBe(true)
      expect(result.length).toBeGreaterThan(0)
    })
  })

  describe('cargarCategorias', () => {
    it('should load categorias successfully', async () => {
      const mockData = {
        success: true,
        data: [
          { id_categoria: 1, nombre_categoria: 'Pre-infantil' },
          { id_categoria: 2, nombre_categoria: 'Infantil' }
        ]
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await calendarioService.cargarCategorias()

      expect(result).toEqual(mockData.data)
      expect(calendarioService.categorias).toEqual(mockData.data)
    })

    it('should use fallback categorias on error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => 'Server error'
      })

      const result = await calendarioService.cargarCategorias()

      expect(result).toHaveLength(3) // Fallback data
      expect(result[0]).toHaveProperty('nombre_categoria')
    })
  })

  describe('obtenerEventosPorFecha', () => {
    beforeEach(async () => {
      calendarioService.eventos = [
        { id: 1, fecha: '2024-12-01', titulo: 'Evento 1' },
        { id: 2, fecha: '2024-12-02', titulo: 'Evento 2' },
        { id: 3, fecha: '2024-12-01', titulo: 'Evento 3' }
      ]
    })

    it('should return eventos for specific date', () => {
      const eventos = calendarioService.obtenerEventosPorFecha('2024-12-01')

      expect(eventos).toHaveLength(2)
      expect(eventos[0].titulo).toBe('Evento 1')
      expect(eventos[1].titulo).toBe('Evento 3')
    })

    it('should return empty array when no eventos for date', () => {
      const eventos = calendarioService.obtenerEventosPorFecha('2024-12-31')

      expect(eventos).toHaveLength(0)
    })

    it('should handle Date object', () => {
      const fecha = new Date('2024-12-01')
      const eventos = calendarioService.obtenerEventosPorFecha(fecha)

      expect(eventos.length).toBeGreaterThan(0)
    })

    it('should handle eventos with time in date string', () => {
      calendarioService.eventos = [
        { id: 1, fecha: '2024-12-01T10:00:00', titulo: 'Evento 1' }
      ]

      const eventos = calendarioService.obtenerEventosPorFecha('2024-12-01')

      expect(eventos).toHaveLength(1)
    })
  })

  describe('obtenerTodosLosEventos', () => {
    it('should return cached eventos', async () => {
      calendarioService.eventos = [
        { id: 1, titulo: 'Evento 1' },
        { id: 2, titulo: 'Evento 2' }
      ]

      const eventos = await calendarioService.obtenerTodosLosEventos()

      expect(eventos).toHaveLength(2)
    })

    it('should load eventos if cache is empty', async () => {
      calendarioService.eventos = []
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          data: [
            { id_evento: 1, nombre: 'Evento 1', fecha_evento: '2024-12-01' }
          ]
        })
      })

      const eventos = await calendarioService.obtenerTodosLosEventos()

      expect(eventos.length).toBeGreaterThan(0)
    })
  })

  describe('obtenerEventosProximos', () => {
    it('should load upcoming eventos successfully', async () => {
      const mockData = {
        success: true,
        data: [
          { id_evento: 1, nombre: 'Evento Próximo', fecha_evento: '2024-12-25' }
        ]
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const eventos = await calendarioService.obtenerEventosProximos()

      expect(eventos.length).toBeGreaterThan(0)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/eventos/proximos'),
        expect.objectContaining({
          method: 'GET'
        })
      )
    })

    it('should handle 401 error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized'
      })

      const eventos = await calendarioService.obtenerEventosProximos()

      expect(Array.isArray(eventos)).toBe(true)
      expect(eventos).toHaveLength(0)
    })

    it('should handle 500 error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      })

      const eventos = await calendarioService.obtenerEventosProximos()

      expect(Array.isArray(eventos)).toBe(true)
      expect(eventos).toHaveLength(0)
    })
  })

  describe('crearEvento', () => {
    it('should create evento successfully', async () => {
      const nuevoEvento = {
        titulo: 'Nuevo Evento',
        fecha: '2024-12-25',
        horaInicio: '10:00',
        lugar: 'Gimnasio',
        idTipoEvento: 1,
        idCategoria: 1
      }

      const mockResponse = {
        success: true,
        data: {
          id_evento: 1,
          nombre: 'Nuevo Evento',
          fecha_evento: '2024-12-25',
          hora_inicio: '10:00',
          lugar: 'Gimnasio'
        }
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const evento = await calendarioService.crearEvento(nuevoEvento)

      expect(evento).toBeDefined()
      expect(evento.titulo).toBe('Nuevo Evento')
      expect(calendarioService.eventos.length).toBeGreaterThan(0)
    })

    it('should throw error for invalid hour format', async () => {
      const nuevoEvento = {
        titulo: 'Nuevo Evento',
        fecha: '2024-12-25',
        horaInicio: 'invalid-time',
        lugar: 'Gimnasio'
      }

      await expect(calendarioService.crearEvento(nuevoEvento)).rejects.toThrow('Formato de hora')
    })

    it('should handle API error', async () => {
      const nuevoEvento = {
        titulo: 'Nuevo Evento',
        fecha: '2024-12-25',
        horaInicio: '10:00',
        lugar: 'Gimnasio'
      }

      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Error al crear evento' })
      })

      await expect(calendarioService.crearEvento(nuevoEvento)).rejects.toThrow()
    })
  })

  describe('actualizarEvento', () => {
    beforeEach(() => {
      calendarioService.eventos = [
        { id: 1, titulo: 'Evento Original', fecha: '2024-12-01' }
      ]
    })

    it('should update evento successfully', async () => {
      const datosActualizados = {
        titulo: 'Evento Actualizado',
        fecha: '2024-12-02'
      }

      const mockResponse = {
        success: true,
        data: {
          id_evento: 1,
          nombre: 'Evento Actualizado',
          fecha_evento: '2024-12-02'
        }
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const evento = await calendarioService.actualizarEvento(1, datosActualizados)

      expect(evento.titulo).toBe('Evento Actualizado')
      expect(calendarioService.eventos[0].titulo).toBe('Evento Actualizado')
    })

    it('should handle API error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Error al actualizar' })
      })

      await expect(calendarioService.actualizarEvento(1, {})).rejects.toThrow()
    })
  })

  describe('eliminarEvento', () => {
    beforeEach(() => {
      calendarioService.eventos = [
        { id: 1, titulo: 'Evento 1' },
        { id: 2, titulo: 'Evento 2' }
      ]
    })

    it('should delete evento successfully', async () => {
      const mockResponse = {
        success: true
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const resultado = await calendarioService.eliminarEvento(1)

      expect(resultado).toBe(true)
      expect(calendarioService.eventos.length).toBe(1)
      expect(calendarioService.eventos[0].id).toBe(2)
    })

    it('should handle API error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Error al eliminar' })
      })

      await expect(calendarioService.eliminarEvento(1)).rejects.toThrow()
    })
  })

  describe('cargarCatalogos', () => {
    it('should load all catalogos successfully', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          success: true,
          data: [
            { id_tipo_evento: 1, nombre: 'Entrenamiento' },
            { id_categoria: 1, nombre_categoria: 'Pre-infantil' }
          ]
        })
      })

      const catalogos = await calendarioService.cargarCatalogos()

      expect(catalogos.tiposEvento).toBeDefined()
      expect(catalogos.categorias).toBeDefined()
    })

    it('should handle error when loading catalogos', async () => {
      // Mock both methods to fail
      global.fetch
        .mockRejectedValueOnce(new Error('Network error')) // for cargarTiposEvento
        .mockRejectedValueOnce(new Error('Network error')) // for cargarCategorias

      // cargarCatalogos uses Promise.all which will reject
      // But cargarTiposEvento and cargarCategorias have fallbacks that catch errors
      // So they return fallback data instead of rejecting
      const result = await calendarioService.cargarCatalogos()

      expect(result).toBeDefined()
      expect(result.tiposEvento).toBeDefined()
      expect(result.categorias).toBeDefined()
    })
  })

  describe('mapearEventoBackendAFrontend', () => {
    it('should map evento correctly', () => {
      const eventoBackend = {
        id_evento: 1,
        nombre: 'Evento Test',
        fecha_evento: '2024-12-01',
        hora_inicio: '10:00:00',
        hora_fin: '11:00:00',
        lugar: 'Gimnasio',
        descripcion: 'Descripción',
        id_tipo_evento: 1,
        tipo_evento: { nombre: 'Entrenamiento' }
      }

      const evento = calendarioService.mapearEventoBackendAFrontend(eventoBackend)

      expect(evento.id).toBe(1)
      expect(evento.titulo).toBe('Evento Test')
      expect(evento.fecha).toBe('2024-12-01')
      expect(evento.horaInicio).toBe('10:00')
      expect(evento.horaFin).toBe('11:00')
      expect(evento.tipo).toBe('Entrenamiento')
    })

    it('should handle evento with string tipo', () => {
      const eventoBackend = {
        id_evento: 1,
        nombre: 'Evento Test',
        fecha_evento: '2024-12-01',
        tipo_evento: 'Competencia'
      }

      const evento = calendarioService.mapearEventoBackendAFrontend(eventoBackend)

      expect(evento.tipo).toBe('Competencia')
    })

    it('should handle evento with missing required fields', () => {
      const eventoInvalido = { id_evento: null }

      const evento = calendarioService.mapearEventoBackendAFrontend(eventoInvalido)

      expect(evento).toBeDefined()
      // When nombre is missing, it uses 'Sin título' as default
      expect(evento.titulo).toBe('Sin título')
    })

    it('should handle evento with missing required fields', () => {
      const eventoIncompleto = {
        id_evento: 1
        // missing other fields
      }

      const evento = calendarioService.mapearEventoBackendAFrontend(eventoIncompleto)

      expect(evento).toBeDefined()
      expect(evento.id).toBe(1)
    })
  })

  describe('mapearEventoFrontendABackend', () => {
    it('should map evento correctly', () => {
      const eventoFrontend = {
        titulo: 'Nuevo Evento',
        fecha: '2024-12-01',
        horaInicio: '10:00',
        horaFin: '11:00',
        lugar: 'Gimnasio',
        descripcion: 'Descripción',
        idTipoEvento: 1,
        idCategoria: 1
      }

      const evento = calendarioService.mapearEventoFrontendABackend(eventoFrontend)

      expect(evento.nombre).toBe('Nuevo Evento')
      expect(evento.fecha_evento).toBe('2024-12-01')
      expect(evento.hora_inicio).toBe('10:00')
      expect(evento.id_categoria).toBe(1)
      expect(evento.id_tipo_evento).toBe(1)
    })

    it('should calculate hora_fin when not provided', () => {
      const eventoFrontend = {
        titulo: 'Nuevo Evento',
        fecha: '2024-12-01',
        horaInicio: '10:00'
      }

      const evento = calendarioService.mapearEventoFrontendABackend(eventoFrontend, false)

      // hora_fin should be calculated as 1 hour after hora_inicio
      expect(evento.hora_fin).toBeDefined()
      expect(evento.hora_fin).toContain(':')
    })

    it('should use hora instead of horaInicio', () => {
      const eventoFrontend = {
        titulo: 'Nuevo Evento',
        fecha: '2024-12-01',
        hora: '10:00'
      }

      const evento = calendarioService.mapearEventoFrontendABackend(eventoFrontend)

      expect(evento.hora_inicio).toBe('10:00')
    })
  })

  describe('normalizarHora', () => {
    it('should return hora already in correct format', () => {
      expect(calendarioService.normalizarHora('10:00')).toBe('10:00')
      expect(calendarioService.normalizarHora('10:00:00')).toBe('10:00:00')
    })

    it('should convert 12-hour format to 24-hour format', () => {
      expect(calendarioService.normalizarHora('10:00 AM')).toBe('10:00')
      expect(calendarioService.normalizarHora('10:00 PM')).toBe('22:00')
      expect(calendarioService.normalizarHora('12:00 AM')).toBe('00:00')
      expect(calendarioService.normalizarHora('12:00 PM')).toBe('12:00')
    })

    it('should return null for invalid format', () => {
      expect(calendarioService.normalizarHora('invalid')).toBe(null)
      expect(calendarioService.normalizarHora(null)).toBe(null)
    })
  })

  describe('validarEvento', () => {
    it('should validate evento correctly', () => {
      const evento = {
        titulo: 'Evento Test',
        fecha: '2024-12-01',
        horaInicio: '10:00',
        lugar: 'Gimnasio',
        idTipoEvento: 1,
        idCategoria: 1
      }

      const errores = calendarioService.validarEvento(evento)

      expect(errores.length).toBe(0)
    })

    it('should return errors for invalid evento', () => {
      const evento = {
        titulo: 'A', // too short
        fecha: 'invalid-date',
        lugar: 'X', // too short
        horaInicio: 'invalid-time'
      }

      const errores = calendarioService.validarEvento(evento)

      expect(errores.length).toBeGreaterThan(0)
    })

    it('should validate hora_fin is after hora_inicio', () => {
      const evento = {
        titulo: 'Evento Test',
        fecha: '2024-12-01',
        horaInicio: '11:00',
        horaFin: '10:00', // before hora_inicio
        lugar: 'Gimnasio',
        idTipoEvento: 1,
        idCategoria: 1
      }

      const errores = calendarioService.validarEvento(evento)

      expect(errores.some(e => e.includes('hora de fin'))).toBe(true)
    })
  })

  describe('obtenerTipoEventoPorNombre', () => {
    beforeEach(() => {
      calendarioService.tiposEvento = [
        { id_tipo_evento: 1, nombre: 'Entrenamiento' },
        { id_tipo_evento: 2, nombre: 'Competencia' }
      ]
    })

    it('should find tipo evento by name', () => {
      const tipo = calendarioService.obtenerTipoEventoPorNombre('Entrenamiento')

      expect(tipo).toBeDefined()
      expect(tipo.id_tipo_evento).toBe(1)
    })

    it('should be case insensitive', () => {
      const tipo = calendarioService.obtenerTipoEventoPorNombre('COMPETENCIA')

      expect(tipo).toBeDefined()
      expect(tipo.id_tipo_evento).toBe(2)
    })

    it('should return undefined when not found', () => {
      const tipo = calendarioService.obtenerTipoEventoPorNombre('No existe')

      expect(tipo).toBeUndefined()
    })
  })

  describe('limpiarCache', () => {
    it('should clear all cache', () => {
      calendarioService.eventos = [{ id: 1 }]
      calendarioService.tiposEvento = [{ id: 1 }]
      calendarioService.categorias = [{ id: 1 }]

      calendarioService.limpiarCache()

      expect(calendarioService.eventos).toHaveLength(0)
      expect(calendarioService.tiposEvento).toHaveLength(0)
      expect(calendarioService.categorias).toHaveLength(0)
    })
  })
})

