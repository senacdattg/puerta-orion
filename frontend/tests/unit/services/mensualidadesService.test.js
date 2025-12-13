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

      try {
        await mensualidadesService.list()
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Server error')
        expect(error.status).toBe(500)
      }
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

      try {
        await mensualidadesService.get(999)
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Not found')
        expect(error.status).toBe(404)
      }
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

      try {
        await mensualidadesService.create({})
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Invalid data')
        expect(error.status).toBe(400)
      }
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

    it('should handle error when deactivating mensualidad', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: async () => 'Mensualidad no encontrada'
      })

      try {
        await mensualidadesService.desactivar(999)
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Mensualidad no encontrada')
        expect(error.status).toBe(404)
      }
    })
  })

  describe('reactivar', () => {
    it('should reactivate mensualidad successfully', async () => {
      const mockData = {
        success: true,
        message: 'Mensualidad reactivada'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.reactivar(1)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/mensualidades/1/reactivar'),
        expect.objectContaining({
          method: 'PATCH'
        })
      )
    })

    it('should handle error when reactivating mensualidad', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: async () => 'Mensualidad no encontrada'
      })

      try {
        await mensualidadesService.reactivar(999)
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Mensualidad no encontrada')
        expect(error.status).toBe(404)
      }
    })
  })

  describe('buscarPersonaPorDocumento', () => {
    it('should search person by document successfully', async () => {
      const mockData = {
        success: true,
        data: {
          id_persona: 1,
          documento: '12345678',
          nombre_completo: 'Juan Pérez'
        }
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.buscarPersonaPorDocumento('12345678')

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/mensualidades/buscar-persona?documento=12345678'),
        expect.any(Object)
      )
    })

    it('should search person without document parameter', async () => {
      const mockData = {
        success: true,
        data: []
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.buscarPersonaPorDocumento()

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/mensualidades/buscar-persona'),
        expect.any(Object)
      )
    })

    it('should handle error when searching person', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: async () => 'Persona no encontrada'
      })

      try {
        await mensualidadesService.buscarPersonaPorDocumento('99999999')
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Persona no encontrada')
        expect(error.status).toBe(404)
      }
    })
  })

  describe('abonar', () => {
    it('should register payment successfully with all parameters', async () => {
      const mockData = {
        success: true,
        data: {
          id_abono: 1,
          monto_abonado: 30000,
          fecha_abono: '2024-12-15',
          id_metodo_pago: 1
        }
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.abonar(1, {
        monto_abonado: 30000,
        fecha_abono: '2024-12-15',
        id_metodo_pago: 1
      })

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/mensualidades/1/abonar'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            monto_abonado: 30000,
            fecha_abono: '2024-12-15',
            id_metodo_pago: 1
          })
        })
      )
    })

    it('should register payment with only monto_abonado', async () => {
      const mockData = {
        success: true,
        data: { id_abono: 1, monto_abonado: 30000 }
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.abonar(1, {
        monto_abonado: 30000
      })

      expect(result).toEqual(mockData)
      const callArgs = globalThis.fetch.mock.calls[0]
      const body = JSON.parse(callArgs[1].body)
      expect(body).toEqual({ monto_abonado: 30000 })
      expect(body.fecha_abono).toBeUndefined()
      expect(body.id_metodo_pago).toBeUndefined()
    })

    it('should register payment with id_metodo_pago as 0', async () => {
      const mockData = {
        success: true,
        data: { id_abono: 1, monto_abonado: 30000, id_metodo_pago: 0 }
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.abonar(1, {
        monto_abonado: 30000,
        id_metodo_pago: 0
      })

      expect(result).toEqual(mockData)
      const callArgs = globalThis.fetch.mock.calls[0]
      const body = JSON.parse(callArgs[1].body)
      expect(body.id_metodo_pago).toBe(0)
    })

    it('should handle error when registering payment', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: async () => 'Monto excede saldo pendiente'
      })

      try {
        await mensualidadesService.abonar(1, { monto_abonado: 100000 })
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Monto excede saldo pendiente')
        expect(error.status).toBe(400)
      }
    })
  })

  describe('listarAbonos', () => {
    it('should list abonos successfully', async () => {
      const mockData = {
        success: true,
        data: [
          { id_abono: 1, monto_abonado: 30000, fecha_abono: '2024-12-15' },
          { id_abono: 2, monto_abonado: 20000, fecha_abono: '2024-12-20' }
        ]
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.listarAbonos(1)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/mensualidades/1/abonos'),
        expect.any(Object)
      )
    })

    it('should handle error when listing abonos', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: async () => 'Mensualidad no encontrada'
      })

      try {
        await mensualidadesService.listarAbonos(999)
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Mensualidad no encontrada')
        expect(error.status).toBe(404)
      }
    })
  })

  describe('updateAbono', () => {
    it('should update abono successfully', async () => {
      const mockData = {
        success: true,
        data: {
          id_abono: 1,
          monto_abonado: 35000,
          fecha_abono: '2024-12-16'
        }
      }

      const payload = {
        monto_abonado: 35000,
        fecha_abono: '2024-12-16'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.updateAbono(1, 1, payload)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/mensualidades/1/abonos/1'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(payload)
        })
      )
    })

    it('should handle error when updating abono', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: async () => 'Abono no encontrado'
      })

      try {
        await mensualidadesService.updateAbono(1, 999, { monto_abonado: 35000 })
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Abono no encontrado')
        expect(error.status).toBe(404)
      }
    })
  })

  describe('deleteAbono', () => {
    it('should delete abono successfully', async () => {
      const mockData = {
        success: true,
        message: 'Abono eliminado'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.deleteAbono(1, 1)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/mensualidades/1/abonos/1'),
        expect.objectContaining({
          method: 'DELETE'
        })
      )
    })

    it('should handle error when deleting abono', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: async () => 'Abono no encontrado'
      })

      try {
        await mensualidadesService.deleteAbono(1, 999)
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Abono no encontrado')
        expect(error.status).toBe(404)
      }
    })
  })

  describe('crearPreferenciaMensualidad', () => {
    it('should create Mercado Pago preference successfully', async () => {
      const mockData = {
        success: true,
        data: {
          preference_id: 'pref_123456',
          init_point: 'https://www.mercadopago.com/checkout/v1/redirect'
        }
      }

      const args = {
        mensualidad_id: 1,
        monto: 50000
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.crearPreferenciaMensualidad(args)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/mercadopago/crear-preferencia'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            tipo_pago: 'mensualidad',
            ...args
          })
        })
      )
    })

    it('should handle error when creating preference', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: async () => 'Error al crear preferencia'
      })

      try {
        await mensualidadesService.crearPreferenciaMensualidad({})
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Error al crear preferencia')
        expect(error.status).toBe(400)
      }
    })
  })

  describe('_request error handling', () => {
    it('should handle error with JSON error response (errorData.error)', async () => {
      const errorJson = JSON.stringify({ error: 'Custom error message' })

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: async () => errorJson
      })

      try {
        await mensualidadesService.get(1)
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Custom error message')
        expect(error.status).toBe(400)
      }
    })

    it('should handle error with JSON error response (errorData.message)', async () => {
      const errorJson = JSON.stringify({ message: 'Error message from backend' })

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => errorJson
      })

      try {
        await mensualidadesService.get(1)
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Error message from backend')
        expect(error.status).toBe(500)
      }
    })

    it('should handle error with invalid JSON but valid text', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => 'Not valid JSON but has text'
      })

      try {
        await mensualidadesService.get(1)
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Not valid JSON but has text')
        expect(error.status).toBe(500)
      }
    })

    it('should handle error with empty text response', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => '   ' // Only whitespace
      })

      try {
        await mensualidadesService.get(1)
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('500 Internal Server Error')
        expect(error.status).toBe(500)
      }
    })

    it('should handle error when cannot read response text', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => {
          throw new Error('Cannot read response')
        }
      })

      try {
        await mensualidadesService.get(1)
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('500 Internal Server Error')
        expect(error.status).toBe(500)
      }
    })

    it('should handle network error', async () => {
      const networkError = new Error('Network error')
      globalThis.fetch.mockRejectedValueOnce(networkError)

      try {
        await mensualidadesService.get(1)
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error).toBe(networkError)
      }
    })

    it('should handle error when JSON parsing fails in success response', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON')
        }
      })

      try {
        await mensualidadesService.get(1)
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Invalid JSON')
      }
    })
  })

  describe('list edge cases', () => {
    it('should handle null and undefined parameters', async () => {
      const mockData = { success: true, data: [] }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.list({
        persona_id: null,
        estado: undefined,
        activo: null
      })

      expect(result).toEqual(mockData)
      const callUrl = globalThis.fetch.mock.calls[0][0]
      expect(callUrl).not.toContain('persona_id')
      expect(callUrl).not.toContain('estado')
      expect(callUrl).not.toContain('activo')
    })

    it('should handle empty params object', async () => {
      const mockData = { success: true, data: [] }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await mensualidadesService.list({})

      expect(result).toEqual(mockData)
      const callUrl = globalThis.fetch.mock.calls[0][0]
      expect(callUrl).toBe('http://localhost:5000/api/mensualidades')
    })
  })

  describe('update edge cases', () => {
    it('should handle error when updating mensualidad', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: async () => 'Mensualidad no encontrada'
      })

      try {
        await mensualidadesService.update(999, { estado: 'pagado' })
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error.message).toBe('Mensualidad no encontrada')
        expect(error.status).toBe(404)
      }
    })
  })

  describe('authentication', () => {
    it('should make request without token when getToken returns undefined', async () => {
      const authService = await import('@/services/authService')
      authService.default.getToken.mockReturnValueOnce(undefined)

      const mockData = { success: true, data: [] }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      await mensualidadesService.list()

      const callArgs = globalThis.fetch.mock.calls[0]
      expect(callArgs[1].headers.Authorization).toBeUndefined()
    })

    it('should make request without token when getToken returns null', async () => {
      const authService = await import('@/services/authService')
      authService.default.getToken.mockReturnValueOnce(null)

      const mockData = { success: true, data: [] }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      await mensualidadesService.list()

      const callArgs = globalThis.fetch.mock.calls[0]
      expect(callArgs[1].headers.Authorization).toBeUndefined()
    })
  })
})

