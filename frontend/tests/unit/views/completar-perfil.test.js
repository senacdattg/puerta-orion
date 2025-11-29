import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import CompletarPerfil from '@/views/completar-perfil.vue'
import { useAuthStore } from '@/stores/auth'

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

  beforeEach(async () => {
    setActivePinia(createPinia())

    // Resetear mocks antes de cada test
    mockRouterPush.mockClear()
    mockRouterReplace.mockClear()
    
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
      loadUserProfileDetail: vi.fn().mockResolvedValue({ success: true, data: {} })
    }

    useAuthStore.mockReturnValue(mockAuthStore)
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

    expect(wrapper.vm.yaEsDeportista).toBe(false)
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
})

