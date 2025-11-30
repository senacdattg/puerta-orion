import { describe, it, expect, beforeEach, vi } from 'vitest'
import mensualidadesService from '@/services/mensualidadesService'

// Mock fetch globally
globalThis.fetch = vi.fn()

// Mock authService
vi.mock('@/services/authService', () => ({
  default: {
    getToken: vi.fn(() => 'mock-token-123')
  }
}))

// Mock API_CONFIG
vi.mock('@/config/environment', () => ({
  API_CONFIG: {
    baseURL: 'http://localhost:5000'
  }
}))

describe('MensualidadesApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('list', () => {
    it('should list mensualidades successfully without filters', async () => {
      const mockData = {
        success: true,
        data: [
          { id_mensualidad: 1, monto: 50000, estado: 'pendiente' },
          { id_mensualidad: 2, monto: 50000, estado: 'pagado' }
        ]
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.list()

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/mensualidades'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      )
    })

    it('should list mensualidades with filters', async () => {
      const mockData = {
        success: true,
        data: [{ id_mensualidad: 1, estado: 'pendiente' }]
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.list({
        persona_id: 1,
        estado: 'pendiente',
        page: 1
      })

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/mensualidades?persona_id=1&estado=pendiente&page=1'),
        expect.any(Object)
      )
    })

    it('should handle error when listing mensualidades', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => 'Server error'
      })

      await expect(mensualidadesService.list()).rejects.toThrow('500')
    })
  })

  describe('get', () => {
    it('should get mensualidad by id successfully', async () => {
      const mockData = {
        success: true,
        data: {
          id_mensualidad: 1,
          monto: 50000,
          estado: 'pendiente'
        }
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.get(1)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/mensualidades/1'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      )
    })

    it('should handle error when getting mensualidad', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: async () => 'Not found'
      })

      await expect(mensualidadesService.get(999)).rejects.toThrow('404')
    })
  })

  describe('create', () => {
    it('should create mensualidad successfully', async () => {
      const mockData = {
        success: true,
        data: { id_mensualidad: 1, monto: 50000 }
      }

      const payload = {
        persona_id: 1,
        monto: 50000,
        fecha_vencimiento: '2024-12-31'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.create(payload)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/mensualidades'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(payload)
        })
      )
    })

    it('should handle error when creating mensualidad', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: async () => 'Invalid data'
      })

      await expect(mensualidadesService.create({})).rejects.toThrow('400')
    })
  })

  describe('update', () => {
    it('should update mensualidad successfully', async () => {
      const mockData = {
        success: true,
        data: { id_mensualidad: 1, estado: 'pagado' }
      }

      const payload = { estado: 'pagado' }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.update(1, payload)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/mensualidades/1'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(payload)
        })
      )
    })
  })

  describe('desactivar', () => {
    it('should deactivate mensualidad successfully', async () => {
      const mockData = {
        success: true,
        message: 'Mensualidad desactivada'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.desactivar(1)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/mensualidades/1/desactivar'),
        expect.objectContaining({
          method: 'PATCH'
        })
      )
    })
  })
})

