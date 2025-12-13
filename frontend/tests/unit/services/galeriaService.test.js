import { describe, it, expect, beforeEach, vi } from 'vitest'
import galeriaService from '@/services/galeriaService'

// Mock fetch globally
globalThis.fetch = vi.fn()

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(() => 'mock-token'),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
globalThis.localStorage = localStorageMock

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

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await galeriaService.cargarImagenes()

      expect(result).toEqual(mockData.data)
      expect(galeriaService.imagenes).toEqual(mockData.data)
      expect(globalThis.fetch).toHaveBeenCalledWith(
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

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await galeriaService.cargarImagenes({
        id_tipo_evento: 1,
        id_categoria: 2,
        limit: 10
      })

      expect(result).toEqual(mockData.data)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/galeria/?id_tipo_evento=1&id_categoria=2&limit=10'),
        expect.any(Object)
      )
    })

    it('should handle 401 authentication error', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized'
      })

      // The service catches errors and returns empty array
      const result = await galeriaService.cargarImagenes()
      expect(result).toEqual([])
    })

    it('should handle 500 server error', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      })

      // The service catches errors and returns empty array
      const result = await galeriaService.cargarImagenes()
      expect(result).toEqual([])
    })

    it('should return empty array on error', async () => {
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

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

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await galeriaService.obtenerImagen(1)

      expect(result).toEqual(mockData.data)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/galeria/1'),
        expect.objectContaining({
          method: 'GET'
        })
      )
    })

    it('should handle error when getting imagen', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      })

      await expect(galeriaService.obtenerImagen(999)).rejects.toThrow('Error al obtener imagen')
    })

    it('should return null when response does not have data', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: null })
      })

      const result = await galeriaService.obtenerImagen(1)
      expect(result).toBeNull()
    })

    it('should handle network error when getting imagen', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(galeriaService.obtenerImagen(1)).rejects.toThrow('Network error')
      
      consoleErrorSpy.mockRestore()
    })
  })

  describe('crearImagenConArchivo', () => {
    it('should create image with file successfully', async () => {
      const mockFormData = new FormData()
      mockFormData.append('file', new Blob(['test']))

      const mockResponse = {
        success: true,
        data: { id_galeria: 1, url: 'http://example.com/img.jpg' }
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await galeriaService.crearImagenConArchivo(mockFormData)

      expect(result).toEqual(mockResponse.data)
      expect(galeriaService.imagenes).toContain(mockResponse.data)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/archivos/upload'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            Authorization: 'Bearer mock-token'
          }),
          body: mockFormData
        })
      )
    })

    it('should throw error when response is not ok', async () => {
      const mockFormData = new FormData()
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Upload failed' })
      })

      await expect(galeriaService.crearImagenConArchivo(mockFormData))
        .rejects.toThrow('Upload failed')
    })

    it('should throw error when response does not have success and data', async () => {
      const mockFormData = new FormData()
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: false })
      })

      await expect(galeriaService.crearImagenConArchivo(mockFormData))
        .rejects.toThrow('Respuesta inválida del servidor')
    })

    it('should throw generic error when response is not ok without error message', async () => {
      const mockFormData = new FormData()
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({})
      })

      await expect(galeriaService.crearImagenConArchivo(mockFormData))
        .rejects.toThrow('Error al subir imagen')
    })

    it('should handle network error', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const mockFormData = new FormData()
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(galeriaService.crearImagenConArchivo(mockFormData))
        .rejects.toThrow('Network error')
      
      expect(consoleErrorSpy).toHaveBeenCalled()
      consoleErrorSpy.mockRestore()
    })
  })

  describe('actualizarImagen', () => {
    beforeEach(() => {
      galeriaService.imagenes = [
        { id_galeria: 1, url: 'old.jpg' },
        { id_galeria: 2, url: 'other.jpg' }
      ]
    })

    it('should update image successfully', async () => {
      const datosActualizados = { descripcion: 'New description' }
      const mockResponse = {
        success: true,
        data: { id_galeria: 1, url: 'new.jpg', descripcion: 'New description' }
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await galeriaService.actualizarImagen(1, datosActualizados)

      expect(result).toEqual(mockResponse.data)
      expect(galeriaService.imagenes[0]).toEqual(mockResponse.data)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/galeria/1'),
        expect.objectContaining({
          method: 'PUT',
          headers: expect.any(Object),
          body: JSON.stringify(datosActualizados)
        })
      )
    })

    it('should update image when image not in cache', async () => {
      const datosActualizados = { descripcion: 'New description' }
      const mockResponse = {
        success: true,
        data: { id_galeria: 999, url: 'new.jpg' }
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await galeriaService.actualizarImagen(999, datosActualizados)

      expect(result).toEqual(mockResponse.data)
      expect(galeriaService.imagenes).toHaveLength(2)
    })

    it('should throw error when response is not ok', async () => {
      const datosActualizados = { descripcion: 'New description' }
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Update failed' })
      })

      await expect(galeriaService.actualizarImagen(1, datosActualizados))
        .rejects.toThrow('Update failed')
    })

    it('should throw error when response does not have success and data', async () => {
      const datosActualizados = { descripcion: 'New description' }
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: false })
      })

      await expect(galeriaService.actualizarImagen(1, datosActualizados))
        .rejects.toThrow('Respuesta inválida del servidor')
    })

    it('should handle network error', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const datosActualizados = { descripcion: 'New description' }
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(galeriaService.actualizarImagen(1, datosActualizados))
        .rejects.toThrow('Network error')
      
      expect(consoleErrorSpy).toHaveBeenCalled()
      consoleErrorSpy.mockRestore()
    })
  })

  describe('eliminarImagen', () => {
    beforeEach(() => {
      galeriaService.imagenes = [
        { id_galeria: 1, url: 'img1.jpg' },
        { id_galeria: 2, url: 'img2.jpg' },
        { id_galeria: 3, url: 'img3.jpg' }
      ]
    })

    it('should delete image successfully', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      })

      const result = await galeriaService.eliminarImagen(2)

      expect(result).toBe(true)
      expect(galeriaService.imagenes).toHaveLength(2)
      expect(galeriaService.imagenes.find(img => img.id_galeria === 2)).toBeUndefined()
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/galeria/2'),
        expect.objectContaining({
          method: 'DELETE'
        })
      )
    })

    it('should throw error when response is not ok', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Delete failed' })
      })

      await expect(galeriaService.eliminarImagen(1))
        .rejects.toThrow('Delete failed')
    })

    it('should throw error when response does not have success', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: false })
      })

      await expect(galeriaService.eliminarImagen(1))
        .rejects.toThrow('Respuesta inválida del servidor')
    })

    it('should handle network error', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(galeriaService.eliminarImagen(1))
        .rejects.toThrow('Network error')
      
      expect(consoleErrorSpy).toHaveBeenCalled()
      consoleErrorSpy.mockRestore()
    })
  })

  describe('cargarCatalogos', () => {
    it('should load catalogos successfully', async () => {
      const mockResponse = {
        success: true,
        data: {
          tipos_evento: [{ id_tipo_evento: 1, nombre: 'Evento 1' }],
          categorias: [{ id_categoria: 1, nombre: 'Categoria 1' }]
        }
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await galeriaService.cargarCatalogos()

      expect(result).toEqual({
        tiposEvento: mockResponse.data.tipos_evento,
        categorias: mockResponse.data.categorias
      })
      expect(galeriaService.tiposEvento).toEqual(mockResponse.data.tipos_evento)
      expect(galeriaService.categorias).toEqual(mockResponse.data.categorias)
    })

    it('should return empty arrays when response does not have data', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: false })
      })

      const result = await galeriaService.cargarCatalogos()

      expect(result).toEqual({ tiposEvento: [], categorias: [] })
    })

    it('should handle missing properties in response data', async () => {
      const mockResponse = {
        success: true,
        data: {}
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await galeriaService.cargarCatalogos()

      expect(result).toEqual({ tiposEvento: [], categorias: [] })
    })

    it('should handle error when loading catalogos', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      const result = await galeriaService.cargarCatalogos()

      expect(result).toEqual({ tiposEvento: [], categorias: [] })
      expect(consoleErrorSpy).toHaveBeenCalled()
      consoleErrorSpy.mockRestore()
    })

    it('should handle non-ok response', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        statusText: 'Server Error'
      })

      const result = await galeriaService.cargarCatalogos()

      expect(result).toEqual({ tiposEvento: [], categorias: [] })
      consoleErrorSpy.mockRestore()
    })
  })

  describe('obtenerTodasLasImagenes', () => {
    it('should return existing imagenes when cache is not empty', async () => {
      galeriaService.imagenes = [
        { id_galeria: 1, url: 'img1.jpg' },
        { id_galeria: 2, url: 'img2.jpg' }
      ]

      const result = await galeriaService.obtenerTodasLasImagenes()

      expect(result).toEqual(galeriaService.imagenes)
      expect(globalThis.fetch).not.toHaveBeenCalled()
    })

    it('should load imagenes when cache is empty', async () => {
      galeriaService.imagenes = []
      const mockData = {
        success: true,
        data: [{ id_galeria: 1, url: 'img1.jpg' }]
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await galeriaService.obtenerTodasLasImagenes()

      expect(result).toEqual(mockData.data)
      expect(globalThis.fetch).toHaveBeenCalled()
    })

    it('should handle error when loading imagenes', async () => {
      galeriaService.imagenes = []
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      const result = await galeriaService.obtenerTodasLasImagenes()

      expect(result).toEqual([])
      expect(consoleErrorSpy).toHaveBeenCalled()
      consoleErrorSpy.mockRestore()
    })
  })

  describe('filtrarImagenesPorTipoEvento', () => {
    beforeEach(() => {
      galeriaService.imagenes = [
        { id_galeria: 1, id_tipo_evento: 1 },
        { id_galeria: 2, id_tipo_evento: 2 },
        { id_galeria: 3, id_tipo_evento: 1 }
      ]
    })

    it('should filter imagenes by tipo evento', () => {
      const result = galeriaService.filtrarImagenesPorTipoEvento(1)

      expect(result).toHaveLength(2)
      expect(result.every(img => img.id_tipo_evento === 1)).toBe(true)
    })

    it('should return empty array when no matches', () => {
      const result = galeriaService.filtrarImagenesPorTipoEvento(999)

      expect(result).toEqual([])
    })
  })

  describe('filtrarImagenesPorCategoria', () => {
    beforeEach(() => {
      galeriaService.imagenes = [
        { id_galeria: 1, id_categoria: 1 },
        { id_galeria: 2, id_categoria: 2 },
        { id_galeria: 3, id_categoria: 1 }
      ]
    })

    it('should filter imagenes by categoria', () => {
      const result = galeriaService.filtrarImagenesPorCategoria(1)

      expect(result).toHaveLength(2)
      expect(result.every(img => img.id_categoria === 1)).toBe(true)
    })

    it('should return empty array when no matches', () => {
      const result = galeriaService.filtrarImagenesPorCategoria(999)

      expect(result).toEqual([])
    })
  })

  describe('obtenerTipoEventoPorId', () => {
    beforeEach(() => {
      galeriaService.tiposEvento = [
        { id_tipo_evento: 1, nombre: 'Evento 1' },
        { id_tipo_evento: 2, nombre: 'Evento 2' }
      ]
    })

    it('should get tipo evento by id', () => {
      const result = galeriaService.obtenerTipoEventoPorId(1)

      expect(result).toEqual({ id_tipo_evento: 1, nombre: 'Evento 1' })
    })

    it('should return undefined when not found', () => {
      const result = galeriaService.obtenerTipoEventoPorId(999)

      expect(result).toBeUndefined()
    })
  })

  describe('obtenerCategoriaPorId', () => {
    beforeEach(() => {
      galeriaService.categorias = [
        { id_categoria: 1, nombre: 'Categoria 1' },
        { id_categoria: 2, nombre: 'Categoria 2' }
      ]
    })

    it('should get categoria by id', () => {
      const result = galeriaService.obtenerCategoriaPorId(1)

      expect(result).toEqual({ id_categoria: 1, nombre: 'Categoria 1' })
    })

    it('should return undefined when not found', () => {
      const result = galeriaService.obtenerCategoriaPorId(999)

      expect(result).toBeUndefined()
    })
  })

  describe('limpiarCache', () => {
    beforeEach(() => {
      galeriaService.imagenes = [{ id_galeria: 1 }]
      galeriaService.tiposEvento = [{ id_tipo_evento: 1 }]
      galeriaService.categorias = [{ id_categoria: 1 }]
    })

    it('should clear all cache', () => {
      galeriaService.limpiarCache()

      expect(galeriaService.imagenes).toEqual([])
      expect(galeriaService.tiposEvento).toEqual([])
      expect(galeriaService.categorias).toEqual([])
    })
  })

  describe('cargarImagenes edge cases', () => {
    it('should handle other error status codes', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 403,
        statusText: 'Forbidden'
      })

      const result = await galeriaService.cargarImagenes()
      expect(result).toEqual([])
    })

    it('should handle offset filter', async () => {
      const mockData = {
        success: true,
        data: [{ id_galeria: 1 }]
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      await galeriaService.cargarImagenes({ offset: 10 })

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('offset=10'),
        expect.any(Object)
      )
    })

    it('should return empty array when response has no success or data', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: false })
      })

      const result = await galeriaService.cargarImagenes()
      expect(result).toEqual([])
    })
  })
})

