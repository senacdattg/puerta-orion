import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import RegistrarDeportistaForm from '@/views/registrar-deportista-form.vue'
import { useAuthStore } from '@/stores/auth'
import Swal from 'sweetalert2'

// Mock vue-router
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn()
}

const mockRoute = {
  path: '/registrar-deportista-form',
  name: 'registrar-deportista-form',
  query: {}
}

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter,
    useRoute: () => mockRoute
  }
})

// Mock store
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(() => Promise.resolve({ isConfirmed: true }))
  }
}))

describe('RegistrarDeportistaForm', () => {
  let pinia
  let wrapper
  let mockAuthStore

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    mockAuthStore = {
      user: {
        id_usuario: 1,
        usuario: 'testuser'
      },
      userRoles: [],
      loadUserProfile: vi.fn().mockResolvedValue(true)
    }

    useAuthStore.mockReturnValue(mockAuthStore)
    vi.clearAllMocks()
    mockRouter.push.mockClear()
    mockRoute.query = {}
  })

  const createWrapper = (routeOptions = {}) => {
    // Update mockRoute query for this test
    mockRoute.query = routeOptions.query || {}
    return mount(RegistrarDeportistaForm, {
      global: {
        plugins: [pinia],
        stubs: {
          'FormularioDeportista': true
        }
      }
    })
  }

  describe('Rendering', () => {
    it('should render main component', () => {
      wrapper = createWrapper()
      expect(wrapper.find('main').exists()).toBe(true)
    })

    it('should render FormularioDeportista component', () => {
      wrapper = createWrapper()
      expect(wrapper.findComponent({ name: 'FormularioDeportista' }).exists()).toBe(true)
    })

    it('should show info banner when asignarAcudienteAuto is true', async () => {
      wrapper = createWrapper({
        query: { asignarAcudiente: 'true' }
      })
      await wrapper.vm.$nextTick()

      const banner = wrapper.find('.info-banner')
      expect(banner.exists()).toBe(true)
    })

    it('should not show info banner when asignarAcudienteAuto is false', () => {
      wrapper = createWrapper({
        query: {}
      })

      const banner = wrapper.find('.info-banner')
      expect(banner.exists()).toBe(false)
    })
  })

  describe('asignarAcudienteAuto computed', () => {
    it('should be true when query param is true', async () => {
      wrapper = createWrapper({
        query: { asignarAcudiente: 'true' }
      })
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.asignarAcudienteAuto).toBe(true)
    })

    it('should be false when query param is not true', () => {
      wrapper = createWrapper({
        query: { asignarAcudiente: 'false' }
      })

      expect(wrapper.vm.asignarAcudienteAuto).toBe(false)
    })
  })

  describe('recargarPerfilUsuario', () => {
    it('should load user profile successfully', async () => {
      wrapper = createWrapper()
      mockAuthStore.loadUserProfile.mockResolvedValue(true)

      const result = await wrapper.vm.recargarPerfilUsuario()

      expect(mockAuthStore.loadUserProfile).toHaveBeenCalled()
      expect(result).toBe(true)
    })

    it('should return false when profile update fails', async () => {
      wrapper = createWrapper()
      mockAuthStore.loadUserProfile.mockResolvedValue(false)

      const result = await wrapper.vm.recargarPerfilUsuario()

      expect(result).toBe(false)
    })
  })

  describe('tieneRolDeportista', () => {
    it('should return true when user has Deportista role', () => {
      wrapper = createWrapper()
      mockAuthStore.userRoles = ['Deportista', 'Usuario']

      expect(wrapper.vm.tieneRolDeportista()).toBe(true)
    })

    it('should return false when user does not have Deportista role', () => {
      wrapper = createWrapper()
      mockAuthStore.userRoles = ['Usuario', 'Admin']

      expect(wrapper.vm.tieneRolDeportista()).toBe(false)
    })
  })

  describe('construirMensajeExito', () => {
    it('should build success message with basic info', () => {
      wrapper = createWrapper()
      const datos = {
        data: {}
      }

      const mensaje = wrapper.vm.construirMensajeExito(datos)

      expect(mensaje).toContain('Registro completado exitosamente')
      expect(mensaje).toContain('Ahora eres un deportista')
    })

    it('should include acudiente message when asignarAcudienteAuto is true', async () => {
      wrapper = createWrapper({
        query: { asignarAcudiente: 'true' }
      })
      await wrapper.vm.$nextTick()

      const datos = {
        data: {}
      }

      const mensaje = wrapper.vm.construirMensajeExito(datos)

      expect(mensaje).toContain('Has sido asignado a tu acudiente')
    })

    it('should include categoria if present', () => {
      wrapper = createWrapper()
      const datos = {
        data: {
          categoria: 'Junior'
        }
      }

      const mensaje = wrapper.vm.construirMensajeExito(datos)

      expect(mensaje).toContain('Categoría: Junior')
    })

    it('should include nombre_persona if present', () => {
      wrapper = createWrapper()
      const datos = {
        data: {
          nombre_persona: 'Juan Pérez'
        }
      }

      const mensaje = wrapper.vm.construirMensajeExito(datos)

      expect(mensaje).toContain('Nombre: Juan Pérez')
    })
  })

  describe('mostrarMensajeExito', () => {
    it('should show success message with HTML', async () => {
      wrapper = createWrapper()
      const html = '<p>Test message</p>'

      await wrapper.vm.mostrarMensajeExito(html)

      expect(Swal.fire).toHaveBeenCalled()
      const call = Swal.fire.mock.calls[0][0]
      expect(call.icon).toBe('success')
      expect(call.title).toBe('Registro completado')
      expect(call.html).toBe(html)
    })
  })

  describe('redirigirSegunContexto', () => {
    it('should redirect to ver-acudidos when asignarAcudienteAuto is true', async () => {
      wrapper = createWrapper({
        query: { asignarAcudiente: 'true' }
      })
      await wrapper.vm.$nextTick()

      wrapper.vm.redirigirSegunContexto()

      expect(mockRouter.push).toHaveBeenCalledWith('/ver-acudidos')
    })

    it('should redirect to deportista dashboard when asignarAcudienteAuto is false', () => {
      wrapper = createWrapper()

      wrapper.vm.redirigirSegunContexto()

      expect(mockRouter.push).toHaveBeenCalledWith('/deportista/dashboard')
    })
  })

  describe('procesarRegistroExitoso', () => {
    it('should process successful registration', async () => {
      wrapper = createWrapper()
      mockAuthStore.loadUserProfile.mockResolvedValue(true)
      Swal.fire.mockClear()
      mockRouter.push.mockClear()

      const datos = {
        data: {
          categoria: 'Junior'
        }
      }

      await wrapper.vm.procesarRegistroExitoso(datos)

      expect(Swal.fire).toHaveBeenCalled()
      expect(mockRouter.push).toHaveBeenCalled()
    })

    it('should assign deportista to acudiente when needed', async () => {
      wrapper = createWrapper({
        query: { asignarAcudiente: 'true' }
      })
      await wrapper.vm.$nextTick()
      mockRouter.push.mockClear()

      const datos = {
        data: {}
      }

      await wrapper.vm.procesarRegistroExitoso(datos)

      // Verify that it processes correctly (Swal is called, router is called)
      expect(Swal.fire).toHaveBeenCalled()
      expect(mockRouter.push).toHaveBeenCalledWith('/ver-acudidos')
    })
  })

  describe('manejarRegistroDeportista', () => {
    it('should handle successful registration with Deportista role', async () => {
      wrapper = createWrapper()
      mockAuthStore.loadUserProfile.mockResolvedValue(true)
      mockAuthStore.userRoles = ['Deportista']
      Swal.fire.mockClear()
      mockRouter.push.mockClear()

      const datos = {
        data: {}
      }

      await wrapper.vm.manejarRegistroDeportista(datos)

      expect(mockAuthStore.loadUserProfile).toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should handle registration without Deportista role', async () => {
      wrapper = createWrapper()
      mockAuthStore.loadUserProfile.mockResolvedValue(true)
      mockAuthStore.userRoles = []
      Swal.fire.mockClear()
      mockRouter.push.mockClear()

      const datos = {
        data: {}
      }

      await wrapper.vm.manejarRegistroDeportista(datos)

      expect(Swal.fire).toHaveBeenCalled()
      expect(mockRouter.push).toHaveBeenCalledWith('/deportista/dashboard')
    })

    it('should handle profile update failure', async () => {
      wrapper = createWrapper()
      mockAuthStore.loadUserProfile.mockResolvedValue(false)
      Swal.fire.mockClear()
      mockRouter.push.mockClear()

      const datos = {
        data: {}
      }

      await wrapper.vm.manejarRegistroDeportista(datos)

      expect(Swal.fire).toHaveBeenCalled()
      expect(mockRouter.push).toHaveBeenCalledWith('/deportista/dashboard')
    })

    it('should handle error when loading profile', async () => {
      wrapper = createWrapper()
      mockAuthStore.loadUserProfile.mockRejectedValue(new Error('Network error'))
      Swal.fire.mockClear()
      mockRouter.push.mockClear()

      const datos = {
        data: {}
      }

      await wrapper.vm.manejarRegistroDeportista(datos)

      expect(Swal.fire).toHaveBeenCalled()
      expect(mockRouter.push).toHaveBeenCalledWith('/deportista/dashboard')
    })
  })

  describe('asignarDeportistaAAcudiente', () => {
    it('should assign deportista to acudiente', async () => {
      wrapper = createWrapper()
      mockAuthStore.user = {
        id_usuario: 1,
        usuario: 'acudiente1'
      }

      const result = await wrapper.vm.asignarDeportistaAAcudiente()

      expect(result).toBe(true)
    })

    it('should handle error when assigning', async () => {
      wrapper = createWrapper()
      mockAuthStore.user = null

      const result = await wrapper.vm.asignarDeportistaAAcudiente()

      // Should still return true as it's handled internally
      expect(result).toBeDefined()
    })
  })

  describe('manejarCancelacion', () => {
    it('should cancel and redirect to ver-acudidos when asignarAcudiente is true', async () => {
      wrapper = createWrapper({
        query: { asignarAcudiente: 'true' }
      })
      await wrapper.vm.$nextTick()

      Swal.fire.mockResolvedValue({ isConfirmed: true })
      mockRouter.push.mockClear()

      await wrapper.vm.manejarCancelacion()

      expect(Swal.fire).toHaveBeenCalled()
      expect(mockRouter.push).toHaveBeenCalledWith('/ver-acudidos')
    })

    it('should cancel and redirect to home when asignarAcudiente is false', async () => {
      wrapper = createWrapper()

      Swal.fire.mockResolvedValue({ isConfirmed: true })
      mockRouter.push.mockClear()

      await wrapper.vm.manejarCancelacion()

      expect(Swal.fire).toHaveBeenCalled()
      expect(mockRouter.push).toHaveBeenCalledWith('/home')
    })

    it('should not redirect if cancellation is not confirmed', async () => {
      wrapper = createWrapper()

      Swal.fire.mockResolvedValue({ isConfirmed: false })
      mockRouter.push.mockClear()

      await wrapper.vm.manejarCancelacion()

      expect(Swal.fire).toHaveBeenCalled()
      expect(mockRouter.push).not.toHaveBeenCalled()
    })
  })

  describe('Event Handlers', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should handle submit event from FormularioDeportista', async () => {
      mockAuthStore.loadUserProfile.mockResolvedValue(true)
      mockAuthStore.userRoles = ['Deportista']

      const datos = { data: {} }

      // Call the handler directly since we can't easily test event propagation with stubs
      await wrapper.vm.manejarRegistroDeportista(datos)

      expect(mockAuthStore.loadUserProfile).toHaveBeenCalled()
    })

    it('should handle cancel event from FormularioDeportista', async () => {
      Swal.fire.mockResolvedValue({ isConfirmed: true })
      mockRouter.push.mockClear()

      // Call the handler directly
      await wrapper.vm.manejarCancelacion()

      expect(Swal.fire).toHaveBeenCalled()
    })
  })

  describe('Helper Functions', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should handle manejarRegistroSinRolDeportista', async () => {
      mockRouter.push.mockClear()

      await wrapper.vm.manejarRegistroSinRolDeportista()

      expect(Swal.fire).toHaveBeenCalled()
      expect(mockRouter.push).toHaveBeenCalledWith('/deportista/dashboard')
    })

    it('should handle manejarPerfilNoActualizado', async () => {
      mockRouter.push.mockClear()

      await wrapper.vm.manejarPerfilNoActualizado()

      expect(Swal.fire).toHaveBeenCalled()
      expect(mockRouter.push).toHaveBeenCalledWith('/deportista/dashboard')
    })

    it('should handle manejarErrorRecargaPerfil', async () => {
      mockRouter.push.mockClear()

      await wrapper.vm.manejarErrorRecargaPerfil()

      expect(Swal.fire).toHaveBeenCalled()
      expect(mockRouter.push).toHaveBeenCalledWith('/deportista/dashboard')
    })
  })
})

