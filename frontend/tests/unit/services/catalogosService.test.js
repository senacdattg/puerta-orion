import { describe, it, expect, beforeEach, vi } from 'vitest'
import catalogosService from '@/services/catalogosService'

// Mock fetch globally
globalThis.fetch = vi.fn()

// Mock API_CONFIG
vi.mock('@/config/environment', () => ({
  API_CONFIG: {
    baseURL: 'http://localhost:5000'
  }
}))

describe('CatalogosService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getTiposDocumento', () => {
    it('should fetch tipos documento successfully', async () => {
      const mockData = [
        { id: 1, nombre: 'Cédula de Ciudadanía', codigo: 'cc' },
        { id: 2, nombre: 'Cédula de Extranjería', codigo: 'ce' }
      ]

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockData })
      })

      const result = await catalogosService.getTiposDocumento()

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/catalogos/tipos-documento'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      )
    })

    it('should handle error when fetching tipos documento', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => 'Server error'
      })

      await expect(catalogosService.getTiposDocumento()).rejects.toThrow()
    })

    it('should return empty array when data is not present', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      })

      const result = await catalogosService.getTiposDocumento()

      expect(result).toEqual([])
    })
  })

  describe('getSexos', () => {
    it('should fetch sexos successfully', async () => {
      const mockData = [
        { id: 1, nombre: 'Masculino', valor: 'masculino' },
        { id: 2, nombre: 'Femenino', valor: 'femenino' }
      ]

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockData })
      })

      const result = await catalogosService.getSexos()

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/catalogos/sexos'),
        expect.objectContaining({
          method: 'GET'
        })
      )
    })

    it('should handle error when fetching sexos', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: async () => 'Not found'
      })

      await expect(catalogosService.getSexos()).rejects.toThrow()
    })
  })

  describe('getCategorias', () => {
    it('should fetch categorias successfully', async () => {
      const mockData = [
        { id: 1, nombre_categoria: 'Pre-infantil', codigo_categoria: 'PRE' },
        { id: 2, nombre_categoria: 'Infantil', codigo_categoria: 'INF' }
      ]

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockData })
      })

      const result = await catalogosService.getCategorias()

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/catalogos/categorias'),
        expect.objectContaining({
          method: 'GET'
        })
      )
    })

    it('should handle error when fetching categorias', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => 'Server error'
      })

      await expect(catalogosService.getCategorias()).rejects.toThrow()
    })
  })

  describe('getCatalogosCompletos', () => {
    it('should fetch all catalogos successfully', async () => {
      const mockData = {
        tipos_documento: [
          { id: 1, nombre: 'Cédula de Ciudadanía', codigo: 'cc' }
        ],
        sexos: [
          { id: 1, nombre: 'Masculino', valor: 'masculino' }
        ],
        categorias: [
          { id: 1, nombre_categoria: 'Pre-infantil', codigo_categoria: 'PRE' }
        ]
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockData })
      })

      const result = await catalogosService.getCatalogosCompletos()

      // The service returns the full response object
      expect(result).toHaveProperty('success', true)
      expect(result).toHaveProperty('data')
      expect(result.data).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/catalogos/catalogos-completos'),
        expect.objectContaining({
          method: 'GET'
        })
      )
    })

    it('should handle error when fetching catalogos completos', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => 'Server error'
      })

      await expect(catalogosService.getCatalogosCompletos()).rejects.toThrow()
    })
  })

  describe('cargarCatalogosFormulario', () => {
    it('should load catalogos for form successfully', async () => {
      const mockData = {
        tipos_documento: [
          { id: 1, nombre: 'Cédula de Ciudadanía', codigo: 'cc' }
        ],
        sexos: [
          { id: 1, nombre: 'Masculino', valor: 'masculino' }
        ]
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: mockData })
      })

      const result = await catalogosService.cargarCatalogosFormulario()

      expect(result).toHaveProperty('tiposDocumento')
      expect(result).toHaveProperty('sexos')
      expect(result.tiposDocumento).toEqual(mockData.tipos_documento)
      expect(result.sexos).toEqual(mockData.sexos)
    })

    it('should handle error when loading catalogos for form', async () => {
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(catalogosService.cargarCatalogosFormulario()).rejects.toThrow()
    })
  })
})

