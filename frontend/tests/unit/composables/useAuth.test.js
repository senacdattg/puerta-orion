import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuth } from '@/composables/useAuth'
import { useAuthStore } from '@/stores/auth'
import { mockUser, mockToken } from '../../fixtures/auth'

vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

describe('useAuth Composable', () => {
  let mockStore

  beforeEach(() => {
    setActivePinia(createPinia())
    mockStore = {
      user: null,
      token: null,
      isLoading: false,
      estaAutenticado: false,
      login: vi.fn(),
      logout: vi.fn(),
      register: vi.fn(),
      verifyToken: vi.fn()
    }
    useAuthStore.mockReturnValue(mockStore)
  })

  describe('Initial State', () => {
    it('should return computed properties', () => {
      const { isAuthenticated, user, token, isLoading } = useAuth()

      expect(isAuthenticated.value).toBe(false)
      expect(user.value).toBeNull()
      expect(token.value).toBeNull()
      expect(isLoading.value).toBe(false)
    })
  })

  describe('Login', () => {
    it('should call store login', async () => {
      mockStore.login.mockResolvedValue({ success: true })

      const { login } = useAuth()
      const result = await login({ username: 'test', password: 'pass' })

      expect(mockStore.login).toHaveBeenCalledWith({ username: 'test', password: 'pass' })
      expect(result.success).toBe(true)
    })

    it('should handle login error', async () => {
      mockStore.login.mockRejectedValue(new Error('Login failed'))

      const { login } = useAuth()
      const result = await login({})

      expect(result.success).toBe(false)
      expect(result.error).toBe('Login failed')
    })
  })

  describe('Logout', () => {
    it('should call store logout', async () => {
      mockStore.logout.mockResolvedValue()

      const { logout } = useAuth()
      const result = await logout()

      expect(mockStore.logout).toHaveBeenCalled()
      expect(result.success).toBe(true)
    })
  })

  describe('Register', () => {
    it('should call store register', async () => {
      mockStore.register.mockResolvedValue({ success: true })

      const { register } = useAuth()
      const result = await register({})

      expect(mockStore.register).toHaveBeenCalled()
      expect(result.success).toBe(true)
    })
  })

  describe('Verify Token', () => {
    it('should call store verifyToken', async () => {
      mockStore.verifyToken.mockResolvedValue(true)

      const { verifyToken } = useAuth()
      const result = await verifyToken()

      expect(mockStore.verifyToken).toHaveBeenCalled()
      expect(result).toBe(true)
    })
  })

  describe('Computed Properties', () => {
    it('should compute userName from user', () => {
      mockStore.user = {
        persona: {
          nombre_completo: 'John Doe'
        }
      }

      const { userName } = useAuth()
      expect(userName.value).toBe('John')
    })

    it('should return default userName when no user', () => {
      mockStore.user = null
      const { userName } = useAuth()
      expect(userName.value).toBe('Usuario')
    })

    it('should compute userEmail', () => {
      mockStore.user = {
        persona: {
          correo_electronico: 'test@example.com'
        }
      }

      const { userEmail } = useAuth()
      expect(userEmail.value).toBe('test@example.com')
    })
  })

  describe('Role Checks', () => {
    it('should check hasRole', () => {
      mockStore.user = {
        roles: ['Deportista']
      }

      const { hasRole } = useAuth()
      expect(hasRole('Deportista')).toBe(true)
      expect(hasRole('Administrador')).toBe(false)
    })

    it('should check hasAnyRole', () => {
      mockStore.user = {
        roles: ['Deportista']
      }

      const { hasAnyRole } = useAuth()
      expect(hasAnyRole(['Deportista', 'Admin'])).toBe(true)
      expect(hasAnyRole(['Admin', 'Entrenador'])).toBe(false)
    })
  })
})

