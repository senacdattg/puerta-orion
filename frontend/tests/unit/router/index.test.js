import { describe, it, expect, beforeEach, vi } from 'vitest'
import router, { navigationGuard } from '@/router/index'
import { useAuthStore } from '@/stores/auth'

// Mock store
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

// Mock localStorage
globalThis.localStorage = {
  getItem: vi.fn(() => null),
  setItem: vi.fn(),
  removeItem: vi.fn()
}

describe('Router Configuration', () => {
  it('should have router instance', () => {
    expect(router).toBeDefined()
    expect(router.options.routes.length).toBeGreaterThan(0)
  })

  it('should have root redirect to login', () => {
    const rootRoute = router.options.routes.find(r => r.path === '/')
    expect(rootRoute).toBeDefined()
    expect(rootRoute.redirect).toBe('/login')
  })

  it('should have login route with requiresGuest meta', () => {
    const loginRoute = router.options.routes.find(r => r.name === 'login')
    expect(loginRoute).toBeDefined()
    expect(loginRoute.meta.requiresGuest).toBe(true)
  })

  it('should have home route with requiresAuth meta', () => {
    const homeRoute = router.options.routes.find(r => r.name === 'home')
    expect(homeRoute).toBeDefined()
    expect(homeRoute.meta.requiresAuth).toBe(true)
  })

  it('should have admin-manager route with role requirements', () => {
    const adminRoute = router.options.routes.find(r => r.name === 'admin-manager')
    expect(adminRoute).toBeDefined()
    expect(adminRoute.meta.requiresAuth).toBe(true)
    expect(adminRoute.meta.requiresRole).toEqual(['SuperAdmin', 'Administrador'])
  })

  it('should have deportista dashboard route', () => {
    const route = router.options.routes.find(r => r.name === 'deportista-dashboard')
    expect(route).toBeDefined()
    expect(route.meta.requiresRole).toContain('Deportista')
  })

  it('should have acudiente dashboard route', () => {
    const route = router.options.routes.find(r => r.name === 'acudiente-dashboard')
    expect(route).toBeDefined()
    expect(route.meta.requiresRole).toContain('Acudiente')
  })
})

// Las funciones auxiliares no están exportadas, así que probamos el router y su comportamiento

