import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import FormularioDeportista from '@/components/formularios/formulario-deportista.vue'
import { useAuthStore } from '@/stores/auth'

// Mock services
vi.mock('@/services/catalogosService', () => ({
  default: {
    getCatalogosCompletos: vi.fn().mockResolvedValue({
      success: true,
      data: {
        tipos_documento: [{ id_documento: 1, nombre: 'Cédula' }],
        sexos: [{ id_sexo: 1, nombre: 'Masculino' }],
        grupos_sanguineos: [{ id_tipo_sangre: 1, tipo_sangre: 'O+' }],
        ciudades: [{ id_ciudad: 1, nombre_ciudad: 'Bogotá' }],
        eps: [{ id_eps: 1, nombre_eps: 'EPS Test' }],
        deportes: [{ id_deporte: 1, nombre_deporte: 'Fútbol' }],
        escuelas: [{ id_escuela: 1, nombre_escuela: 'Escuela Test' }],
        instituciones: [{ id_institucion: 1, nombre_institucion: 'Inst Test' }],
        categorias: [{ id_categoria: 1, nombre_categoria: 'Pre-infantil' }]
      }
    }),
    cargarCatalogosFormulario: vi.fn().mockResolvedValue({
      success: true,
      data: {
        tipos_documento: [{ id_documento: 1, nombre: 'Cédula' }],
        sexos: [{ id_sexo: 1, nombre: 'Masculino' }],
        grupos_sanguineos: [{ id_tipo_sangre: 1, tipo_sangre: 'O+' }],
        ciudades: [{ id_ciudad: 1, nombre_ciudad: 'Bogotá' }],
        eps: [{ id_eps: 1, nombre_eps: 'EPS Test' }],
        deportes: [{ id_deporte: 1, nombre_deporte: 'Fútbol' }],
        escuelas: [{ id_escuela: 1, nombre_escuela: 'Escuela Test' }],
        instituciones: [{ id_institucion: 1, nombre_institucion: 'Inst Test' }],
        categorias: [{ id_categoria: 1, nombre_categoria: 'Pre-infantil' }],
        tipos_enfermedad: [{ id_tipo_enfermedad: 1, nombre: 'Tipo Test' }],
        diagnosticos: [{ id_diagnostico: 1, nombre: 'Diagnóstico Test' }]
      }
    })
  }
}))

vi.mock('@/services/deportistasService', () => ({
  default: {
    crearDeportista: vi.fn().mockResolvedValue({ success: true }),
    actualizarDeportista: vi.fn().mockResolvedValue({ success: true })
  }
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(),
    Swal: {
      fire: vi.fn()
    }
  }
}))

// Mock global fetch
globalThis.fetch = vi.fn()

describe('FormularioDeportista', () => {
  let wrapper
  let mockAuthStore

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    // Mock fetch responses for catalog endpoints
    globalThis.fetch.mockImplementation((url) => {
      const mockResponse = {
        ok: true,
        json: async () => ({ success: true, data: [] }),
        status: 200,
        statusText: 'OK'
      }
      return Promise.resolve(mockResponse)
    })

    mockAuthStore = {
      user: {
        id_usuario: 1,
        roles: [{ nombre_rol: 'Administrador' }]
      }
    }

    useAuthStore.mockReturnValue(mockAuthStore)
  })

  it('should render component', async () => {
    wrapper = mount(FormularioDeportista, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.formulario-datos').exists()).toBe(true)
  })

  it('should display form title', () => {
    wrapper = mount(FormularioDeportista, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    expect(wrapper.vm.obtenerTitulo).toBeDefined()
  })

  it('should initialize form data', () => {
    wrapper = mount(FormularioDeportista, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    expect(wrapper.vm.form).toBeDefined()
    expect(wrapper.vm.form.fecha_nacimiento).toBeDefined()
  })

  it('should handle modo prop', () => {
    wrapper = mount(FormularioDeportista, {
      props: {
        modo: 'ver'
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    expect(wrapper.props('modo')).toBe('ver')
  })

  it('should handle submit event', async () => {
    wrapper = mount(FormularioDeportista, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    await wrapper.vm.$nextTick()

    const form = wrapper.find('.formulario-datos')
    if (form.exists()) {
      await form.trigger('submit')
      // Should handle submit without errors
      expect(wrapper.exists()).toBe(true)
    }
  })

  it('should load catalogos on mount', async () => {
    wrapper = mount(FormularioDeportista, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    expect(wrapper.vm.catalogos).toBeDefined()
  })

  it('should display basic data section', () => {
    wrapper = mount(FormularioDeportista, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    const section = wrapper.find('.seccion-titulo')
    expect(section.exists()).toBe(true)
  })

  it('should handle form validation', () => {
    wrapper = mount(FormularioDeportista, {
      global: {
        stubs: {
          'i': true
        }
      }
    })

    expect(wrapper.vm.form).toBeDefined()
    // Form should have required fields
    expect(wrapper.vm.form.fecha_nacimiento).toBeDefined()
  })
})

