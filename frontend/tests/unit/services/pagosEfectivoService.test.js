import { describe, it, expect, beforeEach, vi } from 'vitest'
import pagosEfectivoService from '@/services/pagosEfectivoService'

// Mock fetch globally
global.fetch = vi.fn()

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(() => '[]'),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
global.localStorage = localStorageMock

// Mock navigator.geolocation
global.navigator = {
  geolocation: {
    getCurrentPosition: vi.fn((success) => {
      success({
        coords: {
          latitude: 4.6097,
          longitude: -74.0817,
          accuracy: 10
        }
      })
    })
  },
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
  language: 'es-CO',
  cookieEnabled: true
}

describe('PagosEfectivoService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue('[]')
    pagosEfectivoService.pagos = []
  })

  describe('validarDatosPago', () => {
    it('should validate datos pago successfully', () => {
      const datosPago = {
        mensualidadId: 1,
        tipoPago: 'efectivo',
        monto: 50000,
        recibidoDe: 'Juan Pérez',
        documentoPagador: '12345678',
        telefonoPagador: '3001234567'
      }

      expect(() => pagosEfectivoService.validarDatosPago(datosPago)).not.toThrow()
    })

    it('should throw error when required field is missing', () => {
      const datosPago = {
        mensualidadId: 1,
        tipoPago: 'efectivo'
        // Missing required fields
      }

      expect(() => pagosEfectivoService.validarDatosPago(datosPago)).toThrow('Campo requerido')
    })

    it('should throw error when monto is zero or negative', () => {
      const datosPago = {
        mensualidadId: 1,
        tipoPago: 'efectivo',
        monto: 0,
        recibidoDe: 'Juan Pérez',
        documentoPagador: '12345678',
        telefonoPagador: '3001234567'
      }

      expect(() => pagosEfectivoService.validarDatosPago(datosPago)).toThrow('Monto debe ser mayor a 0')
    })

    it('should throw error when monto exceeds limit', () => {
      const datosPago = {
        mensualidadId: 1,
        tipoPago: 'efectivo',
        monto: 10000001, // Exceeds 10 million
        recibidoDe: 'Juan Pérez',
        documentoPagador: '12345678',
        telefonoPagador: '3001234567'
      }

      expect(() => pagosEfectivoService.validarDatosPago(datosPago)).toThrow('Monto excede el límite permitido')
    })
  })

  describe('generarHash', () => {
    it('should generate hash from datos', () => {
      const datos = { monto: 50000, mensualidadId: 1 }
      const hash = pagosEfectivoService.generarHash(datos)

      expect(hash).toBeTruthy()
      expect(typeof hash).toBe('string')
    })

    it('should generate different hashes for same datos at different times', () => {
      const datos = { monto: 50000, mensualidadId: 1 }
      const hash1 = pagosEfectivoService.generarHash(datos)
      
      // Wait a bit to ensure different timestamp
      vi.advanceTimersByTime(1000)
      const hash2 = pagosEfectivoService.generarHash(datos)

      expect(hash1).not.toBe(hash2)
    })
  })

  describe('obtenerUbicacion', () => {
    it('should get location successfully', async () => {
      const ubicacion = await pagosEfectivoService.obtenerUbicacion()

      expect(ubicacion).toHaveProperty('lat')
      expect(ubicacion).toHaveProperty('lng')
      expect(ubicacion).toHaveProperty('precision')
    })

    it('should return null when geolocation is not available', async () => {
      global.navigator.geolocation = undefined

      const ubicacion = await pagosEfectivoService.obtenerUbicacion()

      expect(ubicacion).toBeNull()
    })
  })

  describe('obtenerInfoDispositivo', () => {
    it('should get device info successfully', () => {
      const info = pagosEfectivoService.obtenerInfoDispositivo()

      expect(info).toHaveProperty('userAgent')
      expect(info).toHaveProperty('plataforma')
      expect(info).toHaveProperty('idioma')
      expect(info).toHaveProperty('cookies')
      expect(info).toHaveProperty('timestamp')
    })
  })

  describe('registrarPago', () => {
    it('should register pago successfully', async () => {
      const mockData = {
        success: true,
        comprobante: 'COMP-12345'
      }

      const datosPago = {
        mensualidadId: 1,
        tipoPago: 'efectivo',
        monto: 50000,
        recibidoDe: 'Juan Pérez',
        documentoPagador: '12345678',
        telefonoPagador: '3001234567'
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await pagosEfectivoService.registrarPago(datosPago)

      expect(result.success).toBe(true)
      expect(result.pago).toHaveProperty('timestamp')
      expect(result.pago).toHaveProperty('hash')
      expect(result.comprobante).toBe('COMP-12345')
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/pagos-efectivo'),
        expect.objectContaining({
          method: 'POST'
        })
      )
    })

    it('should handle error when registering pago', async () => {
      const datosPago = {
        mensualidadId: 1,
        tipoPago: 'efectivo',
        monto: 50000,
        recibidoDe: 'Juan Pérez',
        documentoPagador: '12345678',
        telefonoPagador: '3001234567'
      }

      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      })

      const result = await pagosEfectivoService.registrarPago(datosPago)

      expect(result.success).toBe(false)
      expect(result.error).toBeTruthy()
    })
  })

  describe('verificarPago', () => {
    it('should verify pago from local storage', async () => {
      const pagoLocal = {
        codigoRecibo: 'REC-123',
        monto: 50000,
        timestamp: Date.now()
      }

      pagosEfectivoService.pagos = [pagoLocal]

      const result = await pagosEfectivoService.verificarPago('REC-123')

      expect(result.success).toBe(true)
      expect(result.pago).toEqual(pagoLocal)
      expect(result.fuente).toBe('local')
    })

    it('should verify pago from server when not found locally', async () => {
      const mockData = {
        success: true,
        pago: {
          codigoRecibo: 'REC-456',
          monto: 50000
        }
      }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await pagosEfectivoService.verificarPago('REC-456')

      expect(result.success).toBe(true)
      expect(result.pago).toEqual(mockData.pago)
      expect(result.fuente).toBe('servidor')
    })

    it('should handle error when pago not found', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      })

      const result = await pagosEfectivoService.verificarPago('REC-999')

      expect(result.success).toBe(false)
      expect(result.error).toBe('Pago no encontrado')
    })
  })

  describe('cargarPagosLocales', () => {
    it('should load pagos from localStorage', () => {
      const pagos = [
        { codigoRecibo: 'REC-1', monto: 50000 },
        { codigoRecibo: 'REC-2', monto: 60000 }
      ]

      localStorageMock.getItem.mockReturnValue(JSON.stringify(pagos))

      const result = pagosEfectivoService.cargarPagosLocales()

      expect(result).toEqual(pagos)
    })

    it('should return empty array when localStorage is empty', () => {
      localStorageMock.getItem.mockReturnValue(null)

      const result = pagosEfectivoService.cargarPagosLocales()

      expect(result).toEqual([])
    })
  })
})