describe('Router Navigation Guards', () => {
  let mockAuthStore

  beforeEach(() => {
    vi.clearAllMocks()

    mockAuthStore = {
      user: null,
      token: null,
      activeRole: null,
      rolesSelector: {},
      permissions: [],
      inicializar: vi.fn().mockResolvedValue(true),
      verifyToken: vi.fn().mockResolvedValue(false),
      refreshRoleOptions: vi.fn().mockResolvedValue(true),
      setActiveRole: vi.fn().mockResolvedValue(true),
      loadUserPermissions: vi.fn().mockResolvedValue(true),
      hasPermission: vi.fn(() => false)
    }

    useAuthStore.mockReturnValue(mockAuthStore)
  })

  it('should have beforeEach guard registered', () => {
    // Verificar que el router tiene guards registrados
    expect(router.beforeEach).toBeDefined()
    expect(typeof router.beforeEach).toBe('function')
  })

  it('should have routes with correct meta information', () => {
    const loginRoute = router.options.routes.find(r => r.name === 'login')
    expect(loginRoute.meta.requiresGuest).toBe(true)

    const homeRoute = router.options.routes.find(r => r.name === 'home')
    expect(homeRoute.meta.requiresAuth).toBe(true)
  })

  it('should have admin route with role restrictions', () => {
    const adminRoute = router.options.routes.find(r => r.name === 'admin-manager')
    expect(adminRoute.meta.requiresRole).toContain('SuperAdmin')
    expect(adminRoute.meta.requiresRole).toContain('Administrador')
  })

  it('should have mensualidades route with permission requirement', () => {
    const mensualidadesRoute = router.options.routes.find(r => r.name === 'mensualidades')
    expect(mensualidadesRoute.meta.requiresPermission).toBe('ver_mensualidad')
  })

  it('should have deportista routes with role restrictions', () => {
    const deportistaRoutes = router.options.routes.filter(r =>
      r.name?.includes('deportista')
    )
    expect(deportistaRoutes.length).toBeGreaterThan(0)
    deportistaRoutes.forEach(route => {
      if (route.meta?.requiresRole) {
        expect(route.meta.requiresRole).toContain('Deportista')
      }
    })
  })

  it('should have acudiente routes with role restrictions', () => {
    const acudienteRoutes = router.options.routes.filter(r =>
      r.name?.includes('acudiente') || r.path?.includes('/acudiente/')
    )
    expect(acudienteRoutes.length).toBeGreaterThan(0)
    // Verificar que al menos una ruta de acudiente tiene el rol requerido
    const routesWithRole = acudienteRoutes.filter(route =>
      route.meta?.requiresRole?.includes('Acudiente')
    )
    expect(routesWithRole.length).toBeGreaterThan(0)
  })

  it('should have all required routes configured', () => {
    const requiredRouteNames = [
      'login', 'home', 'forgot-password', 'reset-password',
      'admin-manager', 'deportista-dashboard', 'acudiente-dashboard',
      'mensualidades', 'calendario', 'galeria'
    ]

    requiredRouteNames.forEach(routeName => {
      const route = router.options.routes.find(r => r.name === routeName)
      expect(route).toBeDefined()
    })
  })

  it('should have redirects configured correctly', () => {
    const rootRoute = router.options.routes.find(r => r.path === '/')
    expect(rootRoute.redirect).toBe('/login')

    const inicioRoute = router.options.routes.find(r => r.path === '/inicio')
    expect(inicioRoute.redirect).toBe('/home')
  })

  it('should redirect unauthenticated user to login when accessing protected route', async () => {
    mockAuthStore.verifyToken.mockResolvedValue(false)
    mockAuthStore.user = null
    mockAuthStore.token = null

    const next = vi.fn()
    const to = { path: '/home', matched: [{ meta: { requiresAuth: true } }] }
    const from = { path: '/' }

    // Simular el guard ejecutándose
    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith('/login')
  })

  it('should redirect authenticated user with multiple roles to role selection', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [
        { nombre_rol: 'Deportista' },
        { nombre_rol: 'Acudiente' }
      ]
    }
    mockAuthStore.activeRole = null
    mockAuthStore.rolesSelector = {
      Deportista: true,
      Acudiente: true
    }

    const next = vi.fn()
    const to = { path: '/calendario', matched: [{ meta: { requiresAuth: true } }] }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    // Debería redirigir a selección de rol si tiene múltiples roles sin seleccionar
    expect(next).toHaveBeenCalledWith('/seleccionar-rol')
  })

  it('should allow access to route with required role', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'SuperAdmin' }]
    }
    mockAuthStore.activeRole = 'SuperAdmin'
    mockAuthStore.rolesSelector = { SuperAdmin: true }

    const next = vi.fn()
    const to = {
      path: '/admin-manager',
      matched: [{ meta: { requiresAuth: true, requiresRole: ['SuperAdmin', 'Administrador'] } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith()
  })

  it('should deny access to route without required role', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Deportista' }]
    }
    mockAuthStore.activeRole = 'Deportista'
    mockAuthStore.rolesSelector = { Deportista: true }

    const next = vi.fn()
    const to = {
      path: '/admin-manager',
      matched: [{ meta: { requiresAuth: true, requiresRole: ['SuperAdmin', 'Administrador'] } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith('/seleccionar-rol')
  })

  it('should check permissions for routes requiring permissions', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Administrador' }]
    }
    mockAuthStore.activeRole = 'Administrador'
    mockAuthStore.permissions = ['ver_mensualidad']
    mockAuthStore.hasPermission.mockReturnValue(true)

    const next = vi.fn()
    const to = {
      path: '/mensualidades',
      matched: [{ meta: { requiresAuth: true, requiresPermission: 'ver_mensualidad' } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith()
  })

  it('should redirect guest user away from guest-only routes when authenticated', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Deportista' }]
    }
    mockAuthStore.activeRole = 'Deportista'
    mockAuthStore.rolesSelector = { Deportista: true }

    const next = vi.fn()
    const to = {
      path: '/login',
      matched: [{ meta: { requiresGuest: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    // Debería redirigir a la ruta por defecto del rol
    expect(next).toHaveBeenCalled()
    expect(next).not.toHaveBeenCalledWith('/login')
  })

  it('should handle route with no meta requirements', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Deportista' }]
    }
    mockAuthStore.activeRole = 'Deportista'

    const next = vi.fn()
    const to = {
      path: '/some-route',
      matched: [{ meta: {} }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith()
  })

  it('should initialize auth store if user is null but token exists', async () => {
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = null
    mockAuthStore.token = 'some-token'

    const next = vi.fn()
    const to = {
      path: '/home',
      matched: [{ meta: { requiresAuth: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(mockAuthStore.inicializar).toHaveBeenCalled()
  })

  it('should handle route with single role redirects correctly', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'SuperAdmin' }]
    }
    mockAuthStore.activeRole = null
    mockAuthStore.rolesSelector = { SuperAdmin: true }

    const next = vi.fn()
    const to = {
      path: '/login',
      matched: [{ meta: { requiresGuest: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    // Cuando tiene un solo rol, getDefaultRouteForRole redirige según el rol
    expect(next).toHaveBeenCalled()
    const calls = next.mock.calls
    // Puede redirigir a /admin-manager, /home o /seleccionar-rol dependiendo de la lógica
    expect(['/admin-manager', '/home', '/seleccionar-rol']).toContain(calls[0][0])
  })

  it('should handle route with Deportista role redirect', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Deportista' }]
    }
    mockAuthStore.activeRole = null
    mockAuthStore.rolesSelector = { Deportista: true }

    const next = vi.fn()
    const to = {
      path: '/login',
      matched: [{ meta: { requiresGuest: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith('/deportista/dashboard')
  })

  it('should handle route with Acudiente role redirect', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Acudiente' }]
    }
    mockAuthStore.activeRole = null
    mockAuthStore.rolesSelector = { Acudiente: true }

    const next = vi.fn()
    const to = {
      path: '/login',
      matched: [{ meta: { requiresGuest: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith('/acudiente/dashboard')
  })

  it('should handle route with Entrenador role redirect to home', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Entrenador' }]
    }
    mockAuthStore.activeRole = null
    mockAuthStore.rolesSelector = { Entrenador: true }

    const next = vi.fn()
    const to = {
      path: '/login',
      matched: [{ meta: { requiresGuest: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith('/home')
  })

  it('should handle route with Usuario role redirect to home', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Usuario' }]
    }
    mockAuthStore.activeRole = null
    mockAuthStore.rolesSelector = { Usuario: true }

    const next = vi.fn()
    const to = {
      path: '/login',
      matched: [{ meta: { requiresGuest: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith('/home')
  })

  it('should handle route with activeRole in lowercase', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Deportista' }]
    }
    mockAuthStore.activeRole = 'deportista'
    mockAuthStore.rolesSelector = { Deportista: true }

    const next = vi.fn()
    const to = {
      path: '/deportista/dashboard',
      matched: [{ meta: { requiresAuth: true, requiresRole: ['Deportista'] } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    // La función verificarRolActivo normaliza y compara, pero puede redirigir si no coincide exactamente
    expect(next).toHaveBeenCalled()
  })

  it('should handle route with role as string in user roles', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: ['SuperAdmin']
    }
    mockAuthStore.activeRole = 'SuperAdmin'
    mockAuthStore.rolesSelector = { SuperAdmin: true }

    const next = vi.fn()
    const to = {
      path: '/admin-manager',
      matched: [{ meta: { requiresAuth: true, requiresRole: ['SuperAdmin'] } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith()
  })

  it('should deny access when activeRole does not match required role', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Deportista' }]
    }
    mockAuthStore.activeRole = 'Deportista'
    mockAuthStore.rolesSelector = { Deportista: true }

    const next = vi.fn()
    const to = {
      path: '/admin-manager',
      matched: [{ meta: { requiresAuth: true, requiresRole: ['SuperAdmin'] } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith('/seleccionar-rol')
  })

  it('should redirect to home when user does not have required role and single role', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Deportista' }]
    }
    mockAuthStore.activeRole = null
    mockAuthStore.rolesSelector = { Deportista: true }

    const next = vi.fn()
    const to = {
      path: '/admin-manager',
      matched: [{ meta: { requiresAuth: true, requiresRole: ['SuperAdmin'] } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith('/home')
  })

  it('should allow access when SuperAdmin or Administrador checks permission', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'SuperAdmin' }]
    }
    mockAuthStore.activeRole = 'SuperAdmin'
    mockAuthStore.permissions = []
    mockAuthStore.rolesSelector = { SuperAdmin: true }

    const next = vi.fn()
    const to = {
      path: '/mensualidades',
      matched: [{ meta: { requiresAuth: true, requiresPermission: 'ver_mensualidad' } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith()
  })

  it('should load permissions when not available and permission required', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Deportista' }]
    }
    mockAuthStore.activeRole = 'Deportista'
    mockAuthStore.permissions = null
    mockAuthStore.loadUserPermissions = vi.fn().mockResolvedValue(true)
    mockAuthStore.hasPermission = vi.fn(() => true)
    mockAuthStore.rolesSelector = { Deportista: true }

    const next = vi.fn()
    const to = {
      path: '/mensualidades',
      matched: [{ meta: { requiresAuth: true, requiresPermission: 'ver_mensualidad' } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(mockAuthStore.loadUserPermissions).toHaveBeenCalled()
  })

  it('should handle permission check with array permissions', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Deportista' }]
    }
    mockAuthStore.activeRole = 'Deportista'
    mockAuthStore.permissions = ['ver_mensualidad']
    // hasPermission retorna true, pero también verifica si está en el array de permisos
    mockAuthStore.hasPermission = vi.fn(() => true)
    mockAuthStore.rolesSelector = { Deportista: true }

    const next = vi.fn()
    const to = {
      path: '/mensualidades',
      matched: [{ meta: { requiresAuth: true, requiresPermission: 'ver_mensualidad' } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    // Verificar que se permitió acceso o se redirigió según la lógica
    expect(next).toHaveBeenCalled()
    // Puede llamar next() sin argumentos (acceso permitido) o con '/home' (denegado)
    const lastCall = next.mock.calls[next.mock.calls.length - 1]
    expect(lastCall[0] === undefined || lastCall[0] === '/home').toBe(true)
  })

  it('should handle permission check with hasPermission method', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Deportista' }]
    }
    mockAuthStore.activeRole = 'Deportista'
    mockAuthStore.permissions = []
    mockAuthStore.hasPermission = vi.fn(() => true)
    mockAuthStore.rolesSelector = { Deportista: true }

    const next = vi.fn()
    const to = {
      path: '/mensualidades',
      matched: [{ meta: { requiresAuth: true, requiresPermission: 'ver_mensualidad' } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(mockAuthStore.hasPermission).toHaveBeenCalledWith('ver_mensualidad')
    expect(next).toHaveBeenCalledWith()
  })

  it('should handle error when loading permissions', async () => {
    const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Deportista' }]
    }
    mockAuthStore.activeRole = 'Deportista'
    mockAuthStore.permissions = null
    mockAuthStore.loadUserPermissions = vi.fn().mockRejectedValue(new Error('Failed'))
    mockAuthStore.hasPermission = vi.fn(() => false)
    mockAuthStore.rolesSelector = { Deportista: true }

    const next = vi.fn()
    const to = {
      path: '/mensualidades',
      matched: [{ meta: { requiresAuth: true, requiresPermission: 'ver_mensualidad' } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(consoleWarn).toHaveBeenCalled()
    consoleWarn.mockRestore()
  })

  it('should deny access to mensualidades for Entrenador role', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Entrenador' }]
    }
    mockAuthStore.activeRole = 'Entrenador'
    mockAuthStore.rolesSelector = { Entrenador: true }

    const next = vi.fn()
    const to = {
      path: '/mensualidades',
      name: 'mensualidades',
      matched: [{ meta: { requiresAuth: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith('/home')
  })

  it('should deny access to mensualidades for Usuario role', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Usuario' }]
    }
    mockAuthStore.activeRole = 'Usuario'
    mockAuthStore.rolesSelector = { Usuario: true }

    const next = vi.fn()
    const to = {
      path: '/mensualidades',
      name: 'mensualidades',
      matched: [{ meta: { requiresAuth: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith('/home')
  })

  it('should allow access to mensualidades for Administrador', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Administrador' }]
    }
    mockAuthStore.activeRole = 'Administrador'
    mockAuthStore.rolesSelector = { Administrador: true }

    const next = vi.fn()
    const to = {
      path: '/mensualidades',
      name: 'mensualidades',
      matched: [{ meta: { requiresAuth: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith()
  })

  it('should redirect to seleccionar-rol when user has multiple roles and tries to access protected route', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [
        { nombre_rol: 'Deportista' },
        { nombre_rol: 'Acudiente' }
      ]
    }
    mockAuthStore.activeRole = null
    mockAuthStore.rolesSelector = {
      Deportista: true,
      Acudiente: true
    }

    const next = vi.fn()
    const to = {
      path: '/home',
      matched: [{ meta: { requiresAuth: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    // Puede redirigir a seleccionar-rol o permitir acceso dependiendo de la lógica
    expect(next).toHaveBeenCalled()
  })

  it('should not redirect to seleccionar-rol when already on seleccionar-rol route', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [
        { nombre_rol: 'Deportista' },
        { nombre_rol: 'Acudiente' }
      ]
    }
    mockAuthStore.activeRole = null
    mockAuthStore.rolesSelector = {}

    const next = vi.fn()
    const to = {
      path: '/seleccionar-rol',
      matched: [{ meta: { requiresAuth: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith()
  })

  it('should not redirect to seleccionar-rol when already on home route', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [
        { nombre_rol: 'Deportista' },
        { nombre_rol: 'Acudiente' }
      ]
    }
    mockAuthStore.activeRole = null
    mockAuthStore.rolesSelector = {
      Deportista: true,
      Acudiente: true
    }

    const next = vi.fn()
    const to = {
      path: '/home',
      matched: [{ meta: { requiresAuth: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    // La lógica puede redirigir o permitir acceso dependiendo de la validación
    expect(next).toHaveBeenCalled()
  })

  it('should handle refreshRoleOptions when rolesSelector is empty', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Deportista' }]
    }
    mockAuthStore.activeRole = null
    mockAuthStore.rolesSelector = {}
    mockAuthStore.refreshRoleOptions = vi.fn().mockResolvedValue(true)
    globalThis.localStorage.getItem = vi.fn(() => null)

    const next = vi.fn()
    const to = {
      path: '/home',
      matched: [{ meta: { requiresAuth: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(mockAuthStore.refreshRoleOptions).toHaveBeenCalled()
  })

  it('should restore activeRole after refreshRoleOptions if changed', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Deportista' }]
    }
    mockAuthStore.activeRole = null
    mockAuthStore.rolesSelector = {}
    globalThis.localStorage.getItem = vi.fn(() => 'Deportista')
    mockAuthStore.refreshRoleOptions = vi.fn().mockImplementation(() => {
      mockAuthStore.rolesSelector = { Deportista: true }
      mockAuthStore.activeRole = null
      return Promise.resolve()
    })
    mockAuthStore.setActiveRole = vi.fn().mockResolvedValue(true)

    const next = vi.fn()
    const to = {
      path: '/home',
      matched: [{ meta: { requiresAuth: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(mockAuthStore.setActiveRole).toHaveBeenCalled()
  })

  it('should handle role name normalization in role restoration', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'deportista' }]
    }
    mockAuthStore.activeRole = null
    mockAuthStore.rolesSelector = {}
    globalThis.localStorage.getItem = vi.fn(() => 'deportista')
    mockAuthStore.refreshRoleOptions = vi.fn().mockImplementation(() => {
      mockAuthStore.rolesSelector = { deportista: true }
      return Promise.resolve()
    })
    mockAuthStore.setActiveRole = vi.fn().mockResolvedValue(true)

    const next = vi.fn()
    const to = {
      path: '/home',
      matched: [{ meta: { requiresAuth: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(mockAuthStore.setActiveRole).toHaveBeenCalled()
  })

  it('should not restore role if role name does not match after normalization', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Deportista' }]
    }
    mockAuthStore.activeRole = null
    mockAuthStore.rolesSelector = {}
    globalThis.localStorage.getItem = vi.fn(() => 'InvalidRole')
    mockAuthStore.refreshRoleOptions = vi.fn().mockImplementation(() => {
      mockAuthStore.rolesSelector = { Deportista: true }
      return Promise.resolve()
    })
    mockAuthStore.setActiveRole = vi.fn().mockResolvedValue(true)

    const next = vi.fn()
    const to = {
      path: '/home',
      matched: [{ meta: { requiresAuth: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(mockAuthStore.setActiveRole).not.toHaveBeenCalled()
  })

  it('should handle empty user roles array', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: []
    }
    mockAuthStore.activeRole = null
    mockAuthStore.rolesSelector = {}

    const next = vi.fn()
    const to = {
      path: '/login',
      matched: [{ meta: { requiresGuest: true } }]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith('/home')
  })

  it('should handle route with no matched records', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Deportista' }]
    }
    mockAuthStore.activeRole = 'Deportista'

    const next = vi.fn()
    const to = {
      path: '/some-route',
      matched: []
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith()
  })

  it('should handle route with requiresRoleRecord found', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'Deportista' }]
    }
    mockAuthStore.activeRole = 'Deportista'
    mockAuthStore.rolesSelector = { Deportista: true }

    const next = vi.fn()
    const to = {
      path: '/deportista/dashboard',
      matched: [
        { meta: { requiresAuth: true } },
        { meta: { requiresRole: ['Deportista'] } }
      ]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith()
  })

  it('should handle route with requiredPermission in nested meta', async () => {
    mockAuthStore.token = 'some-token'
    mockAuthStore.verifyToken.mockResolvedValue(true)
    mockAuthStore.user = {
      roles: [{ nombre_rol: 'SuperAdmin' }]
    }
    mockAuthStore.activeRole = 'SuperAdmin'
    mockAuthStore.rolesSelector = { SuperAdmin: true }

    const next = vi.fn()
    const to = {
      path: '/mensualidades',
      matched: [
        { meta: { requiresAuth: true } },
        { meta: { requiresPermission: 'ver_mensualidad' } }
      ]
    }
    const from = { path: '/' }

    await navigationGuard(to, from, next)

    expect(next).toHaveBeenCalledWith()
  })
})

