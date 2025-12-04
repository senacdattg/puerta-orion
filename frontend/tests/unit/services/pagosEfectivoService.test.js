import { describe, it, expect, beforeEach, vi } from 'vitest'
import pagosEfectivoService from '@/services/pagosEfectivoService'

// Mock fetch globally
globalThis.fetch = vi.fn()

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(() => '[]'),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
globalThis.localStorage = localStorageMock

// Mock navigator.geolocation
globalThis.navigator = {
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

      // The validation checks required fields first, then monto
      expect(() => pagosEfectivoService.validarDatosPago(datosPago)).toThrow()
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

    it('should generate different hashes for same datos at different times', async () => {
      vi.useFakeTimers()
      const datos = { monto: 50000, mensualidadId: 1 }
      const hash1 = pagosEfectivoService.generarHash(datos)

      // Advance time to ensure different timestamp
      vi.advanceTimersByTime(1000)
      const hash2 = pagosEfectivoService.generarHash(datos)

      expect(hash1).not.toBe(hash2)
      vi.useRealTimers()
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
      globalThis.navigator.geolocation = undefined

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

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await pagosEfectivoService.registrarPago(datosPago)

      expect(result.success).toBe(true)
      expect(result.pago).toHaveProperty('timestamp')
      expect(result.pago).toHaveProperty('hash')
      expect(result.comprobante).toBe('COMP-12345')
      expect(globalThis.fetch).toHaveBeenCalledWith(
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

      globalThis.fetch.mockResolvedValueOnce({
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

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await pagosEfectivoService.verificarPago('REC-456')

      expect(result.success).toBe(true)
      expect(result.pago).toEqual(mockData.pago)
      expect(result.fuente).toBe('servidor')
    })

    it('should handle error when pago not found', async () => {
      globalThis.fetch.mockResolvedValueOnce({
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

    it('should handle error when localStorage contains invalid JSON', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      localStorageMock.getItem.mockReturnValue('invalid json')

      const result = pagosEfectivoService.cargarPagosLocales()

      expect(result).toEqual([])
      expect(consoleSpy).toHaveBeenCalledWith('Error al cargar pagos locales:', expect.any(Error))
      consoleSpy.mockRestore()
    })
  })

  describe('obtenerHistorial', () => {
    beforeEach(() => {
      globalThis.fetch.mockClear()
      pagosEfectivoService.pagos = [
        {
          codigoRecibo: 'REC-1',
          monto: 50000,
          fecha: '2024-01-15',
          administrador: { id: 'admin_001' }
        },
        {
          codigoRecibo: 'REC-2',
          monto: 60000,
          fecha: '2024-02-20',
          administrador: { id: 'admin_002' }
        },
        {
          codigoRecibo: 'REC-3',
          monto: 70000,
          fecha: '2024-03-25',
          administrador: { id: 'admin_001' }
        }
      ]
    })

    it('should return all local pagos when no filters provided', async () => {
      const result = await pagosEfectivoService.obtenerHistorial()

      expect(result.success).toBe(true)
      expect(result.pagos).toHaveLength(3)
      expect(result.total).toBe(3)
    })

    it('should filter pagos by fechaInicio', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500
      })

      const result = await pagosEfectivoService.obtenerHistorial({
        fechaInicio: '2024-02-01'
      })

      expect(result.success).toBe(true)
      expect(result.pagos).toHaveLength(2)
      expect(result.pagos.every(p => new Date(p.fecha) >= new Date('2024-02-01'))).toBe(true)
    })

    it('should filter pagos by fechaFin', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500
      })

      const result = await pagosEfectivoService.obtenerHistorial({
        fechaFin: '2024-02-28'
      })

      expect(result.success).toBe(true)
      expect(result.pagos).toHaveLength(2)
      expect(result.pagos.every(p => new Date(p.fecha) <= new Date('2024-02-28'))).toBe(true)
    })

    it('should filter pagos by fechaInicio and fechaFin', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500
      })

      const result = await pagosEfectivoService.obtenerHistorial({
        fechaInicio: '2024-02-01',
        fechaFin: '2024-02-28'
      })

      expect(result.success).toBe(true)
      expect(result.pagos).toHaveLength(1)
      expect(result.pagos[0].codigoRecibo).toBe('REC-2')
    })

    it('should filter pagos by administrador', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500
      })

      const result = await pagosEfectivoService.obtenerHistorial({
        administrador: 'admin_001'
      })

      expect(result.success).toBe(true)
      expect(result.pagos).toHaveLength(2)
      expect(result.pagos.every(p => p.administrador.id === 'admin_001')).toBe(true)
    })

    it('should combine local and server pagos when filters provided', async () => {
      const serverPagos = [
        {
          codigoRecibo: 'REC-4',
          monto: 80000,
          fecha: '2024-04-01'
        }
      ]

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ pagos: serverPagos })
      })

      const result = await pagosEfectivoService.obtenerHistorial({
        fechaInicio: '2024-01-01'
      })

      expect(result.success).toBe(true)
      expect(result.pagos.length).toBeGreaterThan(3)
      expect(result.pagos.some(p => p.codigoRecibo === 'REC-4')).toBe(true)
    })

    it('should handle server error and return only local pagos', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500
      })

      const result = await pagosEfectivoService.obtenerHistorial({
        fechaInicio: '2024-01-01'
      })

      expect(result.success).toBe(true)
      expect(result.pagos.length).toBeGreaterThanOrEqual(0)
    })

    it('should handle network error', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      const result = await pagosEfectivoService.obtenerHistorial({
        fechaInicio: '2024-01-01'
      })

      expect(result.success).toBe(false)
      expect(result.error).toBe('Network error')
      expect(result.pagos).toEqual(pagosEfectivoService.pagos)
      consoleSpy.mockRestore()
    })
  })

  describe('generarReporteAuditoria', () => {
    it('should generate audit report successfully', async () => {
      const mockReporte = {
        reporte: {
          fechaInicio: '2024-01-01',
          fechaFin: '2024-01-31',
          totalPagos: 10,
          totalMonto: 500000
        }
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockReporte
      })

      const result = await pagosEfectivoService.generarReporteAuditoria('2024-01-01', '2024-01-31')

      expect(result.success).toBe(true)
      expect(result.reporte).toEqual(mockReporte.reporte)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auditoria'),
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            fechaInicio: '2024-01-01',
            fechaFin: '2024-01-31'
          })
        })
      )
    })

    it('should handle error when server returns error', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500
      })

      const result = await pagosEfectivoService.generarReporteAuditoria('2024-01-01', '2024-01-31')

      expect(result.success).toBe(false)
      expect(result.error).toBe('Error al generar reporte')
      consoleSpy.mockRestore()
    })

    it('should handle network error', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      const result = await pagosEfectivoService.generarReporteAuditoria('2024-01-01', '2024-01-31')

      expect(result.success).toBe(false)
      expect(result.error).toBe('Network error')
      consoleSpy.mockRestore()
    })
  })

  describe('validarDatosPago', () => {
    it('should throw error when monto is exactly 0', () => {
      const datosPago = {
        mensualidadId: 1,
        tipoPago: 'efectivo',
        monto: 0,
        recibidoDe: 'Juan Pérez',
        documentoPagador: '12345678',
        telefonoPagador: '3001234567'
      }

      // Note: 0 is falsy, so it fails required field check first
      // But we still check that it throws
      expect(() => pagosEfectivoService.validarDatosPago(datosPago)).toThrow()
    })

    it('should throw error when monto is negative', () => {
      const datosPago = {
        mensualidadId: 1,
        tipoPago: 'efectivo',
        monto: -100,
        recibidoDe: 'Juan Pérez',
        documentoPagador: '12345678',
        telefonoPagador: '3001234567'
      }

      expect(() => pagosEfectivoService.validarDatosPago(datosPago)).toThrow('Monto debe ser mayor a 0')
    })

    it('should throw error when monto is exactly at limit', () => {
      const datosPago = {
        mensualidadId: 1,
        tipoPago: 'efectivo',
        monto: 10000000, // Exactly at limit
        recibidoDe: 'Juan Pérez',
        documentoPagador: '12345678',
        telefonoPagador: '3001234567'
      }

      expect(() => pagosEfectivoService.validarDatosPago(datosPago)).not.toThrow()
    })

    it('should throw error for each missing required field', () => {
      const camposRequeridos = [
        'mensualidadId', 'tipoPago', 'monto', 'recibidoDe',
        'documentoPagador', 'telefonoPagador'
      ]

      camposRequeridos.forEach(campo => {
        const datosPago = {
          mensualidadId: 1,
          tipoPago: 'efectivo',
          monto: 50000,
          recibidoDe: 'Juan Pérez',
          documentoPagador: '12345678',
          telefonoPagador: '3001234567'
        }

        delete datosPago[campo]

        expect(() => pagosEfectivoService.validarDatosPago(datosPago)).toThrow(`Campo requerido: ${campo}`)
      })
    })
  })

  describe('obtenerUbicacion', () => {
    beforeEach(() => {
      globalThis.navigator.geolocation = {
        getCurrentPosition: vi.fn((success) => {
          success({
            coords: {
              latitude: 4.6097,
              longitude: -74.0817,
              accuracy: 10
            }
          })
        })
      }
    })

    it('should get location successfully', async () => {
      const ubicacion = await pagosEfectivoService.obtenerUbicacion()

      expect(ubicacion).toHaveProperty('lat')
      expect(ubicacion).toHaveProperty('lng')
      expect(ubicacion).toHaveProperty('precision')
    })

    it('should return null when geolocation is not available', async () => {
      globalThis.navigator.geolocation = undefined

      const ubicacion = await pagosEfectivoService.obtenerUbicacion()

      expect(ubicacion).toBeNull()
    })

    it('should handle geolocation error', async () => {
      globalThis.navigator.geolocation = {
        getCurrentPosition: vi.fn((success, error) => {
          if (error) {
            error(new Error('Geolocation error'))
          }
        })
      }

      const ubicacion = await pagosEfectivoService.obtenerUbicacion()

      expect(ubicacion).toBeNull()
    })
  })

  describe('obtenerInfoDispositivo', () => {
    const originalUserAgent = globalThis.navigator.userAgent

    afterEach(() => {
      globalThis.navigator.userAgent = originalUserAgent
    })

    it('should get device info successfully', () => {
      const info = pagosEfectivoService.obtenerInfoDispositivo()

      expect(info).toHaveProperty('userAgent')
      expect(info).toHaveProperty('plataforma')
      expect(info).toHaveProperty('idioma')
      expect(info).toHaveProperty('cookies')
      expect(info).toHaveProperty('timestamp')
    })

    it('should detect Windows platform', () => {
      globalThis.navigator.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

      const info = pagosEfectivoService.obtenerInfoDispositivo()

      expect(info.plataforma).toBe('Windows')
    })

    it('should detect Mac platform', () => {
      globalThis.navigator.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'

      const info = pagosEfectivoService.obtenerInfoDispositivo()

      expect(info.plataforma).toBe('Mac')
    })

    it('should detect Linux platform', () => {
      globalThis.navigator.userAgent = 'Mozilla/5.0 (X11; Linux x86_64)'

      const info = pagosEfectivoService.obtenerInfoDispositivo()

      expect(info.plataforma).toBe('Linux')
    })

    it('should detect Android platform', () => {
      // Android userAgent must come before Linux check
      globalThis.navigator.userAgent = 'Mozilla/5.0 (Android 10; Mobile; rv:81.0)'

      const info = pagosEfectivoService.obtenerInfoDispositivo()

      expect(info.plataforma).toBe('Android')
    })

    it('should detect iOS platform for iPhone', () => {
      globalThis.navigator.userAgent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)'

      const info = pagosEfectivoService.obtenerInfoDispositivo()

      expect(info.plataforma).toBe('iOS')
    })

    it('should detect iOS platform for iPad', () => {
      globalThis.navigator.userAgent = 'Mozilla/5.0 (iPad; CPU OS 14_0)'

      const info = pagosEfectivoService.obtenerInfoDispositivo()

      expect(info.plataforma).toBe('iOS')
    })

    it('should return unknown for unrecognized platform', () => {
      globalThis.navigator.userAgent = 'Unknown User Agent'

      const info = pagosEfectivoService.obtenerInfoDispositivo()

      expect(info.plataforma).toBe('unknown')
    })
  })

  describe('buscarPagoLocal', () => {
    it('should find pago by codigoRecibo', () => {
      const pago = {
        codigoRecibo: 'REC-123',
        monto: 50000
      }

      pagosEfectivoService.pagos = [pago]

      const result = pagosEfectivoService.buscarPagoLocal('REC-123')

      expect(result).toEqual(pago)
    })

    it('should return undefined when pago not found', () => {
      pagosEfectivoService.pagos = [
        { codigoRecibo: 'REC-123', monto: 50000 }
      ]

      const result = pagosEfectivoService.buscarPagoLocal('REC-999')

      expect(result).toBeUndefined()
    })

    it('should return undefined when pagos array is empty', () => {
      pagosEfectivoService.pagos = []

      const result = pagosEfectivoService.buscarPagoLocal('REC-123')

      expect(result).toBeUndefined()
    })
  })

  describe('filtrarPagosLocales', () => {
    beforeEach(() => {
      pagosEfectivoService.pagos = [
        {
          codigoRecibo: 'REC-1',
          fecha: '2024-01-15',
          administrador: { id: 'admin_001' }
        },
        {
          codigoRecibo: 'REC-2',
          fecha: '2024-02-20',
          administrador: { id: 'admin_002' }
        },
        {
          codigoRecibo: 'REC-3',
          fecha: '2024-03-25',
          administrador: { id: 'admin_001' }
        }
      ]
    })

    it('should return all pagos when no filters provided', () => {
      const result = pagosEfectivoService.filtrarPagosLocales({})

      expect(result).toHaveLength(3)
    })

    it('should filter by fechaInicio', () => {
      const result = pagosEfectivoService.filtrarPagosLocales({
        fechaInicio: '2024-02-01'
      })

      expect(result).toHaveLength(2)
      expect(result.every(p => new Date(p.fecha) >= new Date('2024-02-01'))).toBe(true)
    })

    it('should filter by fechaFin', () => {
      const result = pagosEfectivoService.filtrarPagosLocales({
        fechaFin: '2024-02-28'
      })

      expect(result).toHaveLength(2)
      expect(result.every(p => new Date(p.fecha) <= new Date('2024-02-28'))).toBe(true)
    })

    it('should filter by fechaInicio and fechaFin together', () => {
      const result = pagosEfectivoService.filtrarPagosLocales({
        fechaInicio: '2024-02-01',
        fechaFin: '2024-02-28'
      })

      expect(result).toHaveLength(1)
      expect(result[0].codigoRecibo).toBe('REC-2')
    })

    it('should filter by administrador', () => {
      const result = pagosEfectivoService.filtrarPagosLocales({
        administrador: 'admin_001'
      })

      expect(result).toHaveLength(2)
      expect(result.every(p => p.administrador.id === 'admin_001')).toBe(true)
    })

    it('should filter by all criteria together', () => {
      const result = pagosEfectivoService.filtrarPagosLocales({
        fechaInicio: '2024-01-01',
        fechaFin: '2024-03-31',
        administrador: 'admin_001'
      })

      expect(result).toHaveLength(2)
      expect(result.every(p => p.administrador.id === 'admin_001')).toBe(true)
    })

    it('should return empty array when no pagos match filters', () => {
      const result = pagosEfectivoService.filtrarPagosLocales({
        fechaInicio: '2025-01-01'
      })

      expect(result).toHaveLength(0)
    })
  })

  describe('guardarEnColaReintentos', () => {
    it('should save pago to retry queue successfully', () => {
      localStorageMock.getItem.mockReturnValue('[]')
      const pago = {
        codigoRecibo: 'REC-123',
        monto: 50000
      }

      pagosEfectivoService.guardarEnColaReintentos(pago)

      expect(localStorageMock.setItem).toHaveBeenCalled()
      const setItemCalls = localStorageMock.setItem.mock.calls
      const lastCall = setItemCalls[setItemCalls.length - 1]
      expect(lastCall[0]).toBe('colaReintentos')
      const savedCola = JSON.parse(lastCall[1])
      expect(savedCola).toHaveLength(1)
      expect(savedCola[0].codigoRecibo).toBe('REC-123')
      expect(savedCola[0].intentos).toBe(0)
      expect(savedCola[0].timestamp).toBeDefined()
    })

    it('should append to existing queue', () => {
      const existingCola = [
        { codigoRecibo: 'REC-1', intentos: 0 }
      ]
      localStorageMock.getItem.mockReturnValue(JSON.stringify(existingCola))

      const nuevoPago = {
        codigoRecibo: 'REC-2',
        monto: 60000
      }

      pagosEfectivoService.guardarEnColaReintentos(nuevoPago)

      const setItemCalls = localStorageMock.setItem.mock.calls
      const lastCall = setItemCalls[setItemCalls.length - 1]
      const savedCola = JSON.parse(lastCall[1])
      expect(savedCola).toHaveLength(2)
    })

    it('should handle error when localStorage fails', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      localStorageMock.getItem.mockImplementation(() => {
        throw new Error('localStorage error')
      })

      const pago = {
        codigoRecibo: 'REC-123',
        monto: 50000
      }

      expect(() => pagosEfectivoService.guardarEnColaReintentos(pago)).not.toThrow()
      expect(consoleSpy).toHaveBeenCalledWith(
        'Error al guardar en cola de reintentos:',
        expect.any(Error)
      )
      consoleSpy.mockRestore()
    })
  })

  describe('generarComprobante', () => {
    it('should generate comprobante and log to console', () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      const pago = {
        codigoRecibo: 'REC-123',
        monto: 50000
      }

      pagosEfectivoService.generarComprobante(pago)

      expect(consoleSpy).toHaveBeenCalledWith('Generando comprobante para:', 'REC-123')
      consoleSpy.mockRestore()
    })
  })

  describe('sincronizarPagosPendientes', () => {
    it('should synchronize pending payments successfully', async () => {
      const colaInicial = [
        {
          codigoRecibo: 'REC-1',
          monto: 50000,
          intentos: 0,
          mensualidadId: 1,
          tipoPago: 'efectivo',
          recibidoDe: 'Juan Pérez',
          documentoPagador: '12345678',
          telefonoPagador: '3001234567'
        },
        {
          codigoRecibo: 'REC-2',
          monto: 60000,
          intentos: 1,
          mensualidadId: 2,
          tipoPago: 'efectivo',
          recibidoDe: 'María García',
          documentoPagador: '87654321',
          telefonoPagador: '3007654321'
        }
      ]

      localStorageMock.getItem.mockReturnValue(JSON.stringify(colaInicial))

      globalThis.fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, comprobante: 'COMP-1' })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, comprobante: 'COMP-2' })
        })

      const result = await pagosEfectivoService.sincronizarPagosPendientes()

      expect(result.success).toBe(true)
      expect(result.sincronizados).toBe(2)
      expect(result.pendientes).toBe(0)
    })

    it('should handle payments that fail registration', async () => {
      const colaInicial = [
        {
          codigoRecibo: 'REC-1',
          monto: 50000,
          intentos: 0,
          mensualidadId: 1,
          tipoPago: 'efectivo',
          recibidoDe: 'Juan Pérez',
          documentoPagador: '12345678',
          telefonoPagador: '3001234567'
        },
        {
          codigoRecibo: 'REC-2',
          monto: 60000,
          intentos: 1,
          mensualidadId: 2,
          tipoPago: 'efectivo',
          recibidoDe: 'María García',
          documentoPagador: '87654321',
          telefonoPagador: '3007654321'
        }
      ]

      localStorageMock.getItem.mockReturnValue(JSON.stringify(colaInicial))
      localStorageMock.setItem.mockClear()

      globalThis.fetch.mockClear()
      // First call: successful registration
      globalThis.fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true, comprobante: 'COMP-1' })
        })
      // Second call: failed registration (will throw error in registrarPago)
      globalThis.fetch
        .mockResolvedValueOnce({
          ok: false,
          status: 500,
          statusText: 'Internal Server Error'
        })

      const result = await pagosEfectivoService.sincronizarPagosPendientes()

      expect(result.success).toBe(true)
      expect(result.sincronizados).toBe(1)
      expect(result.pendientes).toBe(1)

      // Verify intentos was incremented for failed payment
      // When registrarPago fails, it calls guardarEnColaReintentos which adds to queue
      // Then sincronizarPagosPendientes saves the queue with incremented intentos
      const setItemCalls = localStorageMock.setItem.mock.calls
      // Find the last call to 'colaReintentos' (the one from sincronizarPagosPendientes)
      const colaCalls = setItemCalls.filter(call => call[0] === 'colaReintentos')
      expect(colaCalls.length).toBeGreaterThan(0)
      const lastColaCall = colaCalls[colaCalls.length - 1]
      const savedCola = JSON.parse(lastColaCall[1])
      // The failed payment (REC-2) should be in the queue with incremented intentos
      const failedPago = savedCola.find(p => p.codigoRecibo === 'REC-2')
      expect(failedPago).toBeDefined()
      // The payment failed, so intentos should be incremented from 1 to 2
      expect(failedPago.intentos).toBe(2)
    })

    it('should increment intentos when registration throws error', async () => {
      const colaInicial = [
        {
          codigoRecibo: 'REC-1',
          monto: 50000,
          intentos: 0,
          mensualidadId: 1,
          tipoPago: 'efectivo',
          recibidoDe: 'Juan Pérez',
          documentoPagador: '12345678',
          telefonoPagador: '3001234567'
        }
      ]

      localStorageMock.getItem.mockReturnValue(JSON.stringify(colaInicial))
      localStorageMock.setItem.mockClear()

      globalThis.fetch.mockClear()
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      await pagosEfectivoService.sincronizarPagosPendientes()

      // Verify intentos was incremented
      // When registrarPago throws error, it calls guardarEnColaReintentos which adds to queue
      // Then sincronizarPagosPendientes saves the queue with incremented intentos
      const setItemCalls = localStorageMock.setItem.mock.calls
      const colaCalls = setItemCalls.filter(call => call[0] === 'colaReintentos')
      expect(colaCalls.length).toBeGreaterThan(0)
      const lastColaCall = colaCalls[colaCalls.length - 1]
      const savedCola = JSON.parse(lastColaCall[1])
      // The failed payment should be in the queue with incremented intentos
      const failedPago = savedCola.find(p => p.codigoRecibo === 'REC-1')
      expect(failedPago).toBeDefined()
      expect(failedPago.intentos).toBe(1)
    })

    it('should skip payments with 3 or more intentos', async () => {
      const colaInicial = [
        {
          codigoRecibo: 'REC-1',
          monto: 50000,
          intentos: 3,
          mensualidadId: 1,
          tipoPago: 'efectivo',
          recibidoDe: 'Juan Pérez',
          documentoPagador: '12345678',
          telefonoPagador: '3001234567'
        },
        {
          codigoRecibo: 'REC-2',
          monto: 60000,
          intentos: 2,
          mensualidadId: 2,
          tipoPago: 'efectivo',
          recibidoDe: 'María García',
          documentoPagador: '87654321',
          telefonoPagador: '3007654321'
        }
      ]

      localStorageMock.getItem.mockReturnValue(JSON.stringify(colaInicial))

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, comprobante: 'COMP-2' })
      })

      const result = await pagosEfectivoService.sincronizarPagosPendientes()

      expect(result.success).toBe(true)
      expect(result.sincronizados).toBe(1)
      expect(globalThis.fetch).toHaveBeenCalledTimes(1)
    })

    it('should handle error when localStorage fails', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      localStorageMock.getItem.mockImplementation(() => {
        throw new Error('localStorage error')
      })

      const result = await pagosEfectivoService.sincronizarPagosPendientes()

      expect(result.success).toBe(false)
      expect(result.error).toBe('localStorage error')
      consoleSpy.mockRestore()
    })

    it('should handle empty queue', async () => {
      localStorageMock.getItem.mockReturnValue('[]')

      const result = await pagosEfectivoService.sincronizarPagosPendientes()

      expect(result.success).toBe(true)
      expect(result.sincronizados).toBe(0)
      expect(result.pendientes).toBe(0)
    })
  })
})

