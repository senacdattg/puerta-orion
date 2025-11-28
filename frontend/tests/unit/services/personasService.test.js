import { describe, it, expect, beforeEach, vi } from 'vitest'
import personasService from '@/services/personasService'

// Mock fetch globally
globalThis.fetch = vi.fn()

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

describe('PersonasService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getAuthHeaders', () => {
    it('should return headers with authorization token when token exists', () => {
      const headers = personasService.getAuthHeaders()

      expect(headers).toHaveProperty('Content-Type', 'application/json')
      expect(headers).toHaveProperty('Authorization', 'Bearer mock-token-123')
    })

    it('should return headers without authorization when token is missing', async () => {
      const { useAuthStore } = await import('@/stores/auth')
      vi.mocked(useAuthStore).mockReturnValueOnce({
        token: null
      })

      const headers = personasService.getAuthHeaders()

      expect(headers).toHaveProperty('Content-Type', 'application/json')
      expect(headers).not.toHaveProperty('Authorization')
    })
  })

  describe('actualizarPersona', () => {
    it('should update persona successfully', async () => {
      const mockData = {
        success: true,
        data: {
          id_persona: 1,
          primer_nombre: 'Juan',
          primer_apellido: 'Pérez'
        },
        message: 'Persona actualizada exitosamente'
      }

      const datosActualizacion = {
        primer_nombre: 'Juan',
        correo_electronico: 'juan@example.com'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await personasService.actualizarPersona(1, datosActualizacion)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/personas/1'),
        expect.objectContaining({
          method: 'PUT',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify(datosActualizacion)
        })
      )
    })

    it('should throw error when idPersona is invalid', async () => {
      await expect(
        personasService.actualizarPersona(null, { primer_nombre: 'Juan' })
      ).rejects.toThrow('Id de persona inválido')

      await expect(
        personasService.actualizarPersona(0, { primer_nombre: 'Juan' })
      ).rejects.toThrow('Id de persona inválido')
    })

    it('should throw error when datos is empty', async () => {
      await expect(
        personasService.actualizarPersona(1, {})
      ).rejects.toThrow('No hay datos para actualizar persona')

      await expect(
        personasService.actualizarPersona(1, null)
      ).rejects.toThrow('No hay datos para actualizar persona')
    })

    it('should handle error response from server', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          error: 'Datos inválidos',
          message: 'El correo electrónico ya está en uso'
        })
      })

      await expect(
        personasService.actualizarPersona(1, { correo_electronico: 'test@example.com' })
      ).rejects.toThrow('Datos inválidos')
    })

    it('should handle non-JSON error response', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => {
          throw new Error('Invalid JSON')
        }
      })

      await expect(
        personasService.actualizarPersona(1, { primer_nombre: 'Juan' })
      ).rejects.toThrow('Error al actualizar persona')
    })
  })
})

