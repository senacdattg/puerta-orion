import { describe, it, expect, beforeEach, vi } from 'vitest'
import usuariosService from '@/services/usuariosService'

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

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await usuariosService.listarUsuarios()

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
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

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await usuariosService.listarUsuarios('activo', 10, 5)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/usuarios?estado=activo&limit=10&offset=5'),
        expect.any(Object)
      )
    })

    it('should not include estado parameter when estado is "todos"', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true, data: [] })
      })

      await usuariosService.listarUsuarios('todos', 5, 0)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.not.stringContaining('estado='),
        expect.any(Object)
      )
    })

    it('should handle error when listing usuarios', async () => {
      globalThis.fetch.mockResolvedValueOnce({
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

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await usuariosService.listarRoles()

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/dynamic-data/roles'),
        expect.objectContaining({
          method: 'GET'
        })
      )
    })

    it('should handle error when listing roles', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 403,
        statusText: 'Forbidden'
      })

      await expect(usuariosService.listarRoles()).rejects.toThrow('Error 403')
    })
  })

  describe('cambiarRolUsuario', () => {
    it('should change user roles successfully with array', async () => {
      const mockData = {
        success: true,
        message: 'Roles actualizados correctamente'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await usuariosService.cambiarRolUsuario(1, [1, 2])

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/usuarios/1/rol'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({ id_roles: [1, 2] })
        })
      )
    })

    it('should change user roles successfully with single number (líneas 100-101)', async () => {
      const mockData = {
        success: true,
        message: 'Rol actualizado correctamente'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await usuariosService.cambiarRolUsuario(1, 2)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/usuarios/1/rol'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({ id_roles: [2] })
        })
      )
    })

    it('should handle error when changing roles', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => ({ error: 'Error 400' })
      })

      await expect(usuariosService.cambiarRolUsuario(1, [1, 2])).rejects.toThrow('Error 400')
      expect(consoleSpy).toHaveBeenCalled()

      consoleSpy.mockRestore()
    })
  })

  describe('cambiarEstadoUsuario', () => {
    it('should change user status successfully', async () => {
      const mockData = {
        success: true,
        message: 'Estado actualizado correctamente'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await usuariosService.cambiarEstadoUsuario(1, true)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/usuarios/1/estado'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({ estado: true })
        })
      )
    })

    it('should handle error when changing status', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const mockErrorData = {
        error: 'Usuario no encontrado'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => mockErrorData
      })

      await expect(usuariosService.cambiarEstadoUsuario(1, true)).rejects.toThrow('Error 404: Usuario no encontrado')
      expect(consoleSpy).toHaveBeenCalled()

      consoleSpy.mockRestore()
    })

    it('should handle error when response json fails', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => {
          throw new Error('Invalid JSON')
        }
      })

      await expect(usuariosService.cambiarEstadoUsuario(1, false)).rejects.toThrow('Error 500: Internal Server Error')
    })
  })

  describe('obtenerDetalleUsuario', () => {
    it('should get user detail successfully', async () => {
      const mockData = {
        success: true,
        data: {
          id_usuario: 1,
          usuario: 'testuser',
          persona: {
            primer_nombre: 'Test',
            primer_apellido: 'User'
          }
        }
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await usuariosService.obtenerDetalleUsuario(1)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/usuarios/1/detalle'),
        expect.objectContaining({
          method: 'GET'
        })
      )
    })

    it('should handle error when getting user detail', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const mockErrorData = {
        error: 'Usuario no encontrado'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => mockErrorData
      })

      await expect(usuariosService.obtenerDetalleUsuario(999)).rejects.toThrow('Error 404: Usuario no encontrado')
      expect(consoleSpy).toHaveBeenCalled()

      consoleSpy.mockRestore()
    })

    it('should handle error when response json fails', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => {
          throw new Error('Invalid JSON')
        }
      })

      await expect(usuariosService.obtenerDetalleUsuario(1)).rejects.toThrow('Error 500: Internal Server Error')
    })
  })

  describe('actualizarUsuario', () => {
    it('should update user successfully', async () => {
      const mockData = {
        success: true,
        message: 'Usuario actualizado correctamente',
        data: {
          id_usuario: 1,
          usuario: 'updateduser'
        }
      }

      const body = {
        datos_usuario: {
          usuario: 'updateduser'
        }
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const result = await usuariosService.actualizarUsuario(1, body)

      expect(result).toEqual(mockData)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/usuarios/1'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(body)
        })
      )
    })

    it('should handle error when updating user (líneas 167-169)', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const mockErrorData = {
        error: 'Error de validación'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => mockErrorData
      })

      const body = {
        datos_persona: {
          primer_nombre: 'Test'
        }
      }

      await expect(usuariosService.actualizarUsuario(1, body)).rejects.toThrow('Error 400: Error de validación')
      expect(consoleSpy).toHaveBeenCalled()

      consoleSpy.mockRestore()
    })

    it('should handle error when response json fails in actualizarUsuario', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => {
          throw new Error('Invalid JSON')
        }
      })

      const body = {
        datos_usuario: {
          usuario: 'testuser'
        }
      }

      await expect(usuariosService.actualizarUsuario(1, body)).rejects.toThrow('Error 500: Internal Server Error')
    })

    it('should handle network errors', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(usuariosService.actualizarUsuario(1, {})).rejects.toThrow('Network error')
      expect(consoleSpy).toHaveBeenCalled()

      consoleSpy.mockRestore()
    })
  })
})

