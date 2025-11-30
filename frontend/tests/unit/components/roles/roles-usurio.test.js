import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import RolesUsurio from '@/components/roles/roles-usurio.vue'

const mockRouter = {
  push: vi.fn(),
  replace: vi.fn()
}

const mockUseAuthStore = vi.fn()
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockUseAuthStore()
}))

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter
  }
})

describe('RolesUsurio', () => {
  let wrapper
  let router
  let mockAuthStore

  beforeEach(() => {
    vi.clearAllMocks()
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } }
      ]
    })

    mockAuthStore = {
      user: {
        roles: []
      },
      rolesSelector: {},
      activeRole: null,
      setActiveRole: vi.fn().mockResolvedValue({ success: true })
    }

    mockUseAuthStore.mockReturnValue(mockAuthStore)
  })

  const createWrapper = (props = {}) => {
    return mount(RolesUsurio, {
      props: {
        usuarioRoles: props.usuarioRoles
      },
      global: {
        plugins: [router],
        stubs: {
          'i': true
        }
      }
    })
  }

  describe('Renderizado básico', () => {
    it('should render component', () => {
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.contenedor-roles').exists()).toBe(true)
    })

    it('should display title', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('GESTIÓN DE ROLES')
    })

    it('should render all role cards', () => {
      wrapper = createWrapper()
      const tarjetas = wrapper.findAll('.sub-contenedor')
      expect(tarjetas.length).toBe(5) // Aspirante, Deportista, Acudiente, Entrenador, Administrador
    })

    it('should render Volver button', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.boton').exists()).toBe(true)
      expect(wrapper.text()).toContain('Volver')
    })
  })

  describe('Usuario roles computed', () => {
    it('should use props usuarioRoles when provided', () => {
      wrapper = createWrapper({ usuarioRoles: ['Deportista', 'Acudiente'] })
      expect(wrapper.vm.usuarioRoles).toEqual(['Deportista', 'Acudiente'])
    })

    it('should use store roles when props not provided', () => {
      mockAuthStore.user = {
        roles: [{ nombre_rol: 'Deportista' }, { nombre_rol: 'Acudiente' }]
      }
      wrapper = createWrapper()
      expect(wrapper.vm.usuarioRoles).toContain('Deportista')
      expect(wrapper.vm.usuarioRoles).toContain('Acudiente')
    })

    it('should handle string roles from store', () => {
      mockAuthStore.user = {
        roles: ['Deportista', 'Acudiente']
      }
      wrapper = createWrapper()
      expect(wrapper.vm.usuarioRoles).toContain('Deportista')
      expect(wrapper.vm.usuarioRoles).toContain('Acudiente')
    })

    it('should handle empty roles', () => {
      mockAuthStore.user = { roles: [] }
      wrapper = createWrapper()
      expect(wrapper.vm.usuarioRoles).toEqual([])
    })
  })

  describe('Roles disponibles computed', () => {
    it('should use rolesSelector when available', () => {
      mockAuthStore.rolesSelector = {
        'Deportista': true,
        'Acudiente': true,
        'Administrador': false
      }
      wrapper = createWrapper()
      expect(wrapper.vm.rolesDisponibles).toContain('Deportista')
      expect(wrapper.vm.rolesDisponibles).toContain('Acudiente')
      expect(wrapper.vm.rolesDisponibles).not.toContain('Administrador')
    })

    it('should fallback to usuarioRoles when rolesSelector is empty', () => {
      mockAuthStore.rolesSelector = {}
      mockAuthStore.user = {
        roles: [{ nombre_rol: 'Deportista' }]
      }
      wrapper = createWrapper()
      expect(wrapper.vm.rolesDisponibles).toContain('Deportista')
    })
  })

  describe('Rol actual', () => {
    it('should initialize with activeRole from store', () => {
      mockAuthStore.activeRole = 'Deportista'
      mockAuthStore.user = {
        roles: [{ nombre_rol: 'Deportista' }]
      }
      wrapper = createWrapper()
      expect(wrapper.vm.rolActual).toBe('Deportista')
    })

    it('should fallback to first available role', () => {
      mockAuthStore.activeRole = null
      mockAuthStore.user = {
        roles: [{ nombre_rol: 'Deportista' }]
      }
      wrapper = createWrapper()
      expect(wrapper.vm.rolActual).toBe('Deportista')
    })

    it('should fallback to Usuario when no roles', () => {
      mockAuthStore.activeRole = null
      mockAuthStore.user = { roles: [] }
      wrapper = createWrapper()
      expect(wrapper.vm.rolActual).toBe('Usuario')
    })
  })

  describe('Cambiar rol', () => {
    it('should change role successfully for SuperAdmin', async () => {
      wrapper = createWrapper()
      wrapper.vm.rolActual = 'SuperAdmin'
      mockAuthStore.setActiveRole.mockResolvedValue({ success: true })

      await wrapper.vm.cambiarRol()
      await wrapper.vm.$nextTick()

      expect(mockAuthStore.setActiveRole).toHaveBeenCalledWith('SuperAdmin')
      expect(mockRouter.replace).toHaveBeenCalledWith('/admin-manager')
    })

    it('should change role successfully for Administrador', async () => {
      wrapper = createWrapper()
      wrapper.vm.rolActual = 'Administrador'
      mockAuthStore.setActiveRole.mockResolvedValue({ success: true })

      await wrapper.vm.cambiarRol()
      await wrapper.vm.$nextTick()

      expect(mockAuthStore.setActiveRole).toHaveBeenCalledWith('Administrador')
      expect(mockRouter.replace).toHaveBeenCalledWith('/admin-manager')
    })

    it('should change role successfully for Entrenador', async () => {
      wrapper = createWrapper()
      wrapper.vm.rolActual = 'Entrenador'
      mockAuthStore.setActiveRole.mockResolvedValue({ success: true })

      await wrapper.vm.cambiarRol()
      await wrapper.vm.$nextTick()

      expect(mockAuthStore.setActiveRole).toHaveBeenCalledWith('Entrenador')
      expect(mockRouter.replace).toHaveBeenCalledWith('/home')
    })

    it('should change role successfully for Deportista', async () => {
      wrapper = createWrapper()
      wrapper.vm.rolActual = 'Deportista'
      mockAuthStore.setActiveRole.mockResolvedValue({ success: true })

      await wrapper.vm.cambiarRol()
      await wrapper.vm.$nextTick()

      expect(mockAuthStore.setActiveRole).toHaveBeenCalledWith('Deportista')
      expect(mockRouter.replace).toHaveBeenCalledWith('/deportista/dashboard')
    })

    it('should change role successfully for Acudiente', async () => {
      wrapper = createWrapper()
      wrapper.vm.rolActual = 'Acudiente'
      mockAuthStore.setActiveRole.mockResolvedValue({ success: true })

      await wrapper.vm.cambiarRol()
      await wrapper.vm.$nextTick()

      expect(mockAuthStore.setActiveRole).toHaveBeenCalledWith('Acudiente')
      expect(mockRouter.replace).toHaveBeenCalledWith('/acudiente/dashboard')
    })

    it('should redirect to home for unknown role', async () => {
      wrapper = createWrapper()
      wrapper.vm.rolActual = 'UnknownRole'
      mockAuthStore.setActiveRole.mockResolvedValue({ success: true })

      await wrapper.vm.cambiarRol()
      await wrapper.vm.$nextTick()

      expect(mockRouter.replace).toHaveBeenCalledWith('/home')
    })

    it('should revert rolActual when setActiveRole fails', async () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      wrapper = createWrapper()
      const previo = 'Deportista'
      mockAuthStore.activeRole = previo
      wrapper.vm.rolActual = 'Acudiente'
      mockAuthStore.setActiveRole.mockResolvedValue({ success: false, error: 'Error' })

      await wrapper.vm.cambiarRol()
      await wrapper.vm.$nextTick()

      expect(consoleSpy).toHaveBeenCalled()
      expect(wrapper.vm.rolActual).toBe(previo)
      consoleSpy.mockRestore()
    })
  })

  describe('Accion boton', () => {
    it('should navigate to ver-general when Volver is clicked', () => {
      wrapper = createWrapper()
      wrapper.vm.accionBoton()

      expect(mockRouter.push).toHaveBeenCalledWith('/ver-general')
    })
  })

  describe('Role cards inactive state', () => {
    it('should mark role as inactive when not in usuarioRoles', () => {
      wrapper = createWrapper({ usuarioRoles: ['Deportista'] })
      const tarjetas = wrapper.findAll('.sub-contenedor')
      
      // Deportista should be active
      const deportistaCard = tarjetas.find(card => card.text().includes('Deportista'))
      expect(deportistaCard?.classes()).not.toContain('inactivo')
      
      // Acudiente should be inactive
      const acudienteCard = tarjetas.find(card => card.text().includes('Acudiente'))
      expect(acudienteCard?.classes()).toContain('inactivo')
    })
  })

  describe('On mounted', () => {
    it('should sync rolActual with store activeRole', () => {
      mockAuthStore.activeRole = 'Acudiente'
      mockAuthStore.user = {
        roles: [{ nombre_rol: 'Deportista' }, { nombre_rol: 'Acudiente' }]
      }
      wrapper = createWrapper()
      
      expect(wrapper.vm.rolActual).toBe('Acudiente')
    })

    it('should not sync if activeRole not in rolesDisponibles', () => {
      mockAuthStore.activeRole = 'InvalidRole'
      mockAuthStore.user = {
        roles: [{ nombre_rol: 'Deportista' }]
      }
      wrapper = createWrapper()
      
      expect(wrapper.vm.rolActual).not.toBe('InvalidRole')
    })
  })
})

