import { describe, it, expect, beforeEach, vi } from 'vitest'
import galeriaService from '@/services/galeriaService'

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

describe('GaleriaService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    galeriaService.imagenes = []
    galeriaService.tiposEvento = []
    galeriaService.categorias = []
  })

  describe('getAuthHeaders', () => {
    it('should return headers with authorization token', () => {
      const headers = galeriaService.getAuthHeaders()

      expect(headers).toHaveProperty('Content-Type', 'application/json')
      expect(headers).toHaveProperty('Authorization', 'Bearer mock-token')
    })

    it('should return headers without authorization when token is missing', () => {
      localStorageMock.getItem.mockReturnValueOnce(null)

      const headers = galeriaService.getAuthHeaders()

      expect(headers).toHaveProperty('Content-Type', 'application/json')
      expect(headers.Authorization).toBe('')
    })
  })

  describe('cargarImagenes', () => {
    it('should load imagenes successfully without filters', async () => {
      const mockData = {
        success: true,
        data: [
          { id_galeria: 1, url: 'http://example.com/img1.jpg' },
          { id_galeria: 2, url: 'http://example.com/img2.jpg' }
        ]
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await galeriaService.cargarImagenes()

      expect(result).toEqual(mockData.data)
      expect(galeriaService.imagenes).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/galeria/'),
        expect.objectContaining({
          method: 'GET'
        })
      )
    })

    it('should load imagenes with filters', async () => {
      const mockData = {
        success: true,
        data: [{ id_galeria: 1, id_tipo_evento: 1 }]
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await galeriaService.cargarImagenes({
        id_tipo_evento: 1,
        id_categoria: 2,
        limit: 10
      })

      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/galeria/?id_tipo_evento=1&id_categoria=2&limit=10'),
        expect.any(Object)
      )
    })

    it('should handle 401 authentication error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized'
      })

      await expect(galeriaService.cargarImagenes()).rejects.toThrow('Error de autenticación')
    })

    it('should handle 500 server error', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      })

      await expect(galeriaService.cargarImagenes()).rejects.toThrow('Error interno del servidor')
    })

    it('should return empty array on error', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'))

      const result = await galeriaService.cargarImagenes()

      expect(result).toEqual([])
      expect(galeriaService.imagenes).toEqual([])
    })
  })

  describe('obtenerImagen', () => {
    it('should get imagen by id successfully', async () => {
      const mockData = {
        success: true,
        data: {
          id_galeria: 1,
          url: 'http://example.com/img1.jpg',
          descripcion: 'Imagen de prueba'
        }
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await galeriaService.obtenerImagen(1)

      expect(result).toEqual(mockData.data)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/galeria/1'),
        expect.objectContaining({
          method: 'GET'
        })
      )
    })

    it('should handle error when getting imagen', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      })

      await expect(galeriaService.obtenerImagen(999)).rejects.toThrow('Error al obtener imagen')
    })
  })
})

