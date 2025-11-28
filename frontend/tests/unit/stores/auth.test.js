import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import authService from '@/services/authService'
import { mockUser, mockToken, mockLoginCredentials, mockLoginResponse, mockPermissions } from '../../fixtures/auth'

// Mock authService
vi.mock('@/services/authService', () => ({
  default: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    verifyToken: vi.fn(),
    getProfile: vi.fn(),
    getProfileDetail: vi.fn(),
    getUserPermissions: vi.fn(),
    getRolePermissions: vi.fn(),
    getRoleOptions: vi.fn(),
    activateRole: vi.fn()
  }
}))

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('Initial State', () => {
    it('should initialize with default values', () => {
      const store = useAuthStore()
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should load token from localStorage', () => {
      localStorage.setItem('token', mockToken)
      const store = useAuthStore()
      // Token is loaded in the store constructor via ref(localStorage.getItem('token') || null)
      // Since we're using a mock, we need to check if it's set
      expect(store.token).toBeTruthy()
    })
  })

  describe('Login', () => {
    it('should login successfully', async () => {
      authService.login.mockResolvedValue(mockLoginResponse)
      
      const store = useAuthStore()
      const result = await store.login(mockLoginCredentials)

      expect(result.success).toBe(true)
      expect(store.token).toBeTruthy()
      expect(store.user).toEqual(mockUser)
      expect(store.isAuthenticated).toBe(true)
      expect(localStorage.getItem('token')).toBeTruthy()
    })

    it('should handle login error', async () => {
      authService.login.mockResolvedValue({
        success: false,
        error: 'Invalid credentials'
      })

      const store = useAuthStore()
      const result = await store.login(mockLoginCredentials)

      expect(result.success).toBe(false)
      expect(store.error).toBe('Invalid credentials')
      expect(store.isAuthenticated).toBe(false)
    })

    it('should set loading state during login', async () => {
      let resolveLogin
      const loginPromise = new Promise(resolve => {
        resolveLogin = resolve
      })
      authService.login.mockReturnValue(loginPromise)

      const store = useAuthStore()
      const loginPromise2 = store.login(mockLoginCredentials)

      expect(store.isLoading).toBe(true)
      
      resolveLogin(mockLoginResponse)
      await loginPromise2

      expect(store.isLoading).toBe(false)
    })
  })

  describe('Logout', () => {
    it('should logout successfully', async () => {
      authService.logout.mockResolvedValue({ success: true })
      
      const store = useAuthStore()
      store.token = mockToken
      store.user = mockUser
      localStorage.setItem('token', mockToken)

      await store.logout()

      expect(store.token).toBeNull()
      expect(store.user).toBeNull()
      expect(store.isAuthenticated).toBe(false)
      // localStorage is cleared in logout
      expect(localStorage.getItem('token')).toBeFalsy()
    })

    it('should clear permissions on logout', async () => {
      const store = useAuthStore()
      store.permissions = mockPermissions
      store.token = mockToken

      await store.logout()

      expect(store.permissions).toEqual([])
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

      authService.register.mockResolvedValue({
        success: true,
        data: { id: 1 }
      })

      const store = useAuthStore()
      const result = await store.register(registerData)

      expect(result.success).toBe(true)
      expect(store.isLoading).toBe(false)
    })

    it('should handle register error', async () => {
      authService.register.mockResolvedValue({
        success: false,
        error: 'Email already exists'
      })

      const store = useAuthStore()
      const result = await store.register({})

      expect(result.success).toBe(false)
      expect(store.error).toBe('Email already exists')
    })
  })

  describe('Verify Token', () => {
    it('should verify valid token', async () => {
      authService.verifyToken.mockResolvedValue({
        success: true
      })
      authService.getProfile.mockResolvedValue({
        success: true,
        data: mockUser
      })

      const store = useAuthStore()
      store.token = mockToken
      const result = await store.verifyToken()

      expect(result).toBe(true)
    })

    it('should return false for invalid token', async () => {
      authService.verifyToken.mockResolvedValue({
        success: false,
        message: 'Token inválido'
      })

      const store = useAuthStore()
      store.token = 'invalid-token'
      const result = await store.verifyToken()

      expect(result).toBe(false)
      expect(store.token).toBeNull()
    })

    it('should return false when no token exists', async () => {
      const store = useAuthStore()
      const result = await store.verifyToken()

      expect(result).toBe(false)
    })
  })

  describe('Load User Profile', () => {
    it('should load user profile successfully', async () => {
      authService.getProfile.mockResolvedValue({
        success: true,
        data: mockUser
      })

      const store = useAuthStore()
      store.token = mockToken
      const result = await store.loadUserProfile()

      expect(result).toBe(true)
      expect(store.user).toEqual(mockUser)
    })

    it('should logout on profile load error', async () => {
      authService.getProfile.mockResolvedValue({
        success: false,
        error: 'Unauthorized'
      })

      const store = useAuthStore()
      store.token = mockToken
      
      const result = await store.loadUserProfile()

      expect(result).toBe(false)
      // logout is called internally, verify state is cleared
      expect(store.token).toBeFalsy()
    })
  })

  describe('Load Permissions', () => {
    it('should load permissions for active role', async () => {
      authService.getRolePermissions.mockResolvedValue({
        success: true,
        permisos: mockPermissions
      })

      const store = useAuthStore()
      store.activeRole = 'Deportista'
      await store.loadPermissionsForRole('Deportista')

      expect(store.permissions).toEqual(mockPermissions)
    })

    it('should handle permission load error', async () => {
      authService.getRolePermissions.mockResolvedValue({
        success: false,
        error: 'Error loading permissions'
      })

      const store = useAuthStore()
      await store.loadPermissionsForRole('Deportista')

      expect(store.permissions).toEqual([])
    })
  })

  describe('Set Active Role', () => {
    it('should set active role successfully', async () => {
      authService.activateRole.mockResolvedValue({
        success: true,
        data: {
          rol_activo: 'Deportista',
          roles_selector: { Deportista: true },
          paneles: ['deportista']
        }
      })
      authService.getRolePermissions.mockResolvedValue({
        success: true,
        permisos: mockPermissions
      })

      const store = useAuthStore()
      store.user = mockUser
      const result = await store.setActiveRole('Deportista')

      expect(result.success).toBe(true)
      expect(store.activeRole).toBeTruthy()
      expect(localStorage.getItem('activeRole')).toBeTruthy()
    })

    it('should handle role activation error', async () => {
      authService.activateRole.mockResolvedValue({
        success: false,
        error: 'Invalid role'
      })

      const store = useAuthStore()
      const result = await store.setActiveRole('InvalidRole')

      expect(result.success).toBe(false)
      // Error is returned in result, not stored in store.error for this case
      expect(result.error).toBeTruthy()
    })
  })

  describe('Computed Properties', () => {
    it('should compute isAuthenticated correctly', () => {
      const store = useAuthStore()
      expect(store.isAuthenticated).toBe(false)

      store.token = mockToken
      expect(store.isAuthenticated).toBe(true)
    })

    it('should compute userRoles correctly', () => {
      const store = useAuthStore()
      store.user = {
        roles: ['Deportista', 'Acudiente']
      }

      expect(store.userRoles).toEqual(['Deportista', 'Acudiente'])
    })

    it('should compute hasRole correctly', () => {
      const store = useAuthStore()
      store.user = {
        roles: ['Deportista']
      }

      expect(store.hasRole('Deportista')).toBe(true)
      expect(store.hasRole('Administrador')).toBe(false)
    })

    it('should compute role checks correctly', () => {
      const store = useAuthStore()
      store.user = {
        roles: ['Deportista']
      }

      expect(store.isDeportista).toBe(true)
      expect(store.isAdmin).toBe(false)
    })
  })

  describe('Has Permission', () => {
    it('should check permission correctly', () => {
      const store = useAuthStore()
      store.permissions = ['ver_evento', 'editar_perfil']

      expect(store.hasPermission('ver_evento')).toBe(true)
      expect(store.hasPermission('crear_evento')).toBe(false)
    })
  })

  describe('Clear Error', () => {
    it('should clear error', () => {
      const store = useAuthStore()
      store.error = 'Some error'
      store.clearError()
      expect(store.error).toBeNull()
    })
  })
})

