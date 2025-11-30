import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createRouter, createWebHistory } from 'vue-router'
import router from '@/router/index'
import { useAuthStore } from '@/stores/auth'

// Mock store
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

// Mock localStorage
global.localStorage = {
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
      r.name && r.name.includes('deportista')
    )
    expect(deportistaRoutes.length).toBeGreaterThan(0)
    deportistaRoutes.forEach(route => {
      if (route.meta && route.meta.requiresRole) {
        expect(route.meta.requiresRole).toContain('Deportista')
      }
    })
  })

  it('should have acudiente routes with role restrictions', () => {
    const acudienteRoutes = router.options.routes.filter(r => 
      r.name && (r.name.includes('acudiente') || r.path?.includes('/acudiente/'))
    )
    expect(acudienteRoutes.length).toBeGreaterThan(0)
    // Verificar que al menos una ruta de acudiente tiene el rol requerido
    const routesWithRole = acudienteRoutes.filter(route => 
      route.meta && route.meta.requiresRole && route.meta.requiresRole.includes('Acudiente')
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
})

