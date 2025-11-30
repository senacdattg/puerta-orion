import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import VerAcudidos from '@/views/ver-acudidos.vue'
import Swal from 'sweetalert2'

// Mock components
vi.mock('@/components/layout/encabezado.vue', () => ({
  default: {
    name: 'Encabezado',
    template: '<header>Header</header>'
  }
}))

vi.mock('@/components/layout/pie.vue', () => ({
  default: {
    name: 'Pie',
    template: '<footer>Footer</footer>'
  }
}))

vi.mock('@/components/deportistas/perfil-deportista-vista.vue', () => ({
  default: {
    name: 'PerfilDeportistaVista',
    template: '<div>Perfil</div>',
    props: ['datos', 'modoEdicion'],
    emits: ['cerrar', 'editar', 'cancelar', 'guardar']
  }
}))

vi.mock('@/services/deportistasService', () => ({
  default: {
    obtenerDeportistaPorId: vi.fn(),
    listarDeportistas: vi.fn()
  }
}))

vi.mock('@/services/authService', () => ({
  default: {
    asociarAcudienteDeportista: vi.fn(),
    completarPerfilAcudiente: vi.fn()
  }
}))

vi.mock('@/services/catalogosService', () => ({
  default: {
    getParentescos: vi.fn()
  }
}))

const mockUseAuthStore = vi.fn()
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockUseAuthStore()
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(),
    close: vi.fn()
  }
}))

vi.mock('@/config/environment', () => ({
  getApiBaseUrl: vi.fn(() => 'http://localhost:5000')
}))

// Mock fetch and localStorage
globalThis.fetch = vi.fn()
globalThis.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn()
}

