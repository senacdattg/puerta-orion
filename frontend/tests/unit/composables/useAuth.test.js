import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAuth } from '@/composables/useAuth'
import { useAuthStore } from '@/stores/auth'

// Mock the auth store
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

describe('useAuth', () => {
  let mockAuthStore

  beforeEach(() => {
    mockAuthStore = {
      estaAutenticado: false,
      user: null,
      token: null,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      register: vi.fn(),
      verifyToken: vi.fn(),
      inicializar: vi.fn()
    }

    useAuthStore.mockReturnValue(mockAuthStore)
  })

  describe('computed properties', () => {
    it('should return isAuthenticated from store', () => {
      mockAuthStore.estaAutenticado = true
      const { isAuthenticated } = useAuth()

      expect(isAuthenticated.value).toBe(true)
    })

    it('should return user from store', () => {
      const mockUser = { id: 1, usuario: 'testuser' }
      mockAuthStore.user = mockUser
      const { user } = useAuth()

      expect(user.value).toEqual(mockUser)
    })

    it('should return token from store', () => {
      mockAuthStore.token = 'test-token-123'
      const { token } = useAuth()

      expect(token.value).toBe('test-token-123')
    })

    it('should return isLoading from store', () => {
      mockAuthStore.isLoading = true
      const { isLoading } = useAuth()

      expect(isLoading.value).toBe(true)
    })

    it('should compute userName from user persona', () => {
      mockAuthStore.user = {
        persona: {
          nombre_completo: 'Juan Pérez'
        }
      }
      const { userName } = useAuth()

      expect(userName.value).toBe('Juan')
    })

    it('should return default userName when user is null', () => {
      mockAuthStore.user = null
      const { userName } = useAuth()

      expect(userName.value).toBe('Usuario')
    })

    it('should compute userEmail from user persona', () => {
      mockAuthStore.user = {
        persona: {
          correo_electronico: 'test@example.com'
        }
      }
      const { userEmail } = useAuth()

      expect(userEmail.value).toBe('test@example.com')
    })
  })

  describe('login', () => {
    it('should login successfully', async () => {
      mockAuthStore.login.mockResolvedValueOnce()
      const { login } = useAuth()

      const result = await login({ usuario: 'test', password: 'pass123' })

      expect(result.success).toBe(true)
      expect(mockAuthStore.login).toHaveBeenCalledWith({ usuario: 'test', password: 'pass123' })
    })

    it('should handle login error', async () => {
      const error = new Error('Invalid credentials')
      mockAuthStore.login.mockRejectedValueOnce(error)
      const { login } = useAuth()

      const result = await login({ usuario: 'test', password: 'wrong' })

      expect(result.success).toBe(false)
      expect(result.error).toBe('Invalid credentials')
    })
  })

  describe('logout', () => {
    it('should logout successfully', async () => {
      mockAuthStore.logout.mockResolvedValueOnce()
      const { logout } = useAuth()

      const result = await logout()

      expect(result.success).toBe(true)
      expect(mockAuthStore.logout).toHaveBeenCalled()
    })

    it('should handle logout error', async () => {
      const error = new Error('Logout failed')
      mockAuthStore.logout.mockRejectedValueOnce(error)
      const { logout } = useAuth()

      const result = await logout()

      expect(result.success).toBe(false)
      expect(result.error).toBe('Logout failed')
    })
  })

  describe('register', () => {
    it('should register successfully', async () => {
      mockAuthStore.register.mockResolvedValueOnce()
      const { register } = useAuth()

      const userData = {
        usuario: 'newuser',
        password: 'pass123',
        email: 'new@example.com'
      }

      const result = await register(userData)

      expect(result.success).toBe(true)
      expect(mockAuthStore.register).toHaveBeenCalledWith(userData)
    })

    it('should handle register error', async () => {
      const error = new Error('Registration failed')
      mockAuthStore.register.mockRejectedValueOnce(error)
      const { register } = useAuth()

      const result = await register({})

      expect(result.success).toBe(false)
      expect(result.error).toBe('Registration failed')
    })
  })

  describe('verifyToken', () => {
    it('should verify token successfully', async () => {
      mockAuthStore.verifyToken.mockResolvedValueOnce(true)
      const { verifyToken } = useAuth()

      const result = await verifyToken()

      expect(result).toBe(true)
      expect(mockAuthStore.verifyToken).toHaveBeenCalled()
    })

    it('should return false on verification error', async () => {
      mockAuthStore.verifyToken.mockRejectedValueOnce(new Error('Invalid token'))
      const { verifyToken } = useAuth()

      const result = await verifyToken()

      expect(result).toBe(false)
    })
  })

  describe('refreshUser', () => {
    it('should refresh user successfully', async () => {
      mockAuthStore.inicializar.mockResolvedValueOnce()
      const { refreshUser } = useAuth()

      const result = await refreshUser()

      expect(result.success).toBe(true)
      expect(mockAuthStore.inicializar).toHaveBeenCalled()
    })

    it('should handle refresh error', async () => {
      const error = new Error('Refresh failed')
      mockAuthStore.inicializar.mockRejectedValueOnce(error)
      const { refreshUser } = useAuth()

      const result = await refreshUser()

      expect(result.success).toBe(false)
      expect(result.error).toBe('Refresh failed')
    })
  })

  describe('hasRole', () => {
    it('should return true when user has role as string', () => {
      mockAuthStore.user = {
        roles: ['Administrador', 'Entrenador']
      }
      const { hasRole } = useAuth()

      expect(hasRole('Administrador')).toBe(true)
      expect(hasRole('Entrenador')).toBe(true)
      expect(hasRole('Deportista')).toBe(false)
    })

    it('should return true when user has role as object', () => {
      mockAuthStore.user = {
        roles: [
          { nombre_rol: 'Administrador' },
          { nombre_rol: 'Entrenador' }
        ]
      }
      const { hasRole } = useAuth()

      expect(hasRole('Administrador')).toBe(true)
      expect(hasRole('Deportista')).toBe(false)
    })

    it('should return false when user has no roles', () => {
      mockAuthStore.user = null
      const { hasRole } = useAuth()

      expect(hasRole('Administrador')).toBe(false)
    })
  })

  describe('hasAnyRole', () => {
    it('should return true if user has any of the roles', () => {
      mockAuthStore.user = {
        roles: ['Administrador']
      }
      const { hasAnyRole } = useAuth()

      expect(hasAnyRole(['Administrador', 'Entrenador'])).toBe(true)
      expect(hasAnyRole(['Deportista', 'Acudiente'])).toBe(false)
    })

    it('should return false when user has no roles', () => {
      mockAuthStore.user = null
      const { hasAnyRole } = useAuth()

      expect(hasAnyRole(['Administrador'])).toBe(false)
    })
  })
})
