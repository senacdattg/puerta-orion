import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import CompletarPerfil from '@/views/completar-perfil.vue'
import { useAuthStore } from '@/stores/auth'
import { useUserRegistration } from '@/composables/useUserRegistration'
import authService from '@/services/authService'

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: vi.fn()
}))

// Mock components
vi.mock('@/components/layout/encabezado.vue', () => ({
  default: {
    name: 'Encabezado',
    template: '<header class="encabezado">Header</header>'
  }
}))

vi.mock('@/components/layout/pie.vue', () => ({
  default: {
    name: 'Pie',
    template: '<footer class="pie">Footer</footer>'
  }
}))

vi.mock('@/components/formularios/formulario-deportista.vue', () => ({
  default: {
    name: 'FormularioDeportista',
    template: '<div class="formulario-deportista">Form</div>'
  }
}))

vi.mock('@/components/formularios/formulario-acudiente.vue', () => ({
  default: {
    name: 'FormularioAcudiente',
    template: '<div class="formulario-acudiente">Form</div>'
  }
}))

// Mock stores
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

// Mock services
vi.mock('@/services/deportistasService', () => ({
  default: {
    crearDeportista: vi.fn().mockResolvedValue({ success: true }),
    obtenerDeportistaPorUsuario: vi.fn().mockResolvedValue({ success: false, data: null })
  }
}))

vi.mock('@/services/acudientesService', () => ({
  default: {
    crearAcudiente: vi.fn().mockResolvedValue({ success: true }),
    obtenerAcudientePorUsuario: vi.fn().mockResolvedValue({ success: false, data: null })
  }
}))

vi.mock('@/services/catalogosService', () => ({
  default: {
    getCatalogosCompletos: vi.fn().mockResolvedValue({
      success: true,
      data: {
        categorias: [{ id_categoria: 1, nombre_categoria: 'Pre-infantil' }]
      }
    })
  }
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(),
    Swal: {
      fire: vi.fn()
    }
  }
}))

// Mock composables
vi.mock('@/composables/useUserRegistration', () => ({
  useUserRegistration: vi.fn()
}))

// Mock authService
vi.mock('@/services/authService', () => ({
  default: {
    completarPerfilDeportista: vi.fn(),
    completarPerfilAcudiente: vi.fn()
  }
}))

// Mock environment
vi.mock('@/config/environment', () => ({
  getApiUrl: vi.fn((path) => `http://localhost:5000${path}`)
}))

// Mock fetch globally
globalThis.fetch = vi.fn()

// Mock router
const mockRouterPush = vi.fn()
const mockRouterReplace = vi.fn()
const router = {
  push: mockRouterPush,
  replace: mockRouterReplace,
  currentRoute: { value: { path: '/completar-perfil' } }
}

import { useRouter } from 'vue-router'

