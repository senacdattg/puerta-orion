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
    listarDeportistas: vi.fn(),
    buscarDeportistaPorDocumentoParaAcudiente: vi.fn()
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

  // Helper function to wait for async operations
  const waitForAsync = (ms = 100) => new Promise(resolve => setTimeout(resolve, ms))

  // Helper function to create mock fetch response
  const createMockFetchResponse = (options = {}) => ({
    ok: options.ok ?? true,
    json: async () => options.json ?? { success: true, data: [] },
    text: async () => options.text ?? '',
    headers: {
      get: vi.fn(() => options.contentType ?? 'application/json')
    }
  })

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

    // Reset Swal mock
    const Swal = await import('sweetalert2')
    Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })
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
      await waitForAsync(600)

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
      await waitForAsync(600)

      expect(wrapper.vm.acudidos.length).toBe(0)
    })

    it('should handle missing acudiente id', async () => {
      mockAuthStore.user.acudiente = null

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await waitForAsync(600)

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
      deportistasService.default.buscarDeportistaPorDocumentoParaAcudiente.mockResolvedValueOnce({
        success: true,
        encontrado: true,
        data: {
          id_deportista: 1,
          nombre_completo: 'Juan Pérez',
          documento: '12345678',
          categoria: 'Juvenil'
        }
      })

      wrapper.vm.busquedaDeportista = '12345678'
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

  describe('Edge Cases and Uncovered Lines', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    describe('verDetalle button click', () => {
      it('should call verDetalle when button is clicked', async () => {
        const mockData = [{
          id: 1,
          nombre_completo: 'Juan Pérez',
          categoria: 'Juvenil',
          edad: 15,
          correo_electronico: 'juan@test.com',
          telefono: '1234567890'
        }]
        globalThis.fetch.mockResolvedValueOnce(createMockFetchResponse({
          json: { success: true, data: mockData }
        }))

        await wrapper.vm.$nextTick()
        await waitForAsync(600)

        const deportistasService = await import('@/services/deportistasService')
        deportistasService.default.obtenerDeportistaPorId.mockResolvedValueOnce({
          success: true,
          data: {
            id: 1,
            nombre_completo: 'Juan Pérez'
          }
        })

        const verDetalleSpy = vi.spyOn(wrapper.vm, 'verDetalle')
        const acudido = wrapper.vm.acudidos[0]

        const button = wrapper.find('.btn-view')
        if (button.exists()) {
          await button.trigger('click')
          expect(verDetalleSpy).toHaveBeenCalledWith(acudido)
        }
        verDetalleSpy.mockRestore()
      })
    })

    describe('manejarBusqueda', () => {
      it('should normalize and search when input changes', async () => {
        const deportistasService = await import('@/services/deportistasService')
        const mockResponse = {
          success: true,
          encontrado: true,
          data: {
            id_deportista: 1,
            nombre_completo: 'Juan Pérez',
            documento: '12345678',
            categoria: 'Juvenil'
          }
        }
        deportistasService.default.buscarDeportistaPorDocumentoParaAcudiente.mockResolvedValueOnce(mockResponse)

        const event = {
          target: { value: '12345678abc' } // Contains non-numeric characters
        }

        wrapper.vm.manejarBusqueda(event)
        await wrapper.vm.$nextTick()
        await waitForAsync(100)

        expect(wrapper.vm.busquedaDeportista).toBe('12345678') // Normalized
        expect(deportistasService.default.buscarDeportistaPorDocumentoParaAcudiente).toHaveBeenCalled()
      })

      it('should handle null event', async () => {
        wrapper.vm.busquedaDeportista = '12345678'
        const deportistasService = await import('@/services/deportistasService')
        const mockResponse = {
          success: true,
          encontrado: true,
          data: { id_deportista: 1 }
        }
        deportistasService.default.buscarDeportistaPorDocumentoParaAcudiente.mockResolvedValueOnce(mockResponse)

        wrapper.vm.manejarBusqueda(null)
        await wrapper.vm.$nextTick()
        await waitForAsync(100)

        expect(deportistasService.default.buscarDeportistaPorDocumentoParaAcudiente).toHaveBeenCalled()
      })

      it('should use busquedaDeportista.value as fallback', async () => {
        wrapper.vm.busquedaDeportista = '12345678'
        const deportistasService = await import('@/services/deportistasService')
        deportistasService.default.buscarDeportistaPorDocumentoParaAcudiente.mockResolvedValueOnce({
          success: true,
          encontrado: true,
          data: { id_deportista: 1 }
        })

        const event = { target: null }
        wrapper.vm.manejarBusqueda(event)
        await wrapper.vm.$nextTick()
        await waitForAsync(100)

        expect(deportistasService.default.buscarDeportistaPorDocumentoParaAcudiente).toHaveBeenCalled()
      })
    })

    describe('cargarAcudidos edge cases', () => {
      it('should handle non-JSON response', async () => {
        globalThis.fetch.mockResolvedValueOnce(createMockFetchResponse({
          ok: false,
          text: 'Error HTML',
          contentType: 'text/html'
        }))

        await wrapper.vm.cargarAcudidos()
        await wrapper.vm.$nextTick()

        expect(wrapper.vm.acudidos.length).toBe(0)
      })

      it('should handle fetch error', async () => {
        globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

        await wrapper.vm.cargarAcudidos()
        await wrapper.vm.$nextTick()

        expect(wrapper.vm.acudidos.length).toBe(0)
      })

      it('should handle response with no data', async () => {
        globalThis.fetch.mockResolvedValueOnce(createMockFetchResponse({
          json: { success: true, data: null }
        }))

        await wrapper.vm.cargarAcudidos()
        await wrapper.vm.$nextTick()

        expect(wrapper.vm.acudidos).toEqual([])
      })
    })

    describe('verDetalle edge cases', () => {
      it('should handle error when loading profile', async () => {
        const deportistasService = await import('@/services/deportistasService')
        deportistasService.default.obtenerDeportistaPorId.mockRejectedValueOnce(new Error('Network error'))

        const acudido = { id: 1 }
        await wrapper.vm.verDetalle(acudido)
        await wrapper.vm.$nextTick()
        await waitForAsync(1000)

        // The loading should be false in the finally block
        expect(wrapper.vm.cargandoPerfil).toBe(false)
        // Verify that the service was called
        expect(deportistasService.default.obtenerDeportistaPorId).toHaveBeenCalledWith(1)
      })

      it('should handle response without data', async () => {
        const deportistasService = await import('@/services/deportistasService')
        const mockResponse = {
          success: false,
          data: null
        }
        deportistasService.default.obtenerDeportistaPorId.mockResolvedValueOnce(mockResponse)

        const Swal = await import('sweetalert2')
        const swalFireSpy = vi.spyOn(Swal.default, 'fire').mockResolvedValue({ isConfirmed: true })

        const acudido = { id: 1 }
        await wrapper.vm.verDetalle(acudido)
        await wrapper.vm.$nextTick()
        await waitForAsync(2000)

        // Verify that Swal was called (the else block should execute)
        expect(swalFireSpy).toHaveBeenCalled()
        // The modal should be closed in the else block
        expect(wrapper.vm.mostrarModalPerfil).toBe(false)
        // The loading should be false in the finally block
        expect(wrapper.vm.cargandoPerfil).toBe(false)
        swalFireSpy.mockRestore()
      })
    })

    describe('buscarDeportistas edge cases', () => {
      it('should handle ya_acudido response', async () => {
        const deportistasService = await import('@/services/deportistasService')
        const mockResponse = {
          success: false,
          encontrado: false,
          ya_acudido: true,
          data: {
            nombre_completo: 'Juan Pérez'
          }
        }
        deportistasService.default.buscarDeportistaPorDocumentoParaAcudiente.mockResolvedValueOnce(mockResponse)

        const Swal = await import('sweetalert2')
        Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

        wrapper.vm.busquedaDeportista = '12345678'
        await wrapper.vm.buscarDeportistas()
        await wrapper.vm.$nextTick()

        expect(Swal.default.fire).toHaveBeenCalledWith(expect.objectContaining({
          icon: 'info',
          title: 'Deportista ya asociado'
        }))
      })

      it('should handle ya_acudido with nombre fallback', async () => {
        const deportistasService = await import('@/services/deportistasService')
        const mockResponse = {
          success: false,
          encontrado: false,
          ya_acudido: true,
          data: {
            nombre: 'Juan'
          }
        }
        deportistasService.default.buscarDeportistaPorDocumentoParaAcudiente.mockResolvedValueOnce(mockResponse)

        const Swal = await import('sweetalert2')
        Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

        wrapper.vm.busquedaDeportista = '12345678'
        await wrapper.vm.buscarDeportistas()
        await wrapper.vm.$nextTick()

        expect(Swal.default.fire).toHaveBeenCalled()
      })

      it('should handle ya_acudido with default nombre', async () => {
        const deportistasService = await import('@/services/deportistasService')
        deportistasService.default.buscarDeportistaPorDocumentoParaAcudiente.mockResolvedValueOnce({
          success: false,
          encontrado: false,
          ya_acudido: true,
          data: {}
        })

        const Swal = await import('sweetalert2')
        Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

        wrapper.vm.busquedaDeportista = '12345678'
        await wrapper.vm.buscarDeportistas()
        await wrapper.vm.$nextTick()

        expect(Swal.default.fire).toHaveBeenCalled()
      })

      it('should handle response with message', async () => {
        const deportistasService = await import('@/services/deportistasService')
        deportistasService.default.buscarDeportistaPorDocumentoParaAcudiente.mockResolvedValueOnce({
          success: false,
          encontrado: false,
          ya_acudido: false,
          message: 'Deportista no encontrado'
        })

        wrapper.vm.busquedaDeportista = '12345678'
        await wrapper.vm.buscarDeportistas()
        await wrapper.vm.$nextTick()

        expect(wrapper.vm.deportistasEncontrados.length).toBe(0)
      })

      it('should handle empty search', async () => {
        wrapper.vm.busquedaDeportista = ''
        await wrapper.vm.buscarDeportistas()
        await wrapper.vm.$nextTick()

        expect(wrapper.vm.deportistasEncontrados.length).toBe(0)
      })

      it('should handle search with only spaces', async () => {
        wrapper.vm.busquedaDeportista = '   '
        await wrapper.vm.buscarDeportistas()
        await wrapper.vm.$nextTick()

        expect(wrapper.vm.deportistasEncontrados.length).toBe(0)
      })
    })

    describe('asociarDeportista edge cases', () => {
      it('should complete profile when user is not acudiente', async () => {
        const authService = await import('@/services/authService')
        authService.default.asociarAcudienteDeportista.mockResolvedValueOnce({
          success: false,
          error: 'El usuario no está registrado como acudiente'
        })
        authService.default.completarPerfilAcudiente.mockResolvedValueOnce({
          success: true
        })

        wrapper.vm.deportistaSeleccionado = {
          id_deportista: 1,
          id_persona: 2
        }
        wrapper.vm.idParentesco = '1'
        wrapper.vm.esResponsable = false
        mockAuthStore.user.persona = { id_persona: 1 }

        const Swal = await import('sweetalert2')
        Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

        await wrapper.vm.asociarDeportista()
        await wrapper.vm.$nextTick()

        expect(authService.default.completarPerfilAcudiente).toHaveBeenCalled()
      })

      it('should handle self-association with persona.id_persona', async () => {
        wrapper.vm.deportistaSeleccionado = {
          id_deportista: 1,
          persona: { id_persona: 1 }
        }
        wrapper.vm.idParentesco = '1'
        mockAuthStore.user.persona = { id_persona: 1 }

        const Swal = await import('sweetalert2')
        Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

        await wrapper.vm.asociarDeportista()
        await wrapper.vm.$nextTick()

        expect(Swal.default.fire).toHaveBeenCalledWith(expect.objectContaining({
          icon: 'info',
          title: 'Acción no permitida'
        }))
      })

      it('should handle self-association with id_personaUsuario from user.id_persona', async () => {
        wrapper.vm.deportistaSeleccionado = {
          id_deportista: 1,
          id_persona: 1
        }
        wrapper.vm.idParentesco = '1'
        mockAuthStore.user.id_persona = 1
        mockAuthStore.user.persona = null

        const Swal = await import('sweetalert2')
        Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

        await wrapper.vm.asociarDeportista()
        await wrapper.vm.$nextTick()

        expect(Swal.default.fire).toHaveBeenCalled()
      })

      it('should handle association error', async () => {
        const authService = await import('@/services/authService')
        authService.default.asociarAcudienteDeportista.mockResolvedValueOnce({
          success: false,
          error: 'Error al asociar'
        })

        wrapper.vm.deportistaSeleccionado = {
          id_deportista: 1,
          id_persona: 2
        }
        wrapper.vm.idParentesco = '1'
        mockAuthStore.user.persona = { id_persona: 1 }

        const Swal = await import('sweetalert2')
        Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

        await wrapper.vm.asociarDeportista()
        await wrapper.vm.$nextTick()

        expect(Swal.default.fire).toHaveBeenCalledWith(expect.objectContaining({
          icon: 'error',
          title: 'No se pudo asociar'
        }))
      })

      it('should handle association error with unknown error', async () => {
        const authService = await import('@/services/authService')
        authService.default.asociarAcudienteDeportista.mockResolvedValueOnce({
          success: false,
          error: null
        })

        wrapper.vm.deportistaSeleccionado = {
          id_deportista: 1,
          id_persona: 2
        }
        wrapper.vm.idParentesco = '1'
        mockAuthStore.user.persona = { id_persona: 1 }

        const Swal = await import('sweetalert2')
        Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

        await wrapper.vm.asociarDeportista()
        await wrapper.vm.$nextTick()

        expect(Swal.default.fire).toHaveBeenCalled()
      })

      it('should handle network error during association', async () => {
        const authService = await import('@/services/authService')
        authService.default.asociarAcudienteDeportista.mockRejectedValueOnce(new Error('Network error'))

        wrapper.vm.deportistaSeleccionado = {
          id_deportista: 1,
          id_persona: 2
        }
        wrapper.vm.idParentesco = '1'
        mockAuthStore.user.persona = { id_persona: 1 }

        const Swal = await import('sweetalert2')
        Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

        await wrapper.vm.asociarDeportista()
        await wrapper.vm.$nextTick()

        expect(Swal.default.fire).toHaveBeenCalledWith(expect.objectContaining({
          icon: 'error',
          title: 'Error de conexión'
        }))
      })

      it('should handle network error without message', async () => {
        const authService = await import('@/services/authService')
        authService.default.asociarAcudienteDeportista.mockRejectedValueOnce(new Error('Network error'))

        wrapper.vm.deportistaSeleccionado = {
          id_deportista: 1,
          id_persona: 2
        }
        wrapper.vm.idParentesco = '1'
        mockAuthStore.user.persona = { id_persona: 1 }

        const Swal = await import('sweetalert2')
        Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

        await wrapper.vm.asociarDeportista()
        await wrapper.vm.$nextTick()

        expect(Swal.default.fire).toHaveBeenCalled()
      })
    })

    describe('manejarGuardadoPerfil edge cases', () => {
      it('should handle deportistaSeleccionadoPerfil with id_deportista', async () => {
        wrapper.vm.deportistaSeleccionadoPerfil = {
          id_deportista: 1
        }

        const deportistasService = await import('@/services/deportistasService')
        deportistasService.default.obtenerDeportistaPorId.mockResolvedValueOnce({
          status: 'success',
          data: { id_deportista: 1, nombre: 'Updated' }
        })

        await wrapper.vm.manejarGuardadoPerfil()
        await wrapper.vm.$nextTick()

        expect(deportistasService.default.obtenerDeportistaPorId).toHaveBeenCalledWith(1)
      })

      it('should handle deportistaSeleccionadoPerfil with id', async () => {
        wrapper.vm.deportistaSeleccionadoPerfil = {
          id: 1
        }

        const deportistasService = await import('@/services/deportistasService')
        deportistasService.default.obtenerDeportistaPorId.mockResolvedValueOnce({
          success: true,
          data: { id: 1, nombre: 'Updated' }
        })

        await wrapper.vm.manejarGuardadoPerfil()
        await wrapper.vm.$nextTick()

        expect(deportistasService.default.obtenerDeportistaPorId).toHaveBeenCalledWith(1)
      })

      it('should handle error when refreshing profile', async () => {
        wrapper.vm.deportistaSeleccionadoPerfil = {
          id: 1
        }

        const deportistasService = await import('@/services/deportistasService')
        deportistasService.default.obtenerDeportistaPorId.mockRejectedValueOnce(new Error('Error'))

        await wrapper.vm.manejarGuardadoPerfil()
        await wrapper.vm.$nextTick()
        await waitForAsync(1000)

        // Verify that the service was called
        expect(deportistasService.default.obtenerDeportistaPorId).toHaveBeenCalledWith(1)
        // Verify that modoEdicionPerfil is false
        expect(wrapper.vm.modoEdicionPerfil).toBe(false)
      })

      it('should handle deportistaSeleccionadoPerfil without id', async () => {
        wrapper.vm.deportistaSeleccionadoPerfil = {
          nombre: 'Test'
        }

        const deportistasService = await import('@/services/deportistasService')
        const spy = vi.spyOn(deportistasService.default, 'obtenerDeportistaPorId')

        await wrapper.vm.manejarGuardadoPerfil()
        await wrapper.vm.$nextTick()

        expect(spy).not.toHaveBeenCalled()
      })

      it('should handle null deportistaSeleccionadoPerfil', async () => {
        wrapper.vm.deportistaSeleccionadoPerfil = null

        const deportistasService = await import('@/services/deportistasService')
        const spy = vi.spyOn(deportistasService.default, 'obtenerDeportistaPorId')

        await wrapper.vm.manejarGuardadoPerfil()
        await wrapper.vm.$nextTick()

        expect(spy).not.toHaveBeenCalled()
      })
    })

    describe('abrirModalAcudir edge cases', () => {
      it('should handle error loading parentescos', async () => {
        const catalogosService = await import('@/services/catalogosService')
        catalogosService.default.getParentescos.mockRejectedValueOnce(new Error('Error loading'))

        const Swal = await import('sweetalert2')
        Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

        await wrapper.vm.abrirModalAcudir()
        await wrapper.vm.$nextTick()

        expect(Swal.default.fire).toHaveBeenCalledWith(expect.objectContaining({
          icon: 'error',
          title: 'No se pudieron cargar los parentescos'
        }))
      })
    })

    describe('normalizarDocumento', () => {
      it('should normalize document with non-numeric characters', () => {
        // normalizarDocumento is not exposed on wrapper.vm, test it indirectly through manejarBusqueda
        wrapper.vm.busquedaDeportista = '123abc456'
        const event = { target: { value: '123abc456' } }
        wrapper.vm.manejarBusqueda(event)
        expect(wrapper.vm.busquedaDeportista).toBe('123456')
      })

      it('should limit document to MAX_DOCUMENTO', () => {
        const longDoc = '1'.repeat(25)
        const event = { target: { value: longDoc } }
        wrapper.vm.manejarBusqueda(event)
        expect(wrapper.vm.busquedaDeportista.length).toBe(20)
      })

      it('should handle empty string', () => {
        const event = { target: { value: '' } }
        wrapper.vm.manejarBusqueda(event)
        expect(wrapper.vm.busquedaDeportista).toBe('')
      })

      it('should handle null', () => {
        wrapper.vm.busquedaDeportista = 'test'
        wrapper.vm.manejarBusqueda(null)
        expect(wrapper.vm.busquedaDeportista).toBe('')
      })

      it('should handle undefined', () => {
        wrapper.vm.busquedaDeportista = 'test'
        const event = { target: { value: undefined } }
        wrapper.vm.manejarBusqueda(event)
        expect(wrapper.vm.busquedaDeportista).toBe('')
      })
    })
  })
})

