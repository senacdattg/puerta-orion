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

      expect(result).toEqual(mockData.data)
      expect(calendarioService.eventos).toEqual(mockData.data)
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

      await expect(calendarioService.cargarEventos()).rejects.toThrow('Error de autenticación')
    })

    it('should handle 404 not found error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({ error: 'Not found' })
      })

      await expect(calendarioService.cargarEventos()).rejects.toThrow('Ruta no encontrada')
    })

    it('should handle 500 server error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ error: 'Server error', stack: 'Error stack' })
      })

      await expect(calendarioService.cargarEventos()).rejects.toThrow('Error interno del servidor')
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

      expect(result).toEqual([])
      expect(calendarioService.tiposEvento).toHaveLength(3) // Fallback data
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
})

