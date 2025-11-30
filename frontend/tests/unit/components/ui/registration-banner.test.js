import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import RegistrationBanner from '@/components/ui/registration-banner.vue'

const mockRouter = {
  push: vi.fn()
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

describe('RegistrationBanner', () => {
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
      userRoles: [],
      userDetail: null,
      rolesSelector: {},
      activeRole: null,
      loadUserProfile: vi.fn().mockResolvedValue({}),
      loadUserProfileDetail: vi.fn().mockResolvedValue({})
    }

    mockUseAuthStore.mockReturnValue(mockAuthStore)
  })

  const createWrapper = () => {
    return mount(RegistrationBanner, {
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
      expect(wrapper.find('.registration-banner').exists()).toBe(true)
    })

    it('should display banner title', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('¡Completa tu registro!')
    })

    it('should display banner description', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Para acceder a todas las funcionalidades')
    })
  })

  describe('Ya es deportista computed', () => {
    it('should return true when user has Deportista role', () => {
      mockAuthStore.userRoles = ['Deportista']
      wrapper = createWrapper()
      expect(wrapper.vm.yaEsDeportista).toBe(true)
    })

    it('should return false when user does not have Deportista role', () => {
      mockAuthStore.userRoles = ['Acudiente']
      wrapper = createWrapper()
      expect(wrapper.vm.yaEsDeportista).toBe(false)
    })

    it('should return false when userRoles is empty', () => {
      mockAuthStore.userRoles = []
      wrapper = createWrapper()
      expect(wrapper.vm.yaEsDeportista).toBe(false)
    })
  })

  describe('Ya es acudiente computed', () => {
    it('should return true when user has Acudiente role', () => {
      mockAuthStore.userRoles = ['Acudiente']
      wrapper = createWrapper()
      expect(wrapper.vm.yaEsAcudiente).toBe(true)
    })

    it('should return false when user does not have Acudiente role', () => {
      mockAuthStore.userRoles = ['Deportista']
      wrapper = createWrapper()
      expect(wrapper.vm.yaEsAcudiente).toBe(false)
    })
  })

  describe('Edad deportista computed', () => {
    it('should calculate edad from fecha_nacimiento number', () => {
      const añoActual = new Date().getFullYear()
      const añoNacimiento = añoActual - 20
      mockAuthStore.userDetail = {
        deportista: {
          fecha_nacimiento: añoNacimiento
        }
      }
      wrapper = createWrapper()
      expect(wrapper.vm.edadDeportista).toBe(20)
    })

    it('should calculate edad from fecha_nacimiento string', () => {
      const fechaNacimiento = new Date()
      fechaNacimiento.setFullYear(fechaNacimiento.getFullYear() - 18)
      mockAuthStore.userDetail = {
        deportista: {
          fecha_nacimiento: fechaNacimiento.toISOString()
        }
      }
      wrapper = createWrapper()
      expect(wrapper.vm.edadDeportista).toBe(18)
    })

    it('should return null when no deportista', () => {
      mockAuthStore.userDetail = null
      wrapper = createWrapper()
      expect(wrapper.vm.edadDeportista).toBeNull()
    })

    it('should return null when no fecha_nacimiento', () => {
      mockAuthStore.userDetail = {
        deportista: {}
      }
      wrapper = createWrapper()
      expect(wrapper.vm.edadDeportista).toBeNull()
    })

    it('should handle error gracefully', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      mockAuthStore.userDetail = {
        deportista: {
          fecha_nacimiento: 'invalid-date'
        }
      }
      wrapper = createWrapper()
      // El componente puede devolver NaN o null en caso de error
      const edad = wrapper.vm.edadDeportista
      expect(edad === null || isNaN(edad)).toBe(true)
      consoleSpy.mockRestore()
    })
  })

  describe('Es mayor de edad computed', () => {
    it('should return true when edad >= 18', () => {
      const añoActual = new Date().getFullYear()
      mockAuthStore.userDetail = {
        deportista: {
          fecha_nacimiento: añoActual - 18
        }
      }
      wrapper = createWrapper()
      expect(wrapper.vm.esMayorDeEdad).toBe(true)
    })

    it('should return false when edad < 18', () => {
      const añoActual = new Date().getFullYear()
      mockAuthStore.userDetail = {
        deportista: {
          fecha_nacimiento: añoActual - 17
        }
      }
      wrapper = createWrapper()
      expect(wrapper.vm.esMayorDeEdad).toBe(false)
    })

    it('should return false when edad is null', () => {
      mockAuthStore.userDetail = null
      wrapper = createWrapper()
      expect(wrapper.vm.esMayorDeEdad).toBe(false)
    })
  })

  describe('Mostrar opción acudiente computed', () => {
    it('should return false if already acudiente', () => {
      mockAuthStore.userRoles = ['Acudiente']
      wrapper = createWrapper()
      expect(wrapper.vm.mostrarOpcionAcudiente).toBe(false)
    })

    it('should return true if not acudiente and not deportista', () => {
      mockAuthStore.userRoles = []
      wrapper = createWrapper()
      expect(wrapper.vm.mostrarOpcionAcudiente).toBe(true)
    })

    it('should return true if deportista and mayor de edad', () => {
      const añoActual = new Date().getFullYear()
      mockAuthStore.userRoles = ['Deportista']
      mockAuthStore.userDetail = {
        deportista: {
          fecha_nacimiento: añoActual - 18
        }
      }
      wrapper = createWrapper()
      expect(wrapper.vm.mostrarOpcionAcudiente).toBe(true)
    })

    it('should return false if deportista and menor de edad', () => {
      const añoActual = new Date().getFullYear()
      mockAuthStore.userRoles = ['Deportista']
      mockAuthStore.userDetail = {
        deportista: {
          fecha_nacimiento: añoActual - 17
        }
      }
      wrapper = createWrapper()
      expect(wrapper.vm.mostrarOpcionAcudiente).toBe(false)
    })
  })

  describe('Buttons visibility', () => {
    it('should show Acudiente button when mostrarOpcionAcudiente is true', () => {
      mockAuthStore.userRoles = []
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Registrarse como Acudiente')
    })

    it('should show Deportista button when not yaEsDeportista', () => {
      mockAuthStore.userRoles = []
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Registrarse como Deportista')
    })

    it('should not show Deportista button when yaEsDeportista', () => {
      mockAuthStore.userRoles = ['Deportista']
      wrapper = createWrapper()
      expect(wrapper.text()).not.toContain('Registrarse como Deportista')
    })
  })

  describe('Navegación', () => {
    it('should navigate to formulario-acudiente-completo when acudiente button is clicked', async () => {
      mockAuthStore.userRoles = []
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.navigateToRegister('acudiente')

      expect(mockRouter.push).toHaveBeenCalledWith('/formulario-acudiente-completo')
    })

    it('should navigate to registrar-deportista-form when deportista button is clicked', async () => {
      mockAuthStore.userRoles = []
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.navigateToRegister('deportista')

      expect(mockRouter.push).toHaveBeenCalledWith('/registrar-deportista-form')
    })
  })

  describe('On mounted', () => {
    it('should load user profile if not loaded', async () => {
      mockAuthStore.user = null
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockAuthStore.loadUserProfile).toHaveBeenCalled()
    })

    it('should load user profile detail if not loaded', async () => {
      mockAuthStore.userDetail = null
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockAuthStore.loadUserProfileDetail).toHaveBeenCalled()
    })

    it('should not load profile if already loaded', async () => {
      mockAuthStore.user = { id: 1 }
      mockAuthStore.userDetail = { id: 1 }
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockAuthStore.loadUserProfile).not.toHaveBeenCalled()
      expect(mockAuthStore.loadUserProfileDetail).not.toHaveBeenCalled()
    })
  })
})

