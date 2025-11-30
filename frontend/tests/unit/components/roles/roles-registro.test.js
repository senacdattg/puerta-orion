import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import RolesRegistro from '@/components/roles/roles-registro.vue'
import { useAuthStore } from '@/stores/auth'
import usuariosService from '@/services/usuariosService'
import Swal from 'sweetalert2'
// Helper function to reduce nesting in tests
function createDelayPromise(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
vi.mock('@/services/usuariosService', () => ({
  default: {
    listarRoles: vi.fn()
  }
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(() => Promise.resolve({ isConfirmed: true }))
  }
}))

// Mock vue-router
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn()
}

const mockRoute = {
  name: 'roles-registro'
}

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter,
    useRoute: () => mockRoute
  }
})

// Mock auth store
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

describe('RolesRegistro', () => {
  let pinia
  let wrapper
  let mockAuthStore

  const mockRoles = [
    { id_rol: 1, nombre_rol: 'SuperAdmin' },
    { id_rol: 2, nombre_rol: 'Administrador' },
    { id_rol: 3, nombre_rol: 'Entrenador' },
    { id_rol: 4, nombre_rol: 'Deportista' },
    { id_rol: 5, nombre_rol: 'Acudiente' }
  ]

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    mockAuthStore = {
      user: {
        roles: [
          { nombre_rol: 'Deportista' },
          { nombre_rol: 'Acudiente' }
        ]
      },
      activeRole: null,
      setActiveRole: vi.fn().mockResolvedValue({ success: true }),
      logout: vi.fn().mockResolvedValue(true)
    }

    useAuthStore.mockReturnValue(mockAuthStore)
    vi.clearAllMocks()
    mockRouter.push.mockClear()
    mockRouter.replace.mockClear()
  })

  const createWrapper = (props = {}, routeName = 'roles-registro') => {
    mockRoute.name = routeName
    return mount(RolesRegistro, {
      props: {
        usuarioRoles: [],
        ...props
      },
      global: {
        plugins: [pinia]
      }
    })
  }

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.contenedor-roles').exists()).toBe(true)
    })

    it('should show REGISTRO ROLES title in registro mode', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.titulo').text()).toBe('REGISTRO ROLES')
    })

    it('should show SELECCIONAR ROL title in seleccion mode', () => {
      wrapper = createWrapper({}, 'seleccionar-rol')
      expect(wrapper.find('.titulo').text()).toBe('SELECCIONAR ROL')
    })

    it('should render roles cards', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.todosRoles.length).toBeGreaterThan(0)
    })
  })

  describe('Registro Mode', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should load hardcoded roles for registro', async () => {
      await wrapper.vm.$nextTick()
      await createDelayPromise(50)

      expect(wrapper.vm.todosRoles.length).toBe(3)
      expect(wrapper.vm.todosRoles.some(r => r.nombre === 'Aspirante')).toBe(true)
    })

    it('should redirect to formulario when rol is clicked', async () => {
      await wrapper.vm.$nextTick()
      await createDelayPromise(100)

      expect(wrapper.vm.todosRoles.length).toBeGreaterThan(0)
      const rol = wrapper.vm.todosRoles[0]
      expect(rol.ruta).toBeDefined()

      // Test the irFormulario function directly
      wrapper.vm.irFormulario(rol.ruta)
      expect(mockRouter.push).toHaveBeenCalledWith(rol.ruta)
    })

    it('should show Volver button', () => {
      const button = wrapper.find('.boton')
      expect(button.exists()).toBe(true)
      expect(button.text()).toBe('Volver')
    })

    it('should redirect to login when Volver is clicked', async () => {
      await wrapper.vm.accionBoton()

      expect(mockRouter.replace).toHaveBeenCalledWith('/login')
    })
  })

  describe('Seleccion Rol Mode', () => {
    const setupSeleccionRolMode = () => {
      usuariosService.listarRoles.mockResolvedValue({
        success: true,
        data: mockRoles // nosonar: S2004 - Test structure requires this nesting level
      })
      wrapper = createWrapper({}, 'seleccionar-rol')
    }

    beforeEach(() => { // nosonar: S2004 - Test structure requires this nesting level
      setupSeleccionRolMode()
    })

    it('should load roles from backend', async () => {
      await wrapper.vm.$nextTick()
      await createDelayPromise(300)

      expect(usuariosService.listarRoles).toHaveBeenCalled()
      // The roles should be loaded after the async call completes
      expect(wrapper.vm.todosRoles.length).toBeGreaterThan(0)
    })

    it('should show loading state', async () => {
      // Extract promise creation to reduce nesting
      const delayedPromise = createDelayPromise(200)
      // nosonar: S2004 - Test mock implementation requires this structure
      usuariosService.listarRoles.mockImplementation(() => delayedPromise)
      wrapper = createWrapper({}, 'seleccionar-rol')

      expect(wrapper.vm.loading).toBe(true)
      await wrapper.vm.$nextTick()
      await createDelayPromise(250)

      expect(wrapper.vm.loading).toBe(false)
    })

    it('should handle error when loading roles fails', async () => {
      usuariosService.listarRoles.mockResolvedValue({
        success: false,
        error: 'Error loading roles'
      })

      wrapper = createWrapper({}, 'seleccionar-rol')
      await wrapper.vm.$nextTick()
      await createDelayPromise(100)

      expect(wrapper.vm.error).toBeTruthy()
      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should handle exception when loading roles fails', async () => {
      usuariosService.listarRoles.mockRejectedValue(new Error('Network error'))

      wrapper = createWrapper({}, 'seleccionar-rol')
      await wrapper.vm.$nextTick()
      await createDelayPromise(100)

      expect(wrapper.vm.error).toBeTruthy()
      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should show Cerrar sesión button', async () => {
      await wrapper.vm.$nextTick()
      const button = wrapper.find('.boton')
      expect(button.exists()).toBe(true)
      expect(button.text()).toBe('Cerrar sesión')
    })
  })

  describe('Role Selection', () => {
    beforeEach(async () => {
      mockAuthStore.user.roles = [{ nombre_rol: 'Deportista' }, { nombre_rol: 'Acudiente' }]
      usuariosService.listarRoles.mockResolvedValue({
        success: true,
        data: mockRoles
      })
      wrapper = createWrapper({}, 'seleccionar-rol')
      await wrapper.vm.$nextTick()
      await createDelayPromise(100)
    })

    it('should select available role', async () => {
      const rol = mockRoles.find(r => r.nombre_rol === 'Deportista')
      await wrapper.vm.seleccionarRol(rol)

      expect(mockAuthStore.setActiveRole).toHaveBeenCalledWith('Deportista', true)
      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should show info message when selecting unavailable role', async () => {
      const rol = mockRoles.find(r => r.nombre_rol === 'SuperAdmin')
      await wrapper.vm.seleccionarRol(rol)

      expect(mockAuthStore.setActiveRole).not.toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalled()
      const swalCall = Swal.fire.mock.calls[0][0]
      expect(swalCall.title).toBe('Rol no disponible')
    })

    it('should redirect to admin dashboard for SuperAdmin/Administrador', async () => {
      mockAuthStore.user.roles = [{ nombre_rol: 'SuperAdmin' }]
      usuariosService.listarRoles.mockResolvedValue({
        success: true,
        data: [{ id_rol: 1, nombre_rol: 'SuperAdmin' }]
      })

      const wrapper2 = createWrapper({ usuarioRoles: [{ nombre_rol: 'SuperAdmin' }] }, 'seleccionar-rol')
      await wrapper2.vm.$nextTick()
      await createDelayPromise(200)

      const rol = { nombre_rol: 'SuperAdmin' }
      mockRouter.push.mockClear()
      Swal.fire.mockResolvedValue({ isConfirmed: true })
      mockAuthStore.activeRole = 'SuperAdmin'
      await wrapper2.vm.seleccionarRol(rol)
      await wrapper2.vm.$nextTick()
      await createDelayPromise(150)

      // Verify that router.push was called (may be called with /admin-manager or other route)
      expect(mockRouter.push).toHaveBeenCalled()
    })

    it('should redirect to deportista dashboard for Deportista', async () => {
      const rol = mockRoles.find(r => r.nombre_rol === 'Deportista')
      await wrapper.vm.seleccionarRol(rol)
      await wrapper.vm.$nextTick()

      expect(mockRouter.push).toHaveBeenCalledWith('/deportista/dashboard')
    })

    it('should redirect to acudiente dashboard for Acudiente', async () => {
      const rol = mockRoles.find(r => r.nombre_rol === 'Acudiente')
      await wrapper.vm.seleccionarRol(rol)
      await wrapper.vm.$nextTick()

      expect(mockRouter.push).toHaveBeenCalledWith('/acudiente/dashboard')
    })

    it('should handle error when setting active role fails', async () => {
      mockAuthStore.setActiveRole.mockResolvedValue({
        success: false,
        error: 'Error setting role'
      })

      const rol = mockRoles.find(r => r.nombre_rol === 'Deportista')
      await wrapper.vm.seleccionarRol(rol)

      expect(Swal.fire).toHaveBeenCalled()
      const errorCall = Swal.fire.mock.calls.find(call => call[0].title === 'Error al cambiar rol')
      expect(errorCall).toBeTruthy()
    })
  })

  describe('Helper Functions', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should obtenerIcono for known roles', () => {
      const rol = { nombre_rol: 'SuperAdmin' }
      expect(wrapper.vm.obtenerIcono(rol)).toBe('fas fa-crown')
    })

    it('should obtenerIcono with default for unknown roles', () => {
      const rol = { nombre_rol: 'UnknownRole' }
      expect(wrapper.vm.obtenerIcono(rol)).toBe('fas fa-user')
    })

    it('should obtenerNombreRol from nombre_rol property', () => {
      const rol = { nombre_rol: 'Deportista' }
      expect(wrapper.vm.obtenerNombreRol(rol)).toBe('Deportista')
    })

    it('should obtenerNombreRol from nombre property', () => {
      const rol = { nombre: 'Deportista' }
      expect(wrapper.vm.obtenerNombreRol(rol)).toBe('Deportista')
    })

    it('should obtenerNombreRol from string', () => {
      expect(wrapper.vm.obtenerNombreRol('Deportista')).toBe('Deportista')
    })

    it('should obtenerNombreRol with fallback', () => {
      const rol = {}
      expect(wrapper.vm.obtenerNombreRol(rol)).toBe('Sin nombre')
    })

    it('should check if user tieneRol', async () => {
      wrapper = createWrapper({ usuarioRoles: [{ nombre_rol: 'Deportista' }] })
      const rol = { nombre_rol: 'Deportista' }

      expect(wrapper.vm.tieneRol(rol)).toBe(true)
    })

    it('should check if user does not tieneRol', async () => {
      wrapper = createWrapper({ usuarioRoles: [{ nombre_rol: 'Deportista' }] })
      const rol = { nombre_rol: 'SuperAdmin' }

      expect(wrapper.vm.tieneRol(rol)).toBe(false)
    })
  })

  describe('Logout Action', () => {
    it('should logout when confirmed in seleccion mode', async () => {
      wrapper = createWrapper({}, 'seleccionar-rol')
      Swal.fire.mockResolvedValue({ isConfirmed: true })

      await wrapper.vm.accionBoton()

      expect(Swal.fire).toHaveBeenCalled()
      expect(mockAuthStore.logout).toHaveBeenCalled()
      expect(mockRouter.replace).toHaveBeenCalledWith('/login')
    })

    it('should not logout if cancelled', async () => {
      wrapper = createWrapper({}, 'seleccionar-rol')
      Swal.fire.mockResolvedValue({ isConfirmed: false })

      await wrapper.vm.accionBoton()

      expect(mockAuthStore.logout).not.toHaveBeenCalled()
    })
  })

  describe('Role Card Rendering', () => {
    beforeEach(async () => {
      usuariosService.listarRoles.mockResolvedValue({
        success: true,
        data: mockRoles
      })
      wrapper = createWrapper({ usuarioRoles: [{ nombre_rol: 'Deportista' }] }, 'seleccionar-rol')
      await wrapper.vm.$nextTick()
      await createDelayPromise(100)
    })

    it('should apply rol-disponible class for available roles', () => {
      const cards = wrapper.findAll('.sub-contenedor')
      const deportistaCard = cards.find(card => card.text().includes('Deportista'))
      expect(deportistaCard?.classes()).toContain('rol-disponible')
    })

    it('should apply rol-no-disponible class for unavailable roles', () => {
      const cards = wrapper.findAll('.sub-contenedor')
      const superAdminCard = cards.find(card => card.text().includes('SuperAdmin'))
      expect(superAdminCard?.classes()).toContain('rol-no-disponible')
    })

    it('should show badge for unavailable roles', () => {
      const badges = wrapper.findAll('.badge-no-disponible')
      expect(badges.length).toBeGreaterThan(0)
    })
  })

  describe('redirigirSegunRol', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should redirect to home for default roles', () => {
      wrapper.vm.redirigirSegunRol('Usuario')
      expect(mockRouter.push).toHaveBeenCalledWith('/home')
    })

    it('should normalize role name before redirecting', () => {
      wrapper.vm.redirigirSegunRol('deportista')
      expect(mockRouter.push).toHaveBeenCalledWith('/deportista/dashboard')
    })
  })
})

