import { describe, it, expect, beforeEach, vi } from 'vitest'
import deportistasService from '@/services/deportistasService'

// Mock fetch globally
global.fetch = vi.fn()

// Mock stores
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    token: 'mock-token-123'
  }))
}))

// Mock environment config
vi.mock('@/config/environment', () => ({
  getApiBaseUrl: vi.fn(() => 'http://localhost:5000/api')
}))

describe('DeportistasService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getAuthHeaders', () => {
    it('should return headers with authorization token', () => {
      const headers = deportistasService.getAuthHeaders()

      expect(headers).toHaveProperty('Content-Type', 'application/json')
      expect(headers).toHaveProperty('Authorization', 'Bearer mock-token-123')
    })
  })

  describe('listarDeportistas', () => {
    it('should list deportistas successfully with default pagination', async () => {
      const mockData = {
        success: true,
        data: [
          { id_deportista: 1, nombre: 'Juan Pérez' },
          { id_deportista: 2, nombre: 'María García' }
        ],
        pagination: { page: 1, per_page: 100, total: 2 }
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await deportistasService.listarDeportistas()

      expect(result).toEqual(mockData)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/deportistas?page=1&per_page=100'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      )
    })

    it('should list deportistas with custom pagination', async () => {
      const mockData = {
        success: true,
        data: [],
        pagination: { page: 2, per_page: 10, total: 0 }
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await deportistasService.listarDeportistas(2, 10)

      expect(result).toEqual(mockData)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/deportistas?page=2&per_page=10'),
        expect.any(Object)
      )
    })

    it('should handle error when listing deportistas', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      })

      await expect(deportistasService.listarDeportistas()).rejects.toThrow('Error 500')
    })
  })

  describe('obtenerDeportistaPorId', () => {
    it('should get deportista by id successfully', async () => {
      const mockData = {
        success: true,
        data: {
          id_deportista: 1,
          nombre: 'Juan Pérez',
          categoria: 'Pre-infantil'
        }
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await deportistasService.obtenerDeportistaPorId(1)

      expect(result.success).toBe(true)
      expect(result.data.id_deportista).toBe(1)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/deportistas/1'),
        expect.objectContaining({
          method: 'GET'
        })
      )
    })

    it('should normalize response with status to success', async () => {
      const mockData = {
        status: 'success',
        data: { id_deportista: 1 }
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await deportistasService.obtenerDeportistaPorId(1)

      expect(result.success).toBe(true)
      expect(result.status).toBe('success')
    })

    it('should handle error when getting deportista', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      })

      await expect(deportistasService.obtenerDeportistaPorId(999)).rejects.toThrow('Error 404')
    })
  })
})

