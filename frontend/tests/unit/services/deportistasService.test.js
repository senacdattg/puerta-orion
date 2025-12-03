import { describe, it, expect, beforeEach, vi } from 'vitest'
import deportistasService from '@/services/deportistasService'

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

    it('should return headers without authorization when token is null', async () => {
      const { useAuthStore } = await import('@/stores/auth')
      useAuthStore.mockReturnValueOnce({
        token: null
      })

      const headers = deportistasService.getAuthHeaders()

      expect(headers).toHaveProperty('Content-Type', 'application/json')
      expect(headers).toHaveProperty('Authorization', '')
    })

    it('should return headers without authorization when token is undefined', async () => {
      const { useAuthStore } = await import('@/stores/auth')
      useAuthStore.mockReturnValueOnce({
        token: undefined
      })

      const headers = deportistasService.getAuthHeaders()

      expect(headers).toHaveProperty('Content-Type', 'application/json')
      expect(headers).toHaveProperty('Authorization', '')
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

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await deportistasService.listarDeportistas()

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
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

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await deportistasService.listarDeportistas(2, 10)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/deportistas?page=2&per_page=10'),
        expect.any(Object)
      )
    })

    it('should handle error when listing deportistas', async () => {
      globalThis.fetch.mockResolvedValueOnce({
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

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await deportistasService.obtenerDeportistaPorId(1)

      expect(result.success).toBe(true)
      expect(result.data.id_deportista).toBe(1)
      expect(globalThis.fetch).toHaveBeenCalledWith(
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

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await deportistasService.obtenerDeportistaPorId(1)

      expect(result.success).toBe(true)
      expect(result.status).toBe('success')
    })

    it('should handle error when getting deportista', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      })

      await expect(deportistasService.obtenerDeportistaPorId(999)).rejects.toThrow('Error 404')
    })

    it('should handle network error when getting deportista', async () => {
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(deportistasService.obtenerDeportistaPorId(1)).rejects.toThrow('Network error')
      expect(consoleError).toHaveBeenCalled()

      consoleError.mockRestore()
    })
  })

  describe('actualizarDeportista', () => {
    it('should update deportista successfully with formatted data', async () => {
      const mockData = {
        success: true,
        message: 'Deportista actualizado exitosamente'
      }

      const datosEnvio = {
        datos_deportista: { nombre: 'Juan' },
        datos_informacion_deportiva: { peso: 70 }
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await deportistasService.actualizarDeportista(1, datosEnvio)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/deportistas/1'),
        expect.objectContaining({
          method: 'PUT',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify(datosEnvio)
        })
      )
    })

    it('should update deportista with plain data object', async () => {
      const mockData = {
        success: true,
        message: 'Deportista actualizado'
      }

      const datosPlain = {
        nombre: 'Juan',
        peso: 70
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await deportistasService.actualizarDeportista(1, datosPlain)

      expect(result).toEqual(mockData)
      const callBody = JSON.parse(globalThis.fetch.mock.calls[0][1].body)
      expect(callBody).toHaveProperty('datos_deportista')
      expect(callBody).toHaveProperty('datos_informacion_deportiva')
    })

    it('should handle error when updating deportista', async () => {
      const errorData = {
        message: 'Error de validación'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => errorData
      })

      await expect(
        deportistasService.actualizarDeportista(1, { nombre: 'Juan' })
      ).rejects.toThrow('Error de validación')
    })

    it('should handle error without message when updating deportista', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({})
      })

      await expect(
        deportistasService.actualizarDeportista(1, { nombre: 'Juan' })
      ).rejects.toThrow('Error 500')
    })

    it('should handle error when response.json() fails during update', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => {
          throw new Error('Parse error')
        }
      })

      await expect(
        deportistasService.actualizarDeportista(1, { nombre: 'Juan' })
      ).rejects.toThrow('Error 500')
    })

    it('should handle network error when updating deportista', async () => {
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(
        deportistasService.actualizarDeportista(1, { nombre: 'Juan' })
      ).rejects.toThrow('Network error')
      expect(consoleError).toHaveBeenCalled()

      consoleError.mockRestore()
    })
  })

  describe('crearDeportista', () => {
    it('should create deportista successfully', async () => {
      const mockData = {
        success: true,
        data: {
          id_deportista: 1,
          nombre: 'Nuevo Deportista'
        }
      }

      const datos = {
        nombre: 'Nuevo Deportista',
        categoria: 'Pre-infantil'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await deportistasService.crearDeportista(datos)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/deportistas'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify(datos)
        })
      )
    })

    it('should handle error when creating deportista', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request'
      })

      await expect(
        deportistasService.crearDeportista({ nombre: 'Test' })
      ).rejects.toThrow('Error 400')
    })

    it('should handle network error when creating deportista', async () => {
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(
        deportistasService.crearDeportista({ nombre: 'Test' })
      ).rejects.toThrow('Network error')
      expect(consoleError).toHaveBeenCalled()

      consoleError.mockRestore()
    })
  })

  describe('eliminarDeportista', () => {
    it('should delete deportista successfully', async () => {
      const mockData = {
        success: true,
        message: 'Deportista eliminado exitosamente'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await deportistasService.eliminarDeportista(1)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/deportistas/1'),
        expect.objectContaining({
          method: 'DELETE',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      )
    })

    it('should handle error when deleting deportista', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      })

      await expect(deportistasService.eliminarDeportista(999)).rejects.toThrow('Error 404')
    })

    it('should handle network error when deleting deportista', async () => {
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(deportistasService.eliminarDeportista(1)).rejects.toThrow('Network error')
      expect(consoleError).toHaveBeenCalled()

      consoleError.mockRestore()
    })
  })

  describe('buscarDeportistaPorDocumentoParaAcudiente', () => {
    it('should search deportista by document successfully', async () => {
      const mockData = {
        success: true,
        data: {
          id_deportista: 1,
          nombre: 'Juan Pérez',
          documento: '12345678'
        }
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        text: async () => JSON.stringify(mockData)
      })

      const consoleLog = vi.spyOn(console, 'log').mockImplementation(() => {})

      const result = await deportistasService.buscarDeportistaPorDocumentoParaAcudiente('12345678')

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/deportistas/acudientes/buscar-deportista?documento=12345678'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      )

      consoleLog.mockRestore()
    })

    it('should search deportista without document parameter', async () => {
      const mockData = {
        success: true,
        data: []
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        text: async () => JSON.stringify(mockData)
      })

      const result = await deportistasService.buscarDeportistaPorDocumentoParaAcudiente(null)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/deportistas/acudientes/buscar-deportista'),
        expect.any(Object)
      )
    })

    it('should handle error response with error field', async () => {
      const errorData = {
        error: 'Deportista no encontrado'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: async () => JSON.stringify(errorData)
      })

      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      try {
        await deportistasService.buscarDeportistaPorDocumentoParaAcudiente('12345678')
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Deportista no encontrado')
        expect(error.status).toBe(404)
      }

      consoleError.mockRestore()
    })

    it('should handle error response with message field', async () => {
      const errorData = {
        message: 'No se encontró el deportista'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: async () => JSON.stringify(errorData)
      })

      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      try {
        await deportistasService.buscarDeportistaPorDocumentoParaAcudiente('12345678')
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('No se encontró el deportista')
      }

      consoleError.mockRestore()
    })

    it('should handle error response with error object', async () => {
      const errorData = {
        error: { detail: 'Invalid document' }
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: async () => JSON.stringify(errorData)
      })

      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      try {
        await deportistasService.buscarDeportistaPorDocumentoParaAcudiente('123')
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toContain('Invalid document')
      }

      consoleError.mockRestore()
    })

    it('should handle error response without error or message fields', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => '{}'
      })

      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})

      try {
        await deportistasService.buscarDeportistaPorDocumentoParaAcudiente('12345678')
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Error 500: Internal Server Error')
      }

      consoleError.mockRestore()
    })

    it('should handle empty response text', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        text: async () => ''
      })

      const consoleLog = vi.spyOn(console, 'log').mockImplementation(() => {})

      const result = await deportistasService.buscarDeportistaPorDocumentoParaAcudiente('12345678')

      expect(result).toEqual({})
      consoleLog.mockRestore()
    })

    it('should handle invalid JSON response', async () => {
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        text: async () => 'invalid json{'
      })

      const result = await deportistasService.buscarDeportistaPorDocumentoParaAcudiente('12345678')

      expect(result).toEqual({})
      expect(consoleError).toHaveBeenCalled()

      consoleError.mockRestore()
    })

    it('should handle network error', async () => {
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(
        deportistasService.buscarDeportistaPorDocumentoParaAcudiente('12345678')
      ).rejects.toThrow('Network error')
      expect(consoleError).toHaveBeenCalled()

      consoleError.mockRestore()
    })

    it('should handle listarDeportistas network error', async () => {
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(deportistasService.listarDeportistas()).rejects.toThrow('Network error')
      expect(consoleError).toHaveBeenCalled()

      consoleError.mockRestore()
    })
  })
})