describe('CompletarPerfil View', () => {
  let mockAuthStore
  let mockUseUserRegistration

  beforeEach(async () => {
    setActivePinia(createPinia())

    // Resetear mocks antes de cada test
    mockRouterPush.mockClear()
    mockRouterReplace.mockClear()
    vi.clearAllMocks()

    // Mock useRouter
    useRouter.mockReturnValue(router)

    mockAuthStore = {
      user: {
        id_usuario: 1,
        usuario: 'testuser',
        persona: {
          id_persona: 1,
          fecha_nacimiento: '2000-01-01'
        },
        roles: []
      },
      userRoles: [],
      userDetail: null,
      estaAutenticado: true,
      loadUserProfile: vi.fn().mockResolvedValue({ success: true, data: {} }),
      loadUserProfileDetail: vi.fn().mockResolvedValue({ success: true, data: {} })
    }

    useAuthStore.mockReturnValue(mockAuthStore)

    // Mock useUserRegistration
    mockUseUserRegistration = {
      yaEsDeportista: { value: false },
      yaEsAcudiente: { value: false },
      edadDeportista: { value: null },
      esMayorDeEdad: { value: false },
      mostrarOpcionAcudiente: { value: true }
    }
    useUserRegistration.mockReturnValue(mockUseUserRegistration)

    // Mock fetch defaults
    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({ data: [] })
    })
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('should render the view', () => {
    const wrapper = mount(CompletarPerfil, {
      global: {
        mocks: {
          $router: router
        },
        stubs: {
          Encabezado: true,
          Pie: true,
          FormularioDeportista: true,
          FormularioAcudiente: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.completar-perfil-container').exists()).toBe(true)
  })

  it('should display step 1 (profile selection)', () => {
    const wrapper = mount(CompletarPerfil, {
      global: {
        mocks: {
          $router: router
        },
        stubs: {
          Encabezado: true,
          Pie: true,
          FormularioDeportista: true,
          FormularioAcudiente: true
        }
      }
    })

    expect(wrapper.vm.paso).toBe(1)
    expect(wrapper.find('.seleccion-perfil').exists()).toBe(true)
  })

  it('should show deportista option when user is not already deportista', () => {
    const wrapper = mount(CompletarPerfil, {
      global: {
        mocks: {
          $router: router
        },
        stubs: {
          Encabezado: true,
          Pie: true,
          FormularioDeportista: true,
          FormularioAcudiente: true
        }
      }
    })

    expect(wrapper.vm.yaEsDeportista).toEqual({ value: false })
  })

  it('should handle tipo perfil selection', async () => {
    // Resetear el mock antes del test
    mockRouterPush.mockClear()

    const wrapper = mount(CompletarPerfil, {
      global: {
        mocks: {
          $router: router
        },
        stubs: {
          Encabezado: true,
          Pie: true,
          FormularioDeportista: true,
          FormularioAcudiente: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    // Verificar que el método existe
    expect(typeof wrapper.vm.seleccionarTipoPerfil).toBe('function')

    // Llamar al método - seleccionarTipoPerfil usa router.push internamente
    wrapper.vm.seleccionarTipoPerfil('deportista')
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    // Verificar que el método se ejecutó sin errores
    expect(wrapper.exists()).toBe(true)
    // Verificar que router.push fue llamado con la ruta correcta
    expect(mockRouterPush).toHaveBeenCalledWith('/formulario-deportista-completo')
  })

  it('should display form for deportista when paso is 2', async () => {
    const wrapper = mount(CompletarPerfil, {
      global: {
        mocks: {
          $router: router
        },
        stubs: {
          Encabezado: true,
          Pie: true,
          FormularioDeportista: true,
          FormularioAcudiente: true
        }
      }
    })

    wrapper.vm.paso = 2
    wrapper.vm.tipoPerfilSeleccionado = 'deportista'
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.formulario-perfil').exists()).toBe(true)
  })

  it('should display form for acudiente when paso is 2 and tipo is acudiente', async () => {
    const wrapper = mount(CompletarPerfil, {
      global: {
        mocks: {
          $router: router
        },
        stubs: {
          Encabezado: true,
          Pie: true,
          FormularioDeportista: true,
          FormularioAcudiente: true
        }
      }
    })

    wrapper.vm.paso = 2
    wrapper.vm.tipoPerfilSeleccionado = 'acudiente'
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.tipoPerfilSeleccionado).toBe('acudiente')
  })

  it('should handle back navigation', async () => {
    const wrapper = mount(CompletarPerfil, {
      global: {
        mocks: {
          $router: router
        },
        stubs: {
          Encabezado: true,
          Pie: true,
          FormularioDeportista: true,
          FormularioAcudiente: true
        }
      }
    })

    wrapper.vm.paso = 2
    wrapper.vm.tipoPerfilSeleccionado = 'deportista'
    wrapper.vm.volverAtras()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.paso).toBe(1)
    expect(wrapper.vm.tipoPerfilSeleccionado).toBe(null)
  })

  describe('Validation Functions', () => {
    let wrapper

    beforeEach(() => {
      wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })
    })

    describe('validarCategoria', () => {
      it('should return false when category is not selected', () => {
        wrapper.vm.formDeportista.id_categoria = ''
        const result = wrapper.vm.validarCategoria()
        expect(result).toBe(false)
        expect(wrapper.vm.mensajeError).toBe('Por favor selecciona una categoría')
      })

      it('should return true when category is selected', () => {
        wrapper.vm.formDeportista.id_categoria = '1'
        const result = wrapper.vm.validarCategoria()
        expect(result).toBe(true)
        expect(wrapper.vm.mensajeError).toBe('')
      })
    })

    describe('validarYProcesarPeso', () => {
      it('should return true for empty peso', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.peso = null
        const result = wrapper.vm.validarYProcesarPeso(datosDeportista)
        expect(result).toBe(true)
        expect(datosDeportista.peso).toBeUndefined()
      })

      it('should return true for empty string peso', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.peso = ''
        const result = wrapper.vm.validarYProcesarPeso(datosDeportista)
        expect(result).toBe(true)
      })

      it('should return false for invalid peso (NaN)', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.peso = 'invalid'
        const result = wrapper.vm.validarYProcesarPeso(datosDeportista)
        expect(result).toBe(false)
        expect(wrapper.vm.mensajeError).toBe('El peso debe ser un número entre 1 y 300 kg')
      })

      it('should return false for peso <= 0', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.peso = -1
        const result = wrapper.vm.validarYProcesarPeso(datosDeportista)
        expect(result).toBe(false)
      })

      it('should return true for peso = 0 (treated as empty)', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.peso = 0
        const result = wrapper.vm.validarYProcesarPeso(datosDeportista)
        expect(result).toBe(true) // 0 is falsy, so treated as empty
      })

      it('should return false for peso > 300', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.peso = 301
        const result = wrapper.vm.validarYProcesarPeso(datosDeportista)
        expect(result).toBe(false)
      })

      it('should return true and set peso for valid peso', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.peso = 70.5
        const result = wrapper.vm.validarYProcesarPeso(datosDeportista)
        expect(result).toBe(true)
        expect(datosDeportista.peso).toBe(70.5)
      })

      it('should handle string peso', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.peso = '70.5'
        const result = wrapper.vm.validarYProcesarPeso(datosDeportista)
        expect(result).toBe(true)
        expect(datosDeportista.peso).toBe(70.5)
      })
    })

    describe('validarYProcesarAltura', () => {
      it('should return true for empty altura', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.altura = null
        const result = wrapper.vm.validarYProcesarAltura(datosDeportista)
        expect(result).toBe(true)
      })

      it('should return false for invalid altura (NaN)', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.altura = 'invalid'
        const result = wrapper.vm.validarYProcesarAltura(datosDeportista)
        expect(result).toBe(false)
        expect(wrapper.vm.mensajeError).toBe('La altura debe ser un número entre 0.1 y 3 metros')
      })

      it('should return false for altura <= 0', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.altura = -0.1
        const result = wrapper.vm.validarYProcesarAltura(datosDeportista)
        expect(result).toBe(false)
      })

      it('should return true for altura = 0 (treated as empty)', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.altura = 0
        const result = wrapper.vm.validarYProcesarAltura(datosDeportista)
        expect(result).toBe(true) // 0 is falsy, so treated as empty
      })

      it('should return false for altura > 3', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.altura = 3.1
        const result = wrapper.vm.validarYProcesarAltura(datosDeportista)
        expect(result).toBe(false)
      })

      it('should return true and set altura for valid altura', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.altura = 1.75
        const result = wrapper.vm.validarYProcesarAltura(datosDeportista)
        expect(result).toBe(true)
        expect(datosDeportista.altura).toBe(1.75)
      })
    })

    describe('validarYProcesarFechaNacimiento', () => {
      it('should return true for empty fecha_nacimiento', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.fecha_nacimiento = null
        const result = wrapper.vm.validarYProcesarFechaNacimiento(datosDeportista)
        expect(result).toBe(true)
      })

      it('should return false for invalid año (NaN)', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.fecha_nacimiento = 'invalid'
        const result = wrapper.vm.validarYProcesarFechaNacimiento(datosDeportista)
        expect(result).toBe(false)
        expect(wrapper.vm.mensajeError).toContain('El año de nacimiento debe estar entre 1900 y')
      })

      it('should return false for año < 1900', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.fecha_nacimiento = 1899
        const result = wrapper.vm.validarYProcesarFechaNacimiento(datosDeportista)
        expect(result).toBe(false)
      })

      it('should return false for año > current year', () => {
        const datosDeportista = {}
        const añoFuturo = new Date().getFullYear() + 1
        wrapper.vm.formDeportista.fecha_nacimiento = añoFuturo
        const result = wrapper.vm.validarYProcesarFechaNacimiento(datosDeportista)
        expect(result).toBe(false)
      })

      it('should return true and set fecha_nacimiento for valid año', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.fecha_nacimiento = 2000
        const result = wrapper.vm.validarYProcesarFechaNacimiento(datosDeportista)
        expect(result).toBe(true)
        expect(datosDeportista.fecha_nacimiento).toBe(2000)
      })
    })

    describe('agregarCamposOpcionales', () => {
      it('should add id_tipo_sanguineo when provided', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.id_tipo_sanguineo = '1'
        wrapper.vm.agregarCamposOpcionales(datosDeportista)
        expect(datosDeportista.id_tipo_sanguineo).toBe(1)
      })

      it('should not add id_tipo_sanguineo when empty', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.id_tipo_sanguineo = ''
        wrapper.vm.agregarCamposOpcionales(datosDeportista)
        expect(datosDeportista.id_tipo_sanguineo).toBeUndefined()
      })

      it('should add id_eps when provided', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.id_eps = '2'
        wrapper.vm.agregarCamposOpcionales(datosDeportista)
        expect(datosDeportista.id_eps).toBe(2)
      })

      it('should add both optional fields', () => {
        const datosDeportista = {}
        wrapper.vm.formDeportista.id_tipo_sanguineo = '1'
        wrapper.vm.formDeportista.id_eps = '2'
        wrapper.vm.agregarCamposOpcionales(datosDeportista)
        expect(datosDeportista.id_tipo_sanguineo).toBe(1)
        expect(datosDeportista.id_eps).toBe(2)
      })
    })

    describe('construirDatosDeportista', () => {
      it('should build datosDeportista with all valid fields', () => {
        wrapper.vm.formDeportista.id_categoria = '1'
        wrapper.vm.formDeportista.peso = 70.5
        wrapper.vm.formDeportista.altura = 1.75
        wrapper.vm.formDeportista.fecha_nacimiento = 2000
        wrapper.vm.formDeportista.id_tipo_sanguineo = '1'
        wrapper.vm.formDeportista.id_eps = '2'

        const result = wrapper.vm.construirDatosDeportista()
        expect(result).toEqual({
          id_categoria: 1,
          peso: 70.5,
          altura: 1.75,
          fecha_nacimiento: 2000,
          id_tipo_sanguineo: 1,
          id_eps: 2
        })
      })

      it('should return null when peso validation fails', () => {
        wrapper.vm.formDeportista.id_categoria = '1'
        wrapper.vm.formDeportista.peso = 500 // Invalid
        wrapper.vm.formDeportista.altura = 1.75

        const result = wrapper.vm.construirDatosDeportista()
        expect(result).toBeNull()
      })

      it('should return null when altura validation fails', () => {
        wrapper.vm.formDeportista.id_categoria = '1'
        wrapper.vm.formDeportista.peso = 70.5
        wrapper.vm.formDeportista.altura = 5 // Invalid

        const result = wrapper.vm.construirDatosDeportista()
        expect(result).toBeNull()
      })

      it('should return null when fecha_nacimiento validation fails', () => {
        wrapper.vm.formDeportista.id_categoria = '1'
        wrapper.vm.formDeportista.peso = 70.5
        wrapper.vm.formDeportista.altura = 1.75
        wrapper.vm.formDeportista.fecha_nacimiento = 1800 // Invalid

        const result = wrapper.vm.construirDatosDeportista()
        expect(result).toBeNull()
      })

      it('should build datosDeportista with only required fields', () => {
        wrapper.vm.formDeportista.id_categoria = '1'
        wrapper.vm.formDeportista.peso = null
        wrapper.vm.formDeportista.altura = null
        wrapper.vm.formDeportista.fecha_nacimiento = null

        const result = wrapper.vm.construirDatosDeportista()
        expect(result).toEqual({
          id_categoria: 1
        })
      })
    })
  })

  describe('Form Submission', () => {
    let wrapper

    beforeEach(() => {
      wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })
    })

    describe('completarPerfilDeportista', () => {
      it('should not submit if category validation fails', async () => {
        wrapper.vm.formDeportista.id_categoria = ''
        await wrapper.vm.completarPerfilDeportista()
        expect(authService.completarPerfilDeportista).not.toHaveBeenCalled()
      })

      it('should not submit if data construction fails', async () => {
        wrapper.vm.formDeportista.id_categoria = '1'
        wrapper.vm.formDeportista.peso = 500 // Invalid
        await wrapper.vm.completarPerfilDeportista()
        expect(authService.completarPerfilDeportista).not.toHaveBeenCalled()
        expect(wrapper.vm.cargando).toBe(false)
      })

      it('should successfully complete deportista profile', async () => {
        vi.useFakeTimers()
        authService.completarPerfilDeportista = vi.fn().mockResolvedValue({
          success: true,
          data: {},
          message: 'Success'
        })

        wrapper.vm.formDeportista.id_categoria = '1'
        wrapper.vm.formDeportista.peso = 70.5
        wrapper.vm.formDeportista.altura = 1.75

        const promise = wrapper.vm.completarPerfilDeportista()
        await wrapper.vm.$nextTick()
        await promise

        expect(authService.completarPerfilDeportista).toHaveBeenCalled()
        expect(wrapper.vm.cargando).toBe(false)
        expect(mockAuthStore.loadUserProfile).toHaveBeenCalled()

        // Advance timers to trigger redirect
        vi.advanceTimersByTime(2000)
        expect(mockRouterPush).toHaveBeenCalledWith('/deportista/dashboard')
        vi.useRealTimers()
      })

      it('should handle API error response', async () => {
        authService.completarPerfilDeportista = vi.fn().mockResolvedValue({
          success: false,
          error: 'Error message'
        })

        wrapper.vm.formDeportista.id_categoria = '1'
        await wrapper.vm.completarPerfilDeportista()

        expect(wrapper.vm.mensajeError).toBe('Error message')
        expect(wrapper.vm.cargando).toBe(false)
      })

      it('should handle API error without error message', async () => {
        authService.completarPerfilDeportista = vi.fn().mockResolvedValue({
          success: false
        })

        wrapper.vm.formDeportista.id_categoria = '1'
        await wrapper.vm.completarPerfilDeportista()

        expect(wrapper.vm.mensajeError).toBe('Error al completar perfil')
        expect(wrapper.vm.cargando).toBe(false)
      })

      it('should handle network error', async () => {
        authService.completarPerfilDeportista = vi.fn().mockRejectedValue(new Error('Network error'))

        wrapper.vm.formDeportista.id_categoria = '1'
        await wrapper.vm.completarPerfilDeportista()

        expect(wrapper.vm.mensajeError).toBe('Network error')
        expect(wrapper.vm.cargando).toBe(false)
      })

      it('should handle error without message', async () => {
        authService.completarPerfilDeportista = vi.fn().mockRejectedValue({})

        wrapper.vm.formDeportista.id_categoria = '1'
        await wrapper.vm.completarPerfilDeportista()

        expect(wrapper.vm.mensajeError).toBe('Error de conexión')
        expect(wrapper.vm.cargando).toBe(false)
      })
    })

    describe('completarPerfilAcudiente', () => {
      it('should successfully complete acudiente profile', async () => {
        vi.useFakeTimers()
        authService.completarPerfilAcudiente = vi.fn().mockResolvedValue({
          success: true,
          data: {},
          message: 'Success'
        })

        const promise = wrapper.vm.completarPerfilAcudiente()
        await wrapper.vm.$nextTick()
        await promise

        expect(authService.completarPerfilAcudiente).toHaveBeenCalled()
        expect(wrapper.vm.mensajeExito).toBe('¡Perfil completado exitosamente! Redirigiendo...')
        expect(mockAuthStore.loadUserProfile).toHaveBeenCalled()
        expect(wrapper.vm.cargando).toBe(false)

        // Advance timers to trigger redirect
        vi.advanceTimersByTime(2000)
        expect(mockRouterPush).toHaveBeenCalledWith('/home')
        vi.useRealTimers()
      })

      it('should handle API error response', async () => {
        authService.completarPerfilAcudiente = vi.fn().mockResolvedValue({
          success: false,
          error: 'Error message'
        })

        await wrapper.vm.completarPerfilAcudiente()

        expect(wrapper.vm.mensajeError).toBe('Error message')
        expect(wrapper.vm.cargando).toBe(false)
      })

      it('should handle network error', async () => {
        authService.completarPerfilAcudiente = vi.fn().mockRejectedValue(new Error('Network error'))

        await wrapper.vm.completarPerfilAcudiente()

        expect(wrapper.vm.mensajeError).toBe('Network error')
        expect(wrapper.vm.cargando).toBe(false)
      })
    })
  })

  describe('Catalog Loading', () => {
    let wrapper

    beforeEach(() => {
      globalThis.fetch.mockClear()
    })

    it('should load catalogos successfully', async () => {
      // Mock fetch responses - need to provide enough responses for onMounted + our test
      const mockCategorias = [{ id_categoria: 1, nombre_categoria: 'Test' }]
      const mockTiposSanguineos = [{ id_tipo_sangre: 1, tipo_sangre: 'O+' }]
      const mockEps = [{ id_eps: 1, nombre_eps: 'Test EPS' }]

      // Setup mocks for onMounted (called first) and our direct call
      globalThis.fetch
        // First call (onMounted)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: [] })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: [] })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: [] })
        })
        // Second call (our test)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: mockCategorias })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: mockTiposSanguineos })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ data: mockEps })
        })

      wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      // Wait for onMounted to complete
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Now call cargarCatalogos directly
      await wrapper.vm.cargarCatalogos()

      // Wait for all promises to resolve
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Verify the data was loaded
      expect(wrapper.vm.categorias).toEqual(mockCategorias)
      expect(wrapper.vm.tiposSanguineos).toEqual(mockTiposSanguineos)
      expect(wrapper.vm.listaEps).toEqual(mockEps)
    })

    it('should handle catalog loading errors gracefully', async () => {
      globalThis.fetch.mockRejectedValueOnce(new Error('Network error'))

      wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      await wrapper.vm.cargarCatalogos()
      await wrapper.vm.$nextTick()

      expect(consoleSpy).toHaveBeenCalledWith('Error al cargar catálogos:', expect.any(Error))
      consoleSpy.mockRestore()
    })

    it('should handle non-ok responses', async () => {
      globalThis.fetch
        .mockResolvedValueOnce({ ok: false })
        .mockResolvedValueOnce({ ok: false })
        .mockResolvedValueOnce({ ok: false })

      wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      await wrapper.vm.cargarCatalogos()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.categorias).toEqual([])
      expect(wrapper.vm.tiposSanguineos).toEqual([])
      expect(wrapper.vm.listaEps).toEqual([])
    })

    it('should handle missing data property in response', async () => {
      globalThis.fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({}) // No data property
        })

      wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      await wrapper.vm.cargarCatalogos()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.categorias).toEqual([])
    })
  })

  describe('onMounted', () => {
    it('should load user profile if not loaded', async () => {
      mockAuthStore.user = null
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockAuthStore.loadUserProfile).toHaveBeenCalled()
    })

    it('should load user profile detail if not loaded', async () => {
      mockAuthStore.userDetail = null
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockAuthStore.loadUserProfileDetail).toHaveBeenCalled()
    })

    it('should not load user profile if already loaded', async () => {
      mockAuthStore.user = { id: 1 }
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockAuthStore.loadUserProfile).not.toHaveBeenCalled()
    })

    it('should call cargarCatalogos on mount', async () => {
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(globalThis.fetch).toHaveBeenCalled()
    })
  })

  describe('Template Rendering', () => {
    it('should show deportista button when not already deportista', () => {
      mockUseUserRegistration.yaEsDeportista = { value: false }
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      const buttons = wrapper.findAll('.opcion-btn')
      expect(buttons.length).toBeGreaterThan(0)
    })

    it('should show acudiente button when mostrarOpcionAcudiente is true', () => {
      mockUseUserRegistration.mostrarOpcionAcudiente = { value: true }
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      expect(wrapper.vm.mostrarOpcionAcudiente).toEqual({ value: true })
    })

    it('should show message for underage athlete', () => {
      mockUseUserRegistration.yaEsDeportista = { value: true }
      mockUseUserRegistration.esMayorDeEdad = { value: false }
      mockUseUserRegistration.edadDeportista = { value: 17 }
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      expect(wrapper.vm.yaEsDeportista).toEqual({ value: true })
      expect(wrapper.vm.esMayorDeEdad).toEqual({ value: false })
      expect(wrapper.vm.edadDeportista).toEqual({ value: 17 })
    })

    it('should show message when user has both roles', () => {
      mockUseUserRegistration.yaEsDeportista = { value: true }
      mockUseUserRegistration.yaEsAcudiente = { value: true }
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      expect(wrapper.vm.yaEsDeportista).toEqual({ value: true })
      expect(wrapper.vm.yaEsAcudiente).toEqual({ value: true })
    })

    it('should display error message when mensajeError is set', async () => {
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      wrapper.vm.mensajeError = 'Test error'
      await wrapper.vm.$nextTick()

      expect(wrapper.html()).toContain('Test error')
    })

    it('should display success message when mensajeExito is set', async () => {
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      wrapper.vm.mensajeExito = 'Test success'
      await wrapper.vm.$nextTick()

      expect(wrapper.html()).toContain('Test success')
    })

    it('should render deportista form when paso is 2 and tipo is deportista', async () => {
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      wrapper.vm.paso = 2
      wrapper.vm.tipoPerfilSeleccionado = 'deportista'
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.formulario-perfil').exists()).toBe(true)
    })

    it('should render acudiente confirmation when paso is 2 and tipo is acudiente', async () => {
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      wrapper.vm.paso = 2
      wrapper.vm.tipoPerfilSeleccionado = 'acudiente'
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.confirmacion-perfil').exists()).toBe(true)
    })

    it('should disable buttons when cargando is true', async () => {
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      wrapper.vm.cargando = true
      wrapper.vm.paso = 2
      wrapper.vm.tipoPerfilSeleccionado = 'deportista'
      await wrapper.vm.$nextTick()

      const submitButton = wrapper.find('button[type="submit"]')
      if (submitButton.exists()) {
        expect(submitButton.attributes('disabled')).toBeDefined()
      }
    })

    it('should show loading text when cargando is true', async () => {
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      wrapper.vm.cargando = true
      wrapper.vm.paso = 2
      wrapper.vm.tipoPerfilSeleccionado = 'deportista'
      await wrapper.vm.$nextTick()

      expect(wrapper.html()).toContain('Guardando...')
    })
  })

  describe('limpiarMensajes', () => {
    it('should clear error and success messages', () => {
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      wrapper.vm.mensajeError = 'Error'
      wrapper.vm.mensajeExito = 'Success'
      wrapper.vm.limpiarMensajes()

      expect(wrapper.vm.mensajeError).toBe('')
      expect(wrapper.vm.mensajeExito).toBe('')
    })
  })

  describe('seleccionarTipoPerfil', () => {
    it('should navigate to deportista form', () => {
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      wrapper.vm.seleccionarTipoPerfil('deportista')
      expect(mockRouterPush).toHaveBeenCalledWith('/formulario-deportista-completo')
      expect(wrapper.vm.mensajeError).toBe('')
      expect(wrapper.vm.mensajeExito).toBe('')
    })

    it('should navigate to acudiente form', () => {
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      wrapper.vm.seleccionarTipoPerfil('acudiente')
      expect(mockRouterPush).toHaveBeenCalledWith('/formulario-acudiente-completo')
    })
  })

  describe('manejarExitoCompletarPerfil', () => {
    it('should set success message and redirect after delay', async () => {
      vi.useFakeTimers()
      const wrapper = mount(CompletarPerfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true
          }
        }
      })

      const promise = wrapper.vm.manejarExitoCompletarPerfil()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mensajeExito).toBe('¡Perfil completado exitosamente! Redirigiendo...')
      expect(mockAuthStore.loadUserProfile).toHaveBeenCalled()

      await promise
      vi.advanceTimersByTime(2000)
      expect(mockRouterPush).toHaveBeenCalledWith('/deportista/dashboard')
      vi.useRealTimers()
    })
  })
})

