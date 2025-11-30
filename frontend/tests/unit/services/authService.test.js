import { describe, it, expect, beforeEach, vi } from 'vitest'
import authService from '@/services/authService'
import { mockToken, mockUser, mockLoginCredentials } from '../../fixtures/auth'

// Mock fetch globally
globalThis.fetch = vi.fn()

describe('AuthService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('Login', () => {
    it('should login successfully', async () => {
      const mockResponse = {
        success: true,
        data: {
          token: mockToken,
          user: mockUser
        }
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await authService.login(mockLoginCredentials)

      expect(result.success).toBe(true)
      expect(result.token).toBe(mockToken)
      expect(result.user).toEqual(mockUser)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/login'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      )
    })

    it('should handle login error', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Invalid credentials' })
      })

      const result = await authService.login(mockLoginCredentials)

      expect(result.success).toBe(false)
      expect(result.error).toBe('Invalid credentials')
    })
  })

  describe('Register', () => {
    it('should register successfully', async () => {
      const registerData = {
        tipo_documento: 'CC',
        numero_documento: '1234567890',
        primer_nombre: 'Test',
        password: 'password123'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        headers: {
          get: vi.fn(() => 'application/json')
        },
        json: async () => ({
          data: { id: 1, ...registerData }
        })
      })

      const result = await authService.register(registerData)

      expect(result.success).toBe(true)
      expect(result.data).toBeTruthy()
    })

    it('should handle register error', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        headers: {
          get: vi.fn(() => 'application/json')
        },
        json: async () => ({ error: 'Email already exists' })
      })

      const result = await authService.register({})

      expect(result.success).toBe(false)
      expect(result.error).toContain('Email already exists')
    })
  })

  describe('Logout', () => {
    it('should logout successfully', async () => {
      localStorage.setItem('token', mockToken)

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      })

      await authService.logout(mockToken)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/logout'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': `Bearer ${mockToken}`
          })
        })
      )
    })
  })

  describe('Get Profile', () => {
    it('should get profile successfully', async () => {
      // Mock localStorage.getItem to return token
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          data: mockUser
        })
      })

      const result = await authService.getProfile()

      expect(result.success).toBe(true)
      expect(result.data).toEqual(mockUser)

      // Restore
      localStorage.getItem = originalGetItem
    })

    it('should throw error when no token', async () => {
      localStorage.removeItem('token')

      await expect(authService.getProfile()).rejects.toThrow('No hay token de autenticación')
    })
  })

  describe('Verify Token', () => {
    it('should verify valid token', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      })

      const result = await authService.verifyToken(mockToken)

      expect(result.success).toBe(true)
    })

    it('should return false for invalid token', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ success: false, message: 'Token inválido' })
      })

      const result = await authService.verifyToken('invalid-token')

      // verifyToken returns { success: false } for 401
      expect(result.success).toBe(false)
    })

    it('should return false for empty token', async () => {
      const result = await authService.verifyToken('')

      expect(result.success).toBe(false)
    })
  })

  describe('Get Role Permissions', () => {
    it('should get role permissions successfully', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      const mockPermissions = ['ver_evento', 'editar_perfil']

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: {
            permisos: mockPermissions
          }
        })
      })

      const result = await authService.getRolePermissions('Deportista')

      expect(result.success).toBe(true)
      // The service returns { success: true, ...data.data }, so permisos should be in result
      expect(result.permisos || result.data?.permisos).toEqual(mockPermissions)

      localStorage.getItem = originalGetItem
    })
  })

  describe('Token Management', () => {
    it('should get token from localStorage', () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      expect(authService.getToken()).toBe(mockToken)

      localStorage.getItem = originalGetItem
    })

    it('should check if token exists', () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      expect(authService.hasToken()).toBe(true)

      localStorage.getItem = vi.fn(() => null)
      expect(authService.hasToken()).toBe(false)

      localStorage.getItem = originalGetItem
    })

    it('should clear auth data', () => {
      const originalRemoveItem = localStorage.removeItem
      let removedItems = []
      localStorage.removeItem = vi.fn((key) => {
        removedItems.push(key)
        originalRemoveItem(key)
      })

      authService.clearAuthData()

      expect(removedItems).toContain('token')
      expect(removedItems).toContain('user')

      localStorage.removeItem = originalRemoveItem
    })
  })

  describe('Get User Permissions', () => {
    it('should get user permissions successfully', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      const mockPermissions = ['ver_evento', 'editar_perfil', 'ver_mensualidad']

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: {
            permisos: mockPermissions
          }
        })
      })

      const result = await authService.getUserPermissions()

      expect(result.success).toBe(true)
      expect(result.permisos).toEqual(mockPermissions)

      localStorage.getItem = originalGetItem
    })

    it('should handle error when no token', async () => {
      localStorage.removeItem('token')

      const result = await authService.getUserPermissions()

      expect(result.success).toBe(false)
      expect(result.error).toContain('No hay token')
    })

    it('should handle API error', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Unauthorized' })
      })

      const result = await authService.getUserPermissions()

      expect(result.success).toBe(false)

      localStorage.getItem = originalGetItem
    })
  })

  describe('Verify Profile State', () => {
    it('should verify profile state successfully', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          perfil_completo: true
        })
      })

      const result = await authService.verificarEstadoPerfil()

      expect(result.success).toBe(true)
      expect(result.perfil_completo).toBe(true)

      localStorage.getItem = originalGetItem
    })

    it('should throw error when no token', async () => {
      localStorage.removeItem('token')

      await expect(authService.verificarEstadoPerfil()).rejects.toThrow('No hay token')
    })

    it('should handle API error', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Not found' })
      })

      await expect(authService.verificarEstadoPerfil()).rejects.toThrow()

      localStorage.getItem = originalGetItem
    })
  })

  describe('Get Profile Detail', () => {
    it('should get profile detail successfully', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      const mockDetail = {
        id: 1,
        nombre: 'Test User',
        roles: ['Deportista']
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockDetail
      })

      const result = await authService.getProfileDetail()

      expect(result.success).toBe(true)
      expect(result.id).toBe(1)

      localStorage.getItem = originalGetItem
    })

    it('should handle 401 error (expired token)', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ error: 'Token expired' })
      })

      const result = await authService.getProfileDetail()

      expect(result.success).toBe(false)
      expect(result.expired).toBe(true)

      localStorage.getItem = originalGetItem
    })

    it('should handle other API errors', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ error: 'Server error' })
      })

      const result = await authService.getProfileDetail()

      expect(result.success).toBe(false)

      localStorage.getItem = originalGetItem
    })
  })

  describe('Complete Deportista Profile', () => {
    it('should complete deportista profile successfully', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      const datosDeportista = {
        id_categoria: 1,
        peso: 70.5,
        altura: 175,
        fecha_nacimiento: '2010-01-01'
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: { id: 1, ...datosDeportista },
          message: 'Perfil completado'
        })
      })

      const result = await authService.completarPerfilDeportista(datosDeportista)

      expect(result.success).toBe(true)
      expect(result.data).toBeTruthy()

      localStorage.getItem = originalGetItem
    })

    it('should handle missing optional fields', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      const datosDeportista = {
        id_categoria: 1
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: { id: 1 },
          message: 'Perfil completado'
        })
      })

      const result = await authService.completarPerfilDeportista(datosDeportista)

      expect(result.success).toBe(true)

      localStorage.getItem = originalGetItem
    })

    it('should handle API error', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Validation error' })
      })

      const result = await authService.completarPerfilDeportista({})

      expect(result.success).toBe(false)

      localStorage.getItem = originalGetItem
    })
  })

  describe('Associate Acudiente Deportista', () => {
    it('should associate acudiente successfully', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      const datosAsociacion = {
        id_deportista: 1,
        id_acudiente: 2,
        id_parentesco: 1
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: datosAsociacion,
          message: 'Asociación exitosa'
        })
      })

      const result = await authService.asociarAcudienteDeportista(datosAsociacion)

      expect(result.success).toBe(true)

      localStorage.getItem = originalGetItem
    })

    it('should handle API error', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Already associated' })
      })

      const result = await authService.asociarAcudienteDeportista({})

      expect(result.success).toBe(false)

      localStorage.getItem = originalGetItem
    })
  })

  describe('Complete Acudiente Profile', () => {
    it('should complete acudiente profile successfully', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      const datosAcudiente = {
        id_deportista: 1,
        id_parentesco: 2,
        es_responsable: true
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: datosAcudiente,
          message: 'Perfil completado'
        })
      })

      const result = await authService.completarPerfilAcudiente(datosAcudiente)

      expect(result.success).toBe(true)

      localStorage.getItem = originalGetItem
    })

    it('should default es_responsable to false', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      const datosAcudiente = {
        id_deportista: 1,
        id_parentesco: 2
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: { ...datosAcudiente, es_responsable: false },
          message: 'Perfil completado'
        })
      })

      const result = await authService.completarPerfilAcudiente(datosAcudiente)

      expect(result.success).toBe(true)

      localStorage.getItem = originalGetItem
    })
  })

  describe('Forgot Password', () => {
    it('should send forgot password request successfully', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          message: 'Email sent'
        })
      })

      const result = await authService.forgotPassword('test@example.com')

      expect(result.success).toBe(true)
      expect(result.message).toBeTruthy()
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/forgot-password'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('test@example.com')
        })
      )
    })

    it('should handle API error', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          error: 'Email not found'
        })
      })

      const result = await authService.forgotPassword('test@example.com')

      expect(result.success).toBe(false)
      expect(result.error).toBeTruthy()
    })
  })

  describe('Reset Password', () => {
    it('should reset password successfully', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          message: 'Password reset successful'
        })
      })

      const result = await authService.resetPassword('token123', 'newpass', 'newpass')

      expect(result.success).toBe(true)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/reset-password'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('newpass')
        })
      )
    })

    it('should handle API error', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          error: 'Invalid token'
        })
      })

      const result = await authService.resetPassword('invalid', 'newpass', 'newpass')

      expect(result.success).toBe(false)
    })
  })

  describe('Update User', () => {
    it('should update user successfully', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      const datosPersona = { primer_nombre: 'Updated' }
      const datosUsuario = { usuario: 'newuser' }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: { id: 1, ...datosPersona, ...datosUsuario },
          message: 'Updated successfully'
        })
      })

      const result = await authService.updateUser(1, datosPersona, datosUsuario)

      expect(result.success).toBe(true)

      localStorage.getItem = originalGetItem
    })

    it('should update only persona data', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      const datosPersona = { primer_nombre: 'Updated' }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: { id: 1, ...datosPersona },
          message: 'Updated successfully'
        })
      })

      const result = await authService.updateUser(1, datosPersona)

      expect(result.success).toBe(true)

      localStorage.getItem = originalGetItem
    })

    it('should return error when no data provided', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      // The service throws an error but catches it and returns { success: false }
      const result = await authService.updateUser(1, {}, {})

      expect(result.success).toBe(false)
      expect(result.error).toContain('Debe proporcionar')

      localStorage.getItem = originalGetItem
    })
  })

  describe('Get Role Options', () => {
    it('should get role options successfully', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      const mockRoles = {
        roles: ['Deportista', 'Acudiente'],
        paneles: ['/deportista/dashboard']
      }

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: mockRoles
        })
      })

      const result = await authService.getRoleOptions()

      expect(result.success).toBe(true)
      expect(result.data).toEqual(mockRoles)

      localStorage.getItem = originalGetItem
    })

    it('should handle 401 error', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ error: 'Unauthorized' })
      })

      const result = await authService.getRoleOptions()

      expect(result.success).toBe(false)
      expect(result.expired).toBe(true)

      localStorage.getItem = originalGetItem
    })
  })

  describe('Activate Role', () => {
    it('should activate role successfully', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: { activeRole: 'Deportista' }
        })
      })

      const result = await authService.activateRole('Deportista')

      expect(result.success).toBe(true)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/roles/activar'),
        expect.objectContaining({
          method: 'PUT',
          body: expect.stringContaining('Deportista')
        })
      )

      localStorage.getItem = originalGetItem
    })

    it('should handle 401 error', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ error: 'Unauthorized' })
      })

      const result = await authService.activateRole('Deportista')

      expect(result.success).toBe(false)
      expect(result.expired).toBe(true)

      localStorage.getItem = originalGetItem
    })
  })

  describe('Register Edge Cases', () => {
    it('should handle timeout error', async () => {
      // Mock AbortController properly
      const mockAbort = vi.fn()
      const mockSignal = {}
      globalThis.AbortController = vi.fn(function() {
        this.abort = mockAbort
        this.signal = mockSignal
      })

      globalThis.fetch = vi.fn(() => {
        const error = new Error('Aborted')
        error.name = 'AbortError'
        return Promise.reject(error)
      })

      const result = await authService.register({})

      expect(result.success).toBe(false)
      expect(result.error).toContain('tardó demasiado')
    })

    it('should handle network error', async () => {
      globalThis.fetch = vi.fn(() => {
        const error = new TypeError('Failed to fetch')
        error.message = 'Failed to fetch'
        return Promise.reject(error)
      })

      const result = await authService.register({})

      expect(result.success).toBe(false)
      // The service checks for TypeError and 'fetch' in message to return connection error
      expect(result.error).toContain('conexión')
    })

    it('should handle non-JSON response', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        headers: {
          get: vi.fn(() => 'text/html')
        },
        text: async () => '<html>Error</html>'
      })

      const result = await authService.register({})

      expect(result.success).toBe(false)
    })
  })

  describe('Verify Token Edge Cases', () => {
    it('should handle null token', async () => {
      const result = await authService.verifyToken(null)

      expect(result.success).toBe(false)
    })

    it('should handle undefined token', async () => {
      const result = await authService.verifyToken('undefined')

      expect(result.success).toBe(false)
    })

    it('should handle invalid JSON response', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => {
          throw new Error('Invalid JSON')
        }
      })

      const result = await authService.verifyToken('token')

      expect(result.success).toBe(false)
    })

    it('should handle network error silently', async () => {
      globalThis.fetch = vi.fn(() => {
        const error = new Error('Failed to fetch')
        return Promise.reject(error)
      })

      const result = await authService.verifyToken('token')

      expect(result.success).toBe(false)
    })
  })

  describe('Get Role Permissions Edge Cases', () => {
    it('should handle 401 error (expired token)', async () => {
      const originalGetItem = localStorage.getItem
      localStorage.getItem = vi.fn((key) => {
        if (key === 'token') return mockToken
        return originalGetItem(key)
      })

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ error: 'Token expired' })
      })

      const result = await authService.getRolePermissions('Deportista')

      expect(result.success).toBe(false)
      expect(result.expired).toBe(true)

      localStorage.getItem = originalGetItem
    })
  })
})

