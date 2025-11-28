import { describe, it, expect, beforeEach, vi } from 'vitest'
import authService from '@/services/authService'
import { mockToken, mockUser, mockLoginCredentials } from '../../fixtures/auth'

// Mock fetch globally
global.fetch = vi.fn()

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

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await authService.login(mockLoginCredentials)

      expect(result.success).toBe(true)
      expect(result.token).toBe(mockToken)
      expect(result.user).toEqual(mockUser)
      expect(global.fetch).toHaveBeenCalledWith(
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
      global.fetch.mockResolvedValueOnce({
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

      global.fetch.mockResolvedValueOnce({
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
      global.fetch.mockResolvedValueOnce({
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

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      })

      await authService.logout(mockToken)

      expect(global.fetch).toHaveBeenCalledWith(
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

      global.fetch.mockResolvedValueOnce({
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
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      })

      const result = await authService.verifyToken(mockToken)

      expect(result.success).toBe(true)
    })

    it('should return false for invalid token', async () => {
      global.fetch.mockResolvedValueOnce({
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

      global.fetch.mockResolvedValueOnce({
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
})

