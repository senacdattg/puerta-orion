import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useUserRole, navigationConfig } from '@/composables/useUserRole'
import { useAuthStore } from '@/stores/auth'

// Mock the auth store
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

describe('useUserRole', () => {
  let mockAuthStore

  beforeEach(() => {
    mockAuthStore = {
      rolesSelector: {},
      userRoles: [],
      activeRole: null,
      panels: [],
      user: {
        nombre: 'Test User'
      }
    }

    useAuthStore.mockReturnValue(mockAuthStore)
  })

  describe('availableRoles', () => {
    it('should return roles from rolesSelector when available', () => {
      mockAuthStore.rolesSelector = {
        Administrador: true,
        Entrenador: true,
        Deportista: false
      }

      const { availableRoles } = useUserRole()

      expect(availableRoles.value).toEqual(['Administrador', 'Entrenador'])
    })

    it('should return roles from userRoles when rolesSelector is empty', () => {
      mockAuthStore.rolesSelector = {}
      mockAuthStore.userRoles = ['Deportista', 'Acudiente']

      const { availableRoles } = useUserRole()

      expect(availableRoles.value).toEqual(['Deportista', 'Acudiente'])
    })

    it('should return default role when no roles available', () => {
      mockAuthStore.rolesSelector = {}
      mockAuthStore.userRoles = []

      const { availableRoles } = useUserRole()

      expect(availableRoles.value).toEqual(['Usuario'])
    })
  })

  describe('userRole', () => {
    it('should return activeRole when set', () => {
      mockAuthStore.activeRole = 'Administrador'

      const { userRole } = useUserRole()

      expect(userRole.value).toBe('Administrador')
    })

    it('should return first available role when activeRole is not set', () => {
      mockAuthStore.activeRole = null
      mockAuthStore.userRoles = ['Deportista', 'Acudiente']

      const { userRole } = useUserRole()

      expect(userRole.value).toBe('Deportista')
    })

    it('should return default role when no roles available', () => {
      mockAuthStore.activeRole = null
      mockAuthStore.userRoles = []

      const { userRole } = useUserRole()

      expect(userRole.value).toBe('Usuario')
    })
  })

  describe('isAdminOrCoach', () => {
    it('should return true for Administrador', () => {
      mockAuthStore.activeRole = 'Administrador'

      const { isAdminOrCoach } = useUserRole()

      expect(isAdminOrCoach.value).toBe(true)
    })

    it('should return true for SuperAdmin', () => {
      mockAuthStore.activeRole = 'SuperAdmin'

      const { isAdminOrCoach } = useUserRole()

      expect(isAdminOrCoach.value).toBe(true)
    })

    it('should return true for Entrenador', () => {
      mockAuthStore.activeRole = 'Entrenador'

      const { isAdminOrCoach } = useUserRole()

      expect(isAdminOrCoach.value).toBe(true)
    })

    it('should return false for Deportista', () => {
      mockAuthStore.activeRole = 'Deportista'

      const { isAdminOrCoach } = useUserRole()

      expect(isAdminOrCoach.value).toBe(false)
    })
  })

  describe('isDeportista', () => {
    it('should return true for Deportista role', () => {
      mockAuthStore.activeRole = 'Deportista'

      const { isDeportista } = useUserRole()

      expect(isDeportista.value).toBe(true)
    })

    it('should return false for other roles', () => {
      mockAuthStore.activeRole = 'Administrador'

      const { isDeportista } = useUserRole()

      expect(isDeportista.value).toBe(false)
    })
  })

  describe('isAcudiente', () => {
    it('should return true for Acudiente role', () => {
      mockAuthStore.activeRole = 'Acudiente'

      const { isAcudiente } = useUserRole()

      expect(isAcudiente.value).toBe(true)
    })

    it('should return false for other roles', () => {
      mockAuthStore.activeRole = 'Deportista'

      const { isAcudiente } = useUserRole()

      expect(isAcudiente.value).toBe(false)
    })
  })

  describe('allowedPanels', () => {
    it('should return allowed panels from store', () => {
      mockAuthStore.panels = [
        { module: 'calendario', allowed: true },
        { module: 'galeria', allowed: false },
        { module: 'mensualidades', allowed: true }
      ]

      const { allowedPanels } = useUserRole()

      expect(allowedPanels.value.calendario).toBe(true)
      expect(allowedPanels.value.galeria).toBe(false)
      expect(allowedPanels.value.mensualidades).toBe(true)
    })

    it('should default to allowed when allowed is not specified', () => {
      mockAuthStore.panels = [
        { module: 'calendario' }
      ]

      const { allowedPanels } = useUserRole()

      expect(allowedPanels.value.calendario).toBe(true)
    })
  })

  describe('filteredNavigation', () => {
    it('should filter navigation by user roles', () => {
      mockAuthStore.userRoles = ['Administrador']

      const { filteredNavigation } = useUserRole()

      const adminItems = filteredNavigation.value.filter(item =>
        item.roles.includes('Administrador')
      )

      expect(adminItems.length).toBeGreaterThan(0)
    })

    it('should filter out items when panel is not allowed', () => {
      mockAuthStore.userRoles = ['Administrador']
      mockAuthStore.panels = [
        { module: 'calendario', allowed: false }
      ]

      const { filteredNavigation } = useUserRole()

      const calendarioItem = filteredNavigation.value.find(item => item.id === 'calendario')

      expect(calendarioItem).toBeUndefined()
    })

    it('should include items when no roles but panel is allowed', () => {
      mockAuthStore.userRoles = []
      mockAuthStore.panels = [
        { module: 'calendario', allowed: true }
      ]

      const { filteredNavigation } = useUserRole()

      const calendarioItem = filteredNavigation.value.find(item => item.id === 'calendario')

      expect(calendarioItem).toBeDefined()
    })
  })

  describe('welcomeMessage', () => {
    it('should return admin welcome message for admin/coach', () => {
      mockAuthStore.activeRole = 'Administrador'
      mockAuthStore.user = { nombre: 'Admin User' }

      const { welcomeMessage } = useUserRole()

      expect(welcomeMessage.value.title).toContain('Admin User')
      expect(welcomeMessage.value.description).toContain('Gestiona el club deportivo')
    })

    it('should return default welcome message for other roles', () => {
      mockAuthStore.activeRole = 'Deportista'
      mockAuthStore.user = { nombre: 'Deportista User' }

      const { welcomeMessage } = useUserRole()

      expect(welcomeMessage.value.title).toContain('Deportista User')
      expect(welcomeMessage.value.description).toContain('Accede al calendario')
    })
  })

  describe('hasRole', () => {
    it('should return true when user has role', () => {
      mockAuthStore.userRoles = ['Administrador', 'Entrenador']

      const { hasRole } = useUserRole()

      expect(hasRole('Administrador')).toBe(true)
      expect(hasRole('Entrenador')).toBe(true)
      expect(hasRole('Deportista')).toBe(false)
    })

    it('should handle role objects', () => {
      mockAuthStore.userRoles = [
        { nombre_rol: 'Administrador' },
        { nombre_rol: 'Entrenador' }
      ]

      const { hasRole } = useUserRole()

      expect(hasRole('Administrador')).toBe(true)
    })
  })

  describe('canAccessRoute', () => {
    it('should return true when user has required role for route', () => {
      mockAuthStore.userRoles = ['Administrador']

      const { canAccessRoute } = useUserRole()

      expect(canAccessRoute('/admin-manager')).toBe(true)
    })

    it('should return false when user does not have required role', () => {
      mockAuthStore.userRoles = ['Deportista']

      const { canAccessRoute } = useUserRole()

      expect(canAccessRoute('/admin-manager')).toBe(false)
    })

    it('should return true for routes not in navigation config', () => {
      const { canAccessRoute } = useUserRole()

      expect(canAccessRoute('/unknown-route')).toBe(true)
    })

    it('should check panel permissions when no roles', () => {
      mockAuthStore.userRoles = []
      mockAuthStore.panels = [
        { module: 'calendario', allowed: true }
      ]

      const { canAccessRoute } = useUserRole()

      expect(canAccessRoute('/calendario')).toBe(true)
    })
  })
})

describe('navigationConfig', () => {
  it('should have all required navigation items', () => {
    const expectedIds = [
      'registro-deportista',
      'registro-acudiente',
      'completar-perfil',
      'calendario',
      'galeria',
      'admin',
      'deportistas',
      'mensualidades'
    ]

    const configIds = navigationConfig.map(item => item.id)

    expectedIds.forEach(id => {
      expect(configIds).toContain(id)
    })
  })

  it('should have required properties for each item', () => {
    navigationConfig.forEach(item => {
      expect(item).toHaveProperty('id')
      expect(item).toHaveProperty('title')
      expect(item).toHaveProperty('route')
      expect(item).toHaveProperty('icon')
      expect(item).toHaveProperty('colorClass')
      expect(item).toHaveProperty('roles')
      expect(Array.isArray(item.roles)).toBe(true)
    })
  })
})

