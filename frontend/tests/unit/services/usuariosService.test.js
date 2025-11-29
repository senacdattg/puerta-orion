import { describe, it, expect, beforeEach, vi } from 'vitest'
import usuariosService from '@/services/usuariosService'

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

describe('UsuariosService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getAuthHeaders', () => {
    it('should return headers with authorization token', () => {
      const headers = usuariosService.getAuthHeaders()

      expect(headers).toHaveProperty('Content-Type', 'application/json')
      expect(headers).toHaveProperty('Authorization', 'Bearer mock-token-123')
    })

    it('should return headers without authorization when token is missing', async () => {
      const { useAuthStore } = await import('@/stores/auth')
      vi.mocked(useAuthStore).mockReturnValueOnce({
        token: null
      })

      const headers = usuariosService.getAuthHeaders()

      expect(headers).toHaveProperty('Content-Type', 'application/json')
      expect(headers.Authorization).toBe('')
    })
  })

  describe('listarUsuarios', () => {
    it('should list usuarios successfully with default parameters', async () => {
      const mockData = {
        success: true,
        data: [
          { id_usuario: 1, usuario: 'admin', estado: true },
          { id_usuario: 2, usuario: 'user1', estado: true }
        ]
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await usuariosService.listarUsuarios()

      expect(result).toEqual(mockData)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/usuarios?limit=3&offset=0'),
        expect.objectContaining({
          method: 'GET'
        })
      )
    })

    it('should list usuarios with custom filters', async () => {
      const mockData = {
        success: true,
        data: [{ id_usuario: 1, usuario: 'admin', estado: true }]
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await usuariosService.listarUsuarios('activo', 10, 5)

      expect(result).toEqual(mockData)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/usuarios?estado=activo&limit=10&offset=5'),
        expect.any(Object)
      )
    })

    it('should not include estado parameter when estado is "todos"', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: [] })
      })

      await usuariosService.listarUsuarios('todos', 5, 0)

      expect(global.fetch).toHaveBeenCalledWith(
        expect.not.stringContaining('estado='),
        expect.any(Object)
      )
    })

    it('should handle error when listing usuarios', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      })

      await expect(usuariosService.listarUsuarios()).rejects.toThrow('Error 500')
    })
  })

  describe('listarRoles', () => {
    it('should list roles successfully', async () => {
      const mockData = {
        success: true,
        data: [
          { id_rol: 1, nombre_rol: 'admin' },
          { id_rol: 2, nombre_rol: 'usuario' }
        ]
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await usuariosService.listarRoles()

      expect(result).toEqual(mockData)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/dynamic-data/roles'),
        expect.objectContaining({
          method: 'GET'
        })
      )
    })

    it('should handle error when listing roles', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 403,
        statusText: 'Forbidden'
      })

      await expect(usuariosService.listarRoles()).rejects.toThrow('Error 403')
    })
  })
})