describe('VerAcudidos View', () => {
  let wrapper
  let mockAuthStore
  let router

  beforeEach(async () => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    router = createRouter({
      history: createWebHistory(),
      routes: [{ path: '/', component: { template: '<div>Home</div>' } }]
    })

    mockAuthStore = {
      user: {
        id_usuario: 1,
        acudiente: {
          id_acudiente: 1
        }
      },
      token: 'test-token',
      loadUserProfile: vi.fn().mockResolvedValue(true)
    }

    // Configurar el mock global
    mockUseAuthStore.mockReturnValue(mockAuthStore)

    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        success: true,
        data: []
      }),
      headers: {
        get: vi.fn(() => 'application/json')
      }
    })
  })

  const createWrapper = () => {
    return mount(VerAcudidos, {
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
      expect(wrapper.find('.ver-acudidos-page').exists()).toBe(true)
    })

    it('should display page title', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Gestión de Acudidos')
    })

    it('should display empty state when no acudidos', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.empty-state').exists()).toBe(true)
    })
  })

  describe('Cargar acudidos', () => {
    it('should load acudidos on mount', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          data: [
            {
              id: 1,
              nombre_completo: 'Juan Pérez',
              categoria: 'Juvenil',
              edad: 15,
              correo_electronico: 'juan@test.com',
              telefono: '1234567890'
            }
          ]
        }),
        headers: {
          get: vi.fn(() => 'application/json')
        }
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 600))

      expect(globalThis.fetch).toHaveBeenCalled()
    })

    it('should handle error loading acudidos', async () => {
      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          success: false,
          message: 'Error'
        }),
        headers: {
          get: vi.fn(() => 'application/json')
        }
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 600))

      expect(wrapper.vm.acudidos.length).toBe(0)
    })

    it('should handle missing acudiente id', async () => {
      mockAuthStore.user.acudiente = null

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 600))

      expect(wrapper.vm.acudidos.length).toBe(0)
    })
  })

  describe('Modal de acudir', () => {
    it('should open modal acudir', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const catalogosService = await import('@/services/catalogosService')
      catalogosService.default.getParentescos.mockResolvedValueOnce([
        { id_parentesco: 1, nombre: 'Padre' },
        { id_parentesco: 2, nombre: 'Madre' }
      ])

      await wrapper.vm.abrirModalAcudir()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarModalAcudir).toBe(true)
    })

    it('should close modal acudir', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarModalAcudir = true
      wrapper.vm.cerrarModalAcudir()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarModalAcudir).toBe(false)
      expect(wrapper.vm.busquedaDeportista).toBe('')
    })

    it('should search deportistas', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const deportistasService = await import('@/services/deportistasService')
      deportistasService.default.listarDeportistas.mockResolvedValueOnce({
        success: true,
        data: [
          {
            id_deportista: 1,
            nombre: 'Juan Pérez',
            documento: '12345678',
            categoria: 'Juvenil'
          }
        ]
      })

      wrapper.vm.busquedaDeportista = 'Juan'
      await wrapper.vm.buscarDeportistas()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.deportistasEncontrados.length).toBeGreaterThan(0)
    })

    it('should not search if query too short', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.busquedaDeportista = 'J'
      await wrapper.vm.buscarDeportistas()

      expect(wrapper.vm.deportistasEncontrados.length).toBe(0)
    })

    it('should select deportista', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const deportista = {
        id_deportista: 1,
        nombre: 'Juan Pérez'
      }

      wrapper.vm.seleccionarDeportista(deportista)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.deportistaSeleccionado).toEqual(deportista)
    })

    it('should associate deportista successfully', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const authService = await import('@/services/authService')
      authService.default.asociarAcudienteDeportista.mockResolvedValueOnce({
        success: true
      })

      wrapper.vm.deportistaSeleccionado = {
        id_deportista: 1,
        id_persona: 2
      }
      wrapper.vm.idParentesco = '1'
      wrapper.vm.esResponsable = false
      mockAuthStore.user.persona = { id_persona: 1 }

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.asociarDeportista()
      await wrapper.vm.$nextTick()

      expect(authService.default.asociarAcudienteDeportista).toHaveBeenCalled()
    })

    it('should not allow self-association', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.deportistaSeleccionado = {
        id_deportista: 1,
        id_persona: 1
      }
      wrapper.vm.idParentesco = '1'
      mockAuthStore.user.persona = { id_persona: 1 }

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.asociarDeportista()

      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should validate required fields before associating', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.deportistaSeleccionado = null
      wrapper.vm.idParentesco = ''

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.asociarDeportista()

      expect(Swal.fire).toHaveBeenCalled()
    })
  })

  describe('Modal de perfil', () => {
    it('should open profile modal', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const deportistasService = await import('@/services/deportistasService')
      deportistasService.default.obtenerDeportistaPorId.mockResolvedValueOnce({
        success: true,
        data: {
          id: 1,
          nombre_completo: 'Juan Pérez'
        }
      })

      const acudido = { id: 1 }
      await wrapper.vm.verDetalle(acudido)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarModalPerfil).toBe(true)
    })

    it('should close profile modal', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarModalPerfil = true
      wrapper.vm.cerrarModalPerfil()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarModalPerfil).toBe(false)
    })

    it('should enable edit mode', () => {
      wrapper = createWrapper()

      wrapper.vm.habilitarEdicionPerfil()

      expect(wrapper.vm.modoEdicionPerfil).toBe(true)
    })

    it('should cancel edit mode', () => {
      wrapper = createWrapper()

      wrapper.vm.modoEdicionPerfil = true
      wrapper.vm.cancelarEdicionPerfil()

      expect(wrapper.vm.modoEdicionPerfil).toBe(false)
    })

    it('should handle profile save', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.deportistaSeleccionadoPerfil = { id: 1 }

      const deportistasService = await import('@/services/deportistasService')
      deportistasService.default.obtenerDeportistaPorId.mockResolvedValueOnce({
        success: true,
        data: { id: 1, nombre: 'Updated' }
      })

      await wrapper.vm.manejarGuardadoPerfil()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.modoEdicionPerfil).toBe(false)
    })
  })
})

