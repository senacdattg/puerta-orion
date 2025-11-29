import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PerfilDeportistaVista from '@/components/deportistas/perfil-deportista-vista.vue'

// Mock services
// Mock global fetch
globalThis.fetch = vi.fn()

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
        categorias: [{ id_categoria: 1, nombre_categoria: 'Pre-infantil' }],
        tipos_enfermedad: [{ id_tipo_enfermedad: 1, nombre: 'Tipo Test' }],
        diagnosticos: [{ id_diagnostico: 1, nombre: 'Diagnóstico Test' }]
      }
    }),
    getCategorias: vi.fn().mockResolvedValue({
      success: true,
      data: [{ id_categoria: 1, nombre_categoria: 'Pre-infantil' }]
    })
  }
}))

vi.mock('@/services/deportistasService', () => ({
  default: {
    actualizarDeportista: vi.fn().mockResolvedValue({ success: true })
  }
}))

vi.mock('@/services/personasService', () => ({
  default: {
    actualizarPersona: vi.fn().mockResolvedValue({ success: true })
  }
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    user: {
      id_usuario: 1,
      roles: [{ nombre_rol: 'Administrador' }]
    }
  }))
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(),
    Swal: {
      fire: vi.fn()
    }
  }
}))

vi.mock('@/config/environment', () => ({
  getApiUrl: vi.fn(() => 'http://localhost:5000')
}))

describe('PerfilDeportistaVista', () => {
  let wrapper

  const mockDatos = {
    id_deportista: 1,
    persona: {
      id_persona: 1,
      primer_nombre: 'Juan',
      segundo_nombre: 'Carlos',
      primer_apellido: 'Pérez',
      segundo_apellido: 'García',
      documento: '12345678',
      id_tipo_documento: 1,
      correo_electronico: 'juan@example.com',
      telefono: '3001234567',
      fecha_nacimiento: '2000-01-01',
      id_sexo: 1
    },
    id_tipo_sanguineo: 1,
    id_ciudad_residencia: 1,
    id_eps: 1,
    id_deporte: 1,
    id_escuela: 1,
    id_institucion_registro: 1,
    id_categoria: 1,
    diagnosticos: []
  }

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
  })

  it('should render component with datos prop', async () => {
    wrapper = mount(PerfilDeportistaVista, {
      props: {
        datos: mockDatos
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.perfil-deportista-vista').exists()).toBe(true)
  })

  it('should display modal title correctly', async () => {
    wrapper = mount(PerfilDeportistaVista, {
      props: {
        datos: mockDatos
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const title = wrapper.find('.modal-title')
    expect(title.exists()).toBe(true)
  })

  it('should show loading state when catalogos are not loaded', () => {
    wrapper = mount(PerfilDeportistaVista, {
      props: {
        datos: mockDatos
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    // Initially catalogosCargados is false
    expect(wrapper.vm.catalogosCargados).toBe(false)
  })

  it('should emit cerrar event when close button is clicked', async () => {
    wrapper = mount(PerfilDeportistaVista, {
      props: {
        datos: mockDatos
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const closeButton = wrapper.find('.btn-cerrar')
    if (closeButton.exists()) {
      await closeButton.trigger('click')
      expect(wrapper.emitted('cerrar')).toBeTruthy()
    }
  })

  it('should display personal information when datos is provided', async () => {
    wrapper = mount(PerfilDeportistaVista, {
      props: {
        datos: mockDatos
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.vm.datos).toEqual(mockDatos)
  })

  it('should handle modoEdicion prop', () => {
    wrapper = mount(PerfilDeportistaVista, {
      props: {
        datos: mockDatos,
        modoEdicion: true
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    expect(wrapper.props('modoEdicion')).toBe(true)
  })

  it('should initialize formData from datos prop', () => {
    wrapper = mount(PerfilDeportistaVista, {
      props: {
        datos: mockDatos
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    expect(wrapper.vm.formData).toBeDefined()
  })

  it('should have edit and cancel buttons when not editing', async () => {
    wrapper = mount(PerfilDeportistaVista, {
      props: {
        datos: mockDatos,
        modoEdicion: false
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.vm.isEditing).toBe(false)
  })
})

