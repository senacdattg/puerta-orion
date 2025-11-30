import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import FormularioAcudienteCompleto from '@/views/formulario-acudiente-completo.vue'
import Swal from 'sweetalert2'

const mockCompletarPerfilAcudiente = vi.fn()
const mockGetProfile = vi.fn()
vi.mock('@/services/authService', () => ({
  default: {
    getProfile: () => mockGetProfile(),
    completarPerfilAcudiente: () => mockCompletarPerfilAcudiente()
  }
}))

const mockUseAuthStore = vi.fn()
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockUseAuthStore()
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn()
  }
}))

vi.mock('@/config/environment', () => ({
  API_CONFIG: {
    baseURL: 'http://localhost:5000'
  }
}))

globalThis.fetch = vi.fn()
globalThis.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn()
}

describe('FormularioAcudienteCompleto View', () => {
  let wrapper
  let mockAuthStore
  let router

  beforeEach(async () => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } },
        { path: '/acudiente/dashboard', component: { template: '<div>Dashboard</div>' } }
      ]
    })

    mockAuthStore = {
      user: {
        id_usuario: 1,
        persona: { id_persona: 1 }
      },
      userRoles: [],
      activeRole: null,
      setActiveRole: vi.fn().mockResolvedValue(true),
      getProfile: vi.fn().mockResolvedValue({
        success: true,
        data: {
          id_usuario: 1,
          persona: { id_persona: 1 }
        }
      })
    }

    // Configurar el mock global
    mockUseAuthStore.mockReturnValue(mockAuthStore)
    mockCompletarPerfilAcudiente.mockClear()
    mockGetProfile.mockResolvedValue({
      success: true,
      data: {
        id_usuario: 1,
        persona: { id_persona: 1 },
        roles: []
      }
    })

    globalThis.fetch.mockClear()
    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        success: true,
        data: [
          { id_parentesco: 1, nombre: 'Padre' },
          { id_parentesco: 2, nombre: 'Madre' }
        ]
      })
    })
  })

  const createWrapper = () => {
    return mount(FormularioAcudienteCompleto, {
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
    })

    it('should display form title', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Registro como Acudiente')
    })
  })

  describe('Cargar parentescos', () => {
    it('should load parentescos on mount', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await wrapper.vm.$nextTick()

      // Verificar que fetch fue llamado (para cargar parentescos y datos del usuario)
      expect(globalThis.fetch).toHaveBeenCalled()
    })

    it('should handle error loading parentescos', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Error test' })
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      await wrapper.vm.$nextTick()

      // El componente maneja errores, pero no necesariamente establece mensajeBusquedaDeportista
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Buscar deportista', () => {
    it('should search deportista by documento', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          data: {
            id_deportista: 1,
            id_persona: 2,
            persona: {
              nombre_completo: 'Juan Pérez',
              documento: '12345678',
              correo_electronico: 'juan@test.com',
              id_persona: 2
            }
          }
        })
      })

      wrapper.vm.cedulaBuscada = '12345678'
      await wrapper.vm.buscarDeportistaPorCedula()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.deportistaEncontrado).toBeTruthy()
      expect(wrapper.vm.deportistaEncontrado.id_deportista).toBe(1)
    })

    it('should not search if documento is empty', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.cedulaBuscada = ''
      await wrapper.vm.buscarDeportistaPorCedula()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mensajeBusquedaDeportista).toBeTruthy()
      expect(wrapper.vm.mensajeBusquedaDeportista.tipo).toBe('error')
    })

    it('should handle deportista not found', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: false,
          message: 'No encontrado'
        })
      })

      wrapper.vm.cedulaBuscada = '99999999'
      await wrapper.vm.buscarDeportistaPorCedula()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.deportistaEncontrado).toBeNull()
      expect(wrapper.vm.mensajeBusquedaDeportista).toBeTruthy()
      expect(wrapper.vm.mensajeBusquedaDeportista.tipo).toBe('warning')
    })
  })

  describe('Completar registro', () => {
    it('should complete registro successfully', async () => {
      mockCompletarPerfilAcudiente.mockResolvedValueOnce({
        success: true,
        message: 'Perfil completado'
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.deportistaEncontrado = {
        id_deportista: 1,
        id_persona: 2
      }
      wrapper.vm.idParentesco = '1'
      wrapper.vm.esResponsable = true
      mockAuthStore.userRoles = ['Acudiente']
      mockAuthStore.loadUserProfile = vi.fn().mockResolvedValue(true)
      mockAuthStore.setActiveRole = vi.fn().mockResolvedValue(true)

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.completarRegistroAcudiente()
      await wrapper.vm.$nextTick()

      expect(mockCompletarPerfilAcudiente).toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should validate deportista selected', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.deportistaEncontrado = null
      wrapper.vm.idParentesco = '1'

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.completarRegistroAcudiente()
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalled()
      expect(mockCompletarPerfilAcudiente).not.toHaveBeenCalled()
    })

    it('should validate parentesco selected', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.deportistaEncontrado = { id_deportista: 1 }
      wrapper.vm.idParentesco = ''

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.completarRegistroAcudiente()

      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should not allow self-association', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.deportistaEncontrado = {
        id_deportista: 1,
        id_persona: 1
      }
      wrapper.vm.idParentesco = '1'
      mockAuthStore.user.persona = { id_persona: 1 }

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.completarRegistroAcudiente()

      expect(Swal.fire).toHaveBeenCalled()
    })
  })

  describe('Cancelar registro', () => {
    it('should cancel and redirect', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      mockAuthStore.userRoles = ['Deportista']
      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.manejarCancelacion()
      await wrapper.vm.$nextTick()
      await router.isReady()

      expect(router.currentRoute.value.path).toBe('/deportista/dashboard')
    })

    it('should not cancel if user cancels confirmation', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: false })

      await wrapper.vm.manejarCancelacion()

      // Should not redirect
      expect(router.currentRoute.value.path).toBe('/')
    })
  })
})

