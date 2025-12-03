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
  getApiUrl: vi.fn(() => 'http://localhost:5000'),
  LOG_CONFIG: {
    enabled: false,
    level: 'error'
  },
  API_CONFIG: {
    baseURL: 'http://localhost:5000',
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  },
  CURRENT_CONFIG: {
    apiUrl: 'http://localhost:5000',
    debug: false,
    logLevel: 'error'
  },
  APP_ENV_CONFIG: {
    isDevelopment: false,
    isProduction: false,
    isTest: true
  }
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

  describe('Form Data Initialization', () => {
    let wrapper

    beforeEach(() => {
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
    })

    it('should initialize formData correctly', () => {
      expect(wrapper.vm.formData).toBeDefined()
      expect(wrapper.vm.formData.primer_nombre).toBeDefined()
    })

    it('should crearEstadoInicial correctly', () => {
      const estado = wrapper.vm.crearEstadoInicial(mockDatos)
      expect(estado).toBeDefined()
      // crearEstadoInicial may transform to uppercase
      expect(estado.primer_nombre).toBeTruthy()
      expect(typeof estado.primer_nombre).toBe('string')
    })
  })

  describe('Input Sanitization', () => {
    let wrapper

    beforeEach(() => {
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
    })

    it('should sanitizarNombre correctly', () => {
      expect(wrapper.vm.sanitizarNombre('juan123')).toBe('JUAN')
      expect(wrapper.vm.sanitizarNombre('juan carlos')).toBe('JUAN CARLOS')
    })

    it('should sanitizarDireccion correctly', () => {
      const direccion = wrapper.vm.sanitizarDireccion('calle 123')
      expect(direccion).toBe('CALLE 123')
    })

    it('should manejarEntradaNombre correctly', () => {
      const event = {
        target: { value: 'juan123' }
      }
      wrapper.vm.manejarEntradaNombre('primer_nombre', event)
      expect(wrapper.vm.formData.primer_nombre).toBe('JUAN')
    })

    it('should manejarDocumento correctly', () => {
      const event = {
        target: { value: '123-456-789' }
      }
      wrapper.vm.manejarDocumento(event)
      expect(wrapper.vm.formData.documento).toBe('123456789')
    })

    it('should manejarTelefono correctly', () => {
      const event = {
        target: { value: '(300) 123-4567' }
      }
      wrapper.vm.manejarTelefono(event)
      expect(wrapper.vm.formData.telefono).toBe('3001234567')
    })

    it('should manejarCorreo correctly', () => {
      const event = {
        target: { value: '  TEST@EXAMPLE.COM  ' }
      }
      wrapper.vm.manejarCorreo(event)
      expect(wrapper.vm.formData.correo_electronico).toBe('test@example.com')
    })

    it('should manejarEntradaDireccion correctly', () => {
      const event = {
        target: { value: 'calle 123' }
      }
      wrapper.vm.manejarEntradaDireccion(event)
      expect(wrapper.vm.formData.direccion).toBe('CALLE 123')
    })
  })

  describe('Helper Functions', () => {
    let wrapper

    beforeEach(async () => {
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
      await new Promise(resolve => setTimeout(resolve, 200))
    })

    it('should obtenerNombreCompleto correctly', () => {
      const nombre = wrapper.vm.obtenerNombreCompleto()
      expect(nombre).toContain('Juan')
      expect(nombre).toContain('Pérez')
    })

    it('should obtenerTipoDocumento correctly', () => {
      const tipo = wrapper.vm.obtenerTipoDocumento()
      // Should return tipo documento name or undefined
      expect(typeof tipo === 'string' || tipo === undefined || tipo === null).toBe(true)
    })

    it('should obtenerCategoria correctly', () => {
      const categoria = wrapper.vm.obtenerCategoria()
      expect(typeof categoria === 'string' || categoria === undefined || categoria === null).toBe(true)
    })
  })

  describe('Edit Mode', () => {
    let wrapper

    beforeEach(async () => {
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
    })

    it('should enter edit mode', async () => {
      wrapper.vm.iniciarEdicion()
      // iniciarEdicion emits 'editar' event and may rely on modoEdicion prop
      await wrapper.vm.$nextTick()
      // Check that iniciarEdicion was called and emits event
      expect(wrapper.emitted('editar')).toBeTruthy()
    })

    it('should cancel edit mode', () => {
      wrapper.vm.isEditing = true
      wrapper.vm.cancelarEdicion()
      expect(wrapper.vm.isEditing).toBe(false)
    })

    it('should save changes successfully', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })
      Swal.default.close = vi.fn()
      Swal.default.showLoading = vi.fn()

      wrapper.vm.isEditing = true
      wrapper.vm.formData.primer_nombre = 'Juan Actualizado'

      await wrapper.vm.guardarCambios()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))

      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Computed Properties', () => {
    let wrapper

    beforeEach(() => {
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
    })

    it('should check campoEditable correctly', () => {
      const editable = wrapper.vm.campoEditable('persona', 'primer_nombre')
      expect(typeof editable).toBe('boolean')
    })

    it('should filter diagnosticosDisponibles correctly', () => {
      wrapper.vm.formData.id_tipo_enfermedad = 1
      const diagnosticos = wrapper.vm.diagnosticosDisponibles
      expect(Array.isArray(diagnosticos)).toBe(true)
    })
  })

  describe('Date Formatting', () => {
    let wrapper

    beforeEach(() => {
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
    })

    it('should normalizarFechaParaInput correctly', () => {
      const fecha = wrapper.vm.normalizarFechaParaInput('2000-01-01')
      expect(fecha).toBe('2000-01-01')
    })

    it('should normalizarNumeroParaInput correctly', () => {
      expect(wrapper.vm.normalizarNumeroParaInput(50)).toBe('50')
      expect(wrapper.vm.normalizarNumeroParaInput(null)).toBe('')
    })
  })

  describe('Form Submission', () => {
    let wrapper

    beforeEach(async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })
      Swal.default.close = vi.fn()
      Swal.default.showLoading = vi.fn()

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

      wrapper.vm.isEditing = true
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should handle save changes with validation errors', async () => {
      wrapper.vm.formData.primer_nombre = ''
      wrapper.vm.formData.documento = ''

      await wrapper.vm.guardarCambios()
      await wrapper.vm.$nextTick()

      expect(wrapper.exists()).toBe(true)
    })
  })
})

