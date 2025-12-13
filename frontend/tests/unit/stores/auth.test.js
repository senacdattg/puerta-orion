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

  describe('Load User Profile Detail', () => {
    it('should load user profile detail successfully', async () => {
      authService.getProfileDetail.mockResolvedValue({
        success: true,
        data: {
          id_usuario: 1,
          deportista: { id_deportista: 1 }
        }
      })

      const store = useAuthStore()
      store.token = mockToken
      const result = await store.loadUserProfileDetail()

      expect(result).toBe(true)
      expect(store.userDetail).toBeTruthy()
    })

    it('should handle profile detail error', async () => {
      authService.getProfileDetail.mockResolvedValue({
        success: false,
        error: 'Error loading detail'
      })

      const store = useAuthStore()
      store.token = mockToken
      const result = await store.loadUserProfileDetail()

      expect(result).toBe(false)
      expect(store.userDetail).toBeNull()
    })

    it('should return false when no token', async () => {
      const store = useAuthStore()
      const result = await store.loadUserProfileDetail()

      expect(result).toBe(false)
    })
  })

  describe('Refresh Role Options', () => {
    it('should refresh role options successfully', async () => {
      authService.getRoleOptions.mockResolvedValue({
        success: true,
        data: {
          roles_selector: { Deportista: true },
          rol_activo: 'Deportista',
          paneles: ['deportista']
        }
      })
      authService.getRolePermissions.mockResolvedValue({
        success: true,
        permisos: mockPermissions
      })

      const store = useAuthStore()
      store.user = mockUser
      const result = await store.refreshRoleOptions()

      expect(result.success).toBe(true)
      expect(store.rolesSelector).toEqual({ Deportista: true })
    })

    it('should handle refresh role options error', async () => {
      authService.getRoleOptions.mockResolvedValue({
        success: false,
        error: 'Error loading options'
      })

      const store = useAuthStore()
      const result = await store.refreshRoleOptions()

      expect(result.success).toBe(false)
    })
  })

  describe('Set Permissions By Role', () => {
    it('should set permissions for SuperAdmin', () => {
      const store = useAuthStore()
      store.user = {
        roles: ['SuperAdmin']
      }

      store.setPermissionsByRole()

      expect(store.permissions.length).toBeGreaterThan(0)
      expect(store.permissions).toContain('crear_evento')
      expect(store.permissions).toContain('gestionar_usuarios')
    })

    it('should set permissions for Administrador', () => {
      const store = useAuthStore()
      store.user = {
        roles: ['Administrador']
      }

      store.setPermissionsByRole()

      expect(store.permissions.length).toBeGreaterThan(0)
      expect(store.permissions).toContain('crear_evento')
    })

    it('should set permissions for Entrenador', () => {
      const store = useAuthStore()
      store.user = {
        roles: ['Entrenador']
      }

      store.setPermissionsByRole()

      expect(store.permissions).toContain('crear_evento')
      expect(store.permissions).toContain('editar_evento')
      expect(store.permissions).toContain('ver_evento')
    })

    it('should set permissions for other roles', () => {
      const store = useAuthStore()
      store.user = {
        roles: ['Deportista']
      }

      store.setPermissionsByRole()

      expect(store.permissions).toContain('ver_evento')
      expect(store.permissions).not.toContain('crear_evento')
    })

    it('should set empty permissions when no user', () => {
      const store = useAuthStore()
      store.user = null

      store.setPermissionsByRole()

      expect(store.permissions).toEqual([])
    })
  })

  describe('Load User Permissions', () => {
    it('should load user permissions for active role', async () => {
      authService.getRolePermissions.mockResolvedValue({
        success: true,
        permisos: mockPermissions
      })

      const store = useAuthStore()
      store.activeRole = 'Deportista'
      await store.loadUserPermissions()

      expect(store.permissions).toEqual(mockPermissions)
    })

    it('should load user permissions from getUserPermissions', async () => {
      authService.getUserPermissions.mockResolvedValue({
        success: true,
        permisos: mockPermissions
      })

      const store = useAuthStore()
      store.activeRole = null
      await store.loadUserPermissions()

      expect(store.permissions).toEqual(mockPermissions)
    })

    it('should fallback to setPermissionsByRole on error', async () => {
      authService.getUserPermissions.mockResolvedValue({
        success: false,
        error: 'Error loading permissions'
      })

      const store = useAuthStore()
      store.user = { roles: ['Deportista'] }
      store.activeRole = null

      await store.loadUserPermissions()

      // Should fallback to role-based permissions
      expect(store.permissions.length).toBeGreaterThan(0)
    })
  })

  describe('Computed Permission Properties', () => {
    it('should check puedeCrearEventos correctly', () => {
      const store = useAuthStore()
      store.permissions = ['crear_evento']

      expect(store.puedeCrearEventos).toBe(true)
    })

    it('should check puedeEditarEventos correctly', () => {
      const store = useAuthStore()
      store.permissions = ['editar_evento']

      expect(store.puedeEditarEventos).toBe(true)
    })

    it('should check puedeEliminarEventos correctly', () => {
      const store = useAuthStore()
      store.permissions = ['eliminar_evento']

      expect(store.puedeEliminarEventos).toBe(true)
    })

    it('should check puedeVerEventos correctly', () => {
      const store = useAuthStore()
      store.permissions = ['ver_evento']

      expect(store.puedeVerEventos).toBe(true)
    })

    it('should check puedeGestionarUsuarios correctly', () => {
      const store = useAuthStore()
      store.permissions = ['gestionar_usuarios']

      expect(store.puedeGestionarUsuarios).toBe(true)
    })

    it('should check puedeAccederPanelAdmin correctly', () => {
      const store = useAuthStore()
      store.permissions = ['acceso_panel_admin']

      expect(store.puedeAccederPanelAdmin).toBe(true)
    })
  })

  describe('Helper Functions', () => {
    it('should clearActiveRole correctly', () => {
      const store = useAuthStore()
      store.activeRole = 'Deportista'
      localStorage.setItem('activeRole', 'Deportista')

      store.clearActiveRole()

      expect(store.activeRole).toBeNull()
      expect(localStorage.getItem('activeRole')).toBeFalsy()
    })

    it('should updateUser correctly', () => {
      const store = useAuthStore()
      store.user = { id_usuario: 1, nombre: 'Original' }

      store.updateUser({ nombre: 'Updated' })

      expect(store.user.nombre).toBe('Updated')
      expect(localStorage.getItem('user')).toBeTruthy()
    })

    it('should loadUserProfileDetail return false when no token', async () => {
      const store = useAuthStore()
      store.token = null

      const result = await store.loadUserProfileDetail()

      // loadUserProfileDetail calls validarTokenParaCarga internally
      expect(result).toBe(false)
    })
  })

  describe('Initialization', () => {
    it('should initialize store correctly', async () => {
      authService.verifyToken.mockResolvedValue({
        success: true
      })
      authService.getProfile.mockResolvedValue({
        success: true,
        data: mockUser
      })

      localStorage.setItem('token', mockToken)
      localStorage.setItem('user', JSON.stringify(mockUser))

      const store = useAuthStore()
      await store.inicializar()

      expect(store.token).toBeTruthy()
    })

    it('should handle initialization with invalid token', async () => {
      authService.verifyToken.mockResolvedValue({
        success: false
      })

      localStorage.setItem('token', 'invalid-token')

      const store = useAuthStore()
      await store.inicializar()

      // Invalid token should be cleared
      expect(store.token).toBeFalsy()
    })
  })

  describe('User Roles Computed', () => {
    it('should compute userRoles with string roles', () => {
      const store = useAuthStore()
      store.user = {
        roles: ['Deportista', 'Acudiente']
      }

      expect(store.userRoles).toEqual(['Deportista', 'Acudiente'])
    })

    it('should compute userRoles with object roles', () => {
      const store = useAuthStore()
      store.user = {
        roles: [
          { nombre_rol: 'Deportista' },
          { rol: 'Acudiente' }
        ]
      }

      expect(store.userRoles).toEqual(['Deportista', 'Acudiente'])
    })

    it('should compute role checks correctly', () => {
      const store = useAuthStore()
      store.user = {
        roles: ['Deportista', 'Acudiente', 'Entrenador']
      }

      expect(store.isDeportista).toBe(true)
      expect(store.isAcudiente).toBe(true)
      expect(store.isEntrenador).toBe(true)
      expect(store.isAdmin).toBe(false)
    })

    it('should check hasRole correctly', () => {
      const store = useAuthStore()
      store.user = {
        roles: ['Deportista']
      }

      expect(store.hasRole('Deportista')).toBe(true)
      expect(store.hasRole('Administrador')).toBe(false)
    })
  })

  describe('Esta Autenticado Alias', () => {
    it('should compute estaAutenticado correctly', () => {
      const store = useAuthStore()
      expect(store.estaAutenticado).toBe(false)

      store.token = mockToken
      expect(store.estaAutenticado).toBe(true)
    })
  })

  describe('Load Permissions For Role Edge Cases', () => {
    it('should handle empty role name', async () => {
      const store = useAuthStore()
      await store.loadPermissionsForRole('')

      expect(store.permissions).toEqual([])
    })

    it('should handle null role name', async () => {
      const store = useAuthStore()
      await store.loadPermissionsForRole(null)

      expect(store.permissions).toEqual([])
    })

    it('should handle undefined role name', async () => {
      const store = useAuthStore()
      await store.loadPermissionsForRole(undefined)

      expect(store.permissions).toEqual([])
    })
  })

  describe('Set Active Role Edge Cases', () => {
    it('should handle setActiveRole with forzarCambio', async () => {
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
      store.activeRole = 'Acudiente'

      const result = await store.setActiveRole('Deportista', true)

      expect(result.success).toBe(true)
    })

    it('should not change role when forzarCambio is false and role is same', async () => {
      const store = useAuthStore()
      store.user = mockUser
      store.activeRole = 'Deportista'

      const result = await store.setActiveRole('Deportista', false)

      // Should return success without calling activateRole if role is already active
      expect(result.success).toBe(true)
    })
  })
})

