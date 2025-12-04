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

const mockUseAuthStore = vi.fn()
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockUseAuthStore()
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
  let mockAuthStore

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
      id_sexo: 1,
      id_tipo_sanguineo: 1,
      id_ciudad_recidencia: 1,
      id_eps: 1,
      direccion: 'Calle 123'
    },
    datos_deportista: {
      peso: 60.5,
      altura: 1.75,
      fecha_nacimiento: '2000-01-01',
      id_tipo_sanguineo: 1,
      id_categoria: 1
    },
    informacion_deportiva: {
      id_deporte: 1,
      id_escuela: 1,
      id_institucion_registro: 1,
      id_categoria: 1,
      practica_otro_deporte: false,
      participa_escuela: true,
      recomendacion_medica: false,
      descripcion_recomendacion: ''
    },
    salud: {
      tipos_enfermedad_ids: [1],
      diagnosticos: [{ id_diagnostico: 1 }]
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

    // Mock authStore
    mockAuthStore = {
      user: {
        id_usuario: 1,
        roles: [{ nombre_rol: 'Administrador' }]
      },
      activeRole: 'Administrador'
    }
    mockUseAuthStore.mockReturnValue(mockAuthStore)

    // Mock fetch responses for catalog endpoints
    globalThis.fetch.mockImplementation((url) => {
      let mockData = []
      
      if (url.includes('grupos-sanguineos')) {
        mockData = [{ id_tipo_sangre: 1, tipo_sangre: 'O+', id: 1 }]
      } else if (url.includes('ciudades-residencia')) {
        mockData = [{ id_ciudad: 1, nombre_ciudad: 'Bogotá', id_ciudad_residencia: 1, id: 1 }]
      } else if (url.includes('eps')) {
        mockData = [{ id_eps: 1, nombre_eps: 'SURA', id: 1 }]
      } else if (url.includes('deportes')) {
        mockData = [{ id_deporte: 1, nombre_deporte: 'Fútbol', nombre: 'Fútbol', id: 1 }]
      } else if (url.includes('escuelas')) {
        mockData = [{ id_escuela: 1, nombre_escuela: 'Escuela Test', id: 1 }]
      } else if (url.includes('instituciones-registro')) {
        mockData = [{ id_institucion_registro: 1, nombre_institucion: 'Inst Test', id: 1 }]
      } else if (url.includes('tipos-enfermedad')) {
        mockData = [{ id_tipo_enfermedad: 1, nombre: 'Tipo Test', id: 1 }]
      } else if (url.includes('diagnosticos')) {
        mockData = [{ id_diagnostico: 1, nombre: 'Diagnóstico Test', id_tipo_enfermedad: 1, id: 1 }]
      } else if (url.includes('tipos-documento')) {
        mockData = [{ id_tipo_documento: 1, nombre_documento: 'CC', id: 1 }]
      }

      const mockResponse = {
        ok: true,
        json: async () => ({ success: true, data: mockData }),
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

  describe('Helper Functions - Catalog Lookups', () => {
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

      // Wait for catalogos to load
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 200))
      
      // Set catalogos directly
      wrapper.vm.catalogos.tiposSanguineos = [{ id_tipo_sangre: 1, tipo_sangre: 'O+', id: 1 }]
      wrapper.vm.catalogos.ciudades = [{ id_ciudad: 1, nombre_ciudad: 'Bogotá', id: 1 }]
      wrapper.vm.catalogos.eps = [{ id_eps: 1, nombre_eps: 'SURA', id: 1 }]
      wrapper.vm.catalogos.deportes = [{ id_deporte: 1, nombre_deporte: 'Fútbol', id: 1 }]
      wrapper.vm.catalogos.escuelas = [{ id_escuela: 1, nombre_escuela: 'Escuela Test', id: 1 }]
      wrapper.vm.catalogos.instituciones = [{ id_institucion_registro: 1, nombre_institucion: 'Inst Test', id: 1 }]
      wrapper.vm.catalogos.tiposEnfermedad = [{ id_tipo_enfermedad: 1, nombre: 'Tipo Test', id: 1 }]
      wrapper.vm.catalogos.diagnosticos = [{ id_diagnostico: 1, nombre: 'Diagnóstico Test', id: 1 }]
      wrapper.vm.catalogos.tiposDocumento = [{ id_tipo_documento: 1, nombre_documento: 'CC', id: 1 }]
      wrapper.vm.catalogos.categorias = [{ id_categoria: 1, nombre_categoria: 'Pre-infantil' }]
      wrapper.vm.catalogosCargados = true
    })

    it('should obtenerTipoSanguineo return correct name', () => {
      const tipo = wrapper.vm.obtenerTipoSanguineo()
      expect(tipo).toBe('O+')
    })

    it('should obtenerTipoSanguineo return null when not found', () => {
      wrapper.vm.catalogos.tiposSanguineos = []
      const tipo = wrapper.vm.obtenerTipoSanguineo()
      expect(tipo).toBeNull()
    })

    it('should obtenerCiudad return correct name', () => {
      const ciudad = wrapper.vm.obtenerCiudad()
      expect(ciudad).toBe('Bogotá')
    })

    it('should obtenerCiudad return null when not found', () => {
      wrapper.vm.catalogos.ciudades = []
      const ciudad = wrapper.vm.obtenerCiudad()
      expect(ciudad).toBeNull()
    })

    it('should obtenerEPS return correct name', () => {
      const eps = wrapper.vm.obtenerEPS()
      expect(eps).toBe('SURA')
    })

    it('should obtenerEPS return null when not found', () => {
      wrapper.vm.catalogos.eps = []
      const eps = wrapper.vm.obtenerEPS()
      expect(eps).toBeNull()
    })

    it('should obtenerDeporte return correct name', () => {
      const deporte = wrapper.vm.obtenerDeporte()
      expect(deporte).toBe('Fútbol')
    })

    it('should obtenerDeporte return null when not found', () => {
      wrapper.vm.catalogos.deportes = []
      const deporte = wrapper.vm.obtenerDeporte()
      expect(deporte).toBeNull()
    })

    it('should obtenerEscuela return correct name', () => {
      const escuela = wrapper.vm.obtenerEscuela()
      expect(escuela).toBe('Escuela Test')
    })

    it('should obtenerEscuela return null when not found', () => {
      wrapper.vm.catalogos.escuelas = []
      const escuela = wrapper.vm.obtenerEscuela()
      expect(escuela).toBeNull()
    })

    it('should obtenerInstitucion return correct name', () => {
      const institucion = wrapper.vm.obtenerInstitucion()
      expect(institucion).toBe('Inst Test')
    })

    it('should obtenerInstitucion return null when not found', () => {
      wrapper.vm.catalogos.instituciones = []
      const institucion = wrapper.vm.obtenerInstitucion()
      expect(institucion).toBeNull()
    })

    it('should obtenerTipoEnfermedad return correct name', () => {
      const tipo = wrapper.vm.obtenerTipoEnfermedad(1)
      expect(tipo).toBe('Tipo Test')
    })

    it('should obtenerTipoEnfermedad return null when not found', () => {
      const tipo = wrapper.vm.obtenerTipoEnfermedad(999)
      expect(tipo).toBeNull()
    })

    it('should obtenerTipoEnfermedad return null when catalogos not loaded', () => {
      wrapper.vm.catalogosCargados = false
      const tipo = wrapper.vm.obtenerTipoEnfermedad(1)
      expect(tipo).toBeNull()
    })

    it('should obtenerDiagnostico return correct name', () => {
      const diagnostico = wrapper.vm.obtenerDiagnostico(1)
      expect(diagnostico).toBe('Diagnóstico Test')
    })

    it('should obtenerDiagnostico return null when not found', () => {
      const diagnostico = wrapper.vm.obtenerDiagnostico(999)
      expect(diagnostico).toBeNull()
    })

    it('should obtenerDiagnostico return null when catalogos not loaded', () => {
      wrapper.vm.catalogosCargados = false
      const diagnostico = wrapper.vm.obtenerDiagnostico(1)
      expect(diagnostico).toBeNull()
    })

    it('should obtenerTipoDocumento return correct name', () => {
      const tipo = wrapper.vm.obtenerTipoDocumento()
      expect(tipo).toBe('CC')
    })

    it('should obtenerTipoDocumento return null when not found', () => {
      wrapper.vm.catalogos.tiposDocumento = []
      const tipo = wrapper.vm.obtenerTipoDocumento()
      expect(tipo).toBeNull()
    })
  })

  describe('Validation Functions', () => {
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

    it('should validarNombre not add error when field is not editable', async () => {
      // Use Deportista role which has no permissions
      mockAuthStore.activeRole = 'Deportista'
      // Force update the component to recalculate computed properties
      await wrapper.setProps({ datos: mockDatos })
      await wrapper.vm.$nextTick()
      
      const errores = []
      wrapper.vm.formData.primer_nombre = 'Invalid123'
      wrapper.vm.validarNombre('primer_nombre', 'primer nombre', errores)
      // Should not add error because campo is not editable for Deportista role
      expect(errores).toHaveLength(0)
      // Reset to original role
      mockAuthStore.activeRole = 'Administrador'
    })

    it('should validarNombre not add error when field is empty', () => {
      const errores = []
      wrapper.vm.formData.primer_nombre = ''
      wrapper.vm.validarNombre('primer_nombre', 'primer nombre', errores)
      expect(errores).toHaveLength(0)
    })

    it('should validarNombre add error when field has invalid characters', () => {
      const errores = []
      wrapper.vm.formData.primer_nombre = 'Juan123'
      wrapper.vm.validarNombre('primer_nombre', 'primer nombre', errores)
      expect(errores.length).toBeGreaterThan(0)
    })

    it('should validarCorreo not add error when email is empty', () => {
      const errores = []
      wrapper.vm.formData.correo_electronico = ''
      wrapper.vm.validarCorreo(errores)
      expect(errores).toHaveLength(0)
    })

    it('should validarCorreo add error when email is invalid', () => {
      const errores = []
      wrapper.vm.formData.correo_electronico = 'invalid-email'
      wrapper.vm.validarCorreo(errores)
      expect(errores.length).toBeGreaterThan(0)
    })

    it('should validarTelefono not add error when field is not editable', async () => {
      // Use Deportista role which has no permissions for persona fields
      mockAuthStore.activeRole = 'Deportista'
      await wrapper.setProps({ datos: mockDatos })
      await wrapper.vm.$nextTick()
      
      const errores = []
      wrapper.vm.formData.telefono = '123'
      wrapper.vm.validarTelefono(errores)
      // Should not add error because campo is not editable for Deportista role
      expect(errores).toHaveLength(0)
      // Reset to original role
      mockAuthStore.activeRole = 'Administrador'
    })

    it('should validarTelefono not add error when field is empty', () => {
      const errores = []
      wrapper.vm.formData.telefono = ''
      wrapper.vm.validarTelefono(errores)
      expect(errores).toHaveLength(0)
    })

    it('should validarTelefono add error when phone is too short', () => {
      const errores = []
      wrapper.vm.formData.telefono = '123'
      wrapper.vm.validarTelefono(errores)
      expect(errores.length).toBeGreaterThan(0)
    })

    it('should validarDocumento not add error when field is not editable', async () => {
      // Use Deportista role which has no permissions for persona fields
      mockAuthStore.activeRole = 'Deportista'
      await wrapper.setProps({ datos: mockDatos })
      await wrapper.vm.$nextTick()
      
      const errores = []
      wrapper.vm.formData.documento = '123'
      wrapper.vm.validarDocumento(errores)
      // Should not add error because campo is not editable for Deportista role
      expect(errores).toHaveLength(0)
      // Reset to original role
      mockAuthStore.activeRole = 'Administrador'
    })

    it('should validarDocumento not add error when field is empty', () => {
      const errores = []
      wrapper.vm.formData.documento = ''
      wrapper.vm.validarDocumento(errores)
      expect(errores).toHaveLength(0)
    })

    it('should validarDocumento add error when document is too short', () => {
      const errores = []
      wrapper.vm.formData.documento = '12345'
      wrapper.vm.validarDocumento(errores)
      expect(errores.length).toBeGreaterThan(0)
    })

    it('should validarFormulario collect all validation errors', () => {
      wrapper.vm.formData.primer_nombre = 'Invalid123'
      wrapper.vm.formData.correo_electronico = 'invalid-email'
      wrapper.vm.formData.telefono = '123'
      wrapper.vm.formData.documento = '12345'

      const errores = wrapper.vm.validarFormulario()
      expect(errores.length).toBeGreaterThan(0)
    })

    it('should validarCamposObligatorios return false when required fields are missing', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

      wrapper.vm.formData.primer_nombre = ''
      wrapper.vm.formData.documento = ''

      const result = await wrapper.vm.validarCamposObligatorios()
      expect(result).toBe(false)
    })

    it('should validarRecomendacionMedica return true when not required', async () => {
      wrapper.vm.formData.recomendacion_medica = false
      const result = await wrapper.vm.validarRecomendacionMedica()
      expect(result).toBe(true)
    })

    it('should validarRecomendacionMedica return false when tipo enfermedad is missing', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

      wrapper.vm.formData.recomendacion_medica = true
      wrapper.vm.formData.id_tipo_enfermedad = null

      const result = await wrapper.vm.validarRecomendacionMedica()
      expect(result).toBe(false)
    })

    it('should validarRecomendacionMedica return false when diagnosticos are missing', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

      wrapper.vm.formData.recomendacion_medica = true
      wrapper.vm.formData.id_tipo_enfermedad = 1
      wrapper.vm.formData.diagnosticos = []

      const result = await wrapper.vm.validarRecomendacionMedica()
      expect(result).toBe(false)
    })

    it('should validarEdadMinima return true when fecha_nacimiento is empty', async () => {
      wrapper.vm.formData.fecha_nacimiento = ''
      const result = await wrapper.vm.validarEdadMinima()
      expect(result).toBe(true)
    })

    it('should validarEdadMinima return false when age is less than 5', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

      const today = new Date()
      const year = today.getFullYear() - 3 // 3 years old
      wrapper.vm.formData.fecha_nacimiento = `${year}-01-01`

      const result = await wrapper.vm.validarEdadMinima()
      expect(result).toBe(false)
    })

    it('should calcularEdad return correct age', () => {
      const today = new Date()
      const year = today.getFullYear() - 10
      const fechaNacimiento = `${year}-01-01`
      const edad = wrapper.vm.calcularEdad(fechaNacimiento)
      expect(edad).toBe(10)
    })
  })

  describe('Payload Construction Functions', () => {
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

    it('should construirPayloadPersona return filtered fields', () => {
      wrapper.vm.formData.primer_nombre = 'JUAN'
      wrapper.vm.formData.documento = '12345678'
      wrapper.vm.formData.correo_electronico = 'test@example.com'

      const payload = wrapper.vm.construirPayloadPersona()
      expect(payload).toBeDefined()
      expect(typeof payload).toBe('object')
    })

    it('should construirPayloadDatosDeportista return filtered fields', () => {
      wrapper.vm.formData.peso = '60.5'
      wrapper.vm.formData.altura = '1.75'
      wrapper.vm.formData.id_categoria = '1'

      const payload = wrapper.vm.construirPayloadDatosDeportista()
      expect(payload).toBeDefined()
    })

    it('should construirPayloadInformacionDeportiva return filtered fields', () => {
      wrapper.vm.formData.practica_otro_deporte = true
      wrapper.vm.formData.participa_escuela = true
      wrapper.vm.formData.id_deporte = '1'

      const payload = wrapper.vm.construirPayloadInformacionDeportiva()
      expect(payload).toBeDefined()
    })

    it('should construirPayloadSalud return false when no changes', () => {
      wrapper.vm.formDataInicial = { id_tipo_enfermedad: 1, diagnosticos: [1] }
      wrapper.vm.formData.id_tipo_enfermedad = 1
      wrapper.vm.formData.diagnosticos = [1]

      const payload = wrapper.vm.construirPayloadSalud()
      expect(payload.necesitaActualizacion).toBe(false)
    })

    it('should construirPayloadSalud return true when there are changes', () => {
      wrapper.vm.formDataInicial = { id_tipo_enfermedad: 1, diagnosticos: [1] }
      wrapper.vm.formData.id_tipo_enfermedad = 2
      wrapper.vm.formData.diagnosticos = [2]

      const payload = wrapper.vm.construirPayloadSalud()
      expect(payload.necesitaActualizacion).toBe(true)
    })
  })

  describe('Normalization Functions', () => {
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

    it('should normalizarFechaParaInput handle string YYYY-MM-DD', () => {
      const result = wrapper.vm.normalizarFechaParaInput('2000-01-01')
      expect(result).toBe('2000-01-01')
    })

    it('should normalizarFechaParaInput handle number year', () => {
      const result = wrapper.vm.normalizarFechaParaInput(2000)
      expect(result).toBe('2000-01-01')
    })

    it('should normalizarFechaParaInput handle string year', () => {
      const result = wrapper.vm.normalizarFechaParaInput('2000')
      expect(result).toBe('2000-01-01')
    })

    it('should normalizarFechaParaInput handle Date object', () => {
      const date = new Date('2000-01-01')
      const result = wrapper.vm.normalizarFechaParaInput(date)
      expect(result).toBe('2000-01-01')
    })

    it('should normalizarFechaParaInput return empty string for invalid input', () => {
      const result = wrapper.vm.normalizarFechaParaInput('invalid')
      expect(result).toBe('')
    })

    it('should prepararFechaParaEnvio handle string YYYY-MM-DD', () => {
      const result = wrapper.vm.prepararFechaParaEnvio('2000-01-01')
      expect(result).toBe('2000-01-01')
    })

    it('should prepararFechaParaEnvio return null for empty input', () => {
      const result = wrapper.vm.prepararFechaParaEnvio('')
      expect(result).toBeNull()
    })

    it('should normalizarValorParaComparacion handle null', () => {
      const result = wrapper.vm.normalizarValorParaComparacion(null)
      expect(result).toBe('')
    })

    it('should normalizarValorParaComparacion handle string', () => {
      const result = wrapper.vm.normalizarValorParaComparacion('  test  ')
      expect(result).toBe('test')
    })

    it('should normalizarValorParaComparacion handle array', () => {
      const result = wrapper.vm.normalizarValorParaComparacion([3, 1, 2])
      expect(Array.isArray(result)).toBe(true)
    })

    it('should formatearFechaNacimiento handle number', () => {
      const result = wrapper.vm.formatearFechaNacimiento(2000)
      expect(result).toContain('2000')
    })

    it('should formatearFechaNacimiento handle string', () => {
      const result = wrapper.vm.formatearFechaNacimiento('2000-01-01')
      expect(result).toBeTruthy()
    })

    it('should formatearFechaNacimiento handle Date', () => {
      // Use UTC date to avoid timezone issues
      const date = new Date('2000-01-15T12:00:00Z')
      const result = wrapper.vm.formatearFechaNacimiento(date)
      expect(result).toContain('01')
      expect(result).toContain('2000')
    })

    it('should formatearDateADDMYYYY format correctly', () => {
      // Use UTC date to avoid timezone issues
      const date = new Date('2000-01-15T12:00:00Z')
      const result = wrapper.vm.formatearDateADDMYYYY(date)
      // Result should contain the date parts (may vary by timezone)
      expect(result).toMatch(/\d{2}\/\d{2}\/2000/)
    })
  })

  describe('Utility Functions', () => {
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

    it('should limpiarTexto handle null', () => {
      const result = wrapper.vm.limpiarTexto(null)
      expect(result).toBe('')
    })

    it('should limpiarTexto trim string', () => {
      const result = wrapper.vm.limpiarTexto('  test  ')
      expect(result).toBe('test')
    })

    it('should convertirEntero return number', () => {
      const result = wrapper.vm.convertirEntero('123')
      expect(result).toBe(123)
    })

    it('should convertirEntero return null for invalid input', () => {
      const result = wrapper.vm.convertirEntero('invalid')
      expect(result).toBeNull()
    })

    it('should convertirDecimal handle comma', () => {
      const result = wrapper.vm.convertirDecimal('60,5')
      expect(result).toBe(60.5)
    })

    it('should convertirDecimal return null for invalid input', () => {
      const result = wrapper.vm.convertirDecimal('invalid')
      expect(result).toBeNull()
    })

    it('should limpiarObjeto remove empty values', () => {
      const obj = {
        a: 'value',
        b: '',
        c: null,
        d: undefined
      }
      const result = wrapper.vm.limpiarObjeto(obj)
      expect(result.a).toBe('value')
      expect(result.b).toBeUndefined()
    })

    it('should limpiarObjeto keep booleans when mantenerBooleanos is true', () => {
      const obj = {
        a: true,
        b: false,
        c: ''
      }
      const result = wrapper.vm.limpiarObjeto(obj, { mantenerBooleanos: true })
      expect(result.a).toBe(true)
      expect(result.b).toBe(false)
    })

    it('should filtrarCamposPermitidos return all fields when permisos is *', () => {
      wrapper.vm.permisosRol = { persona: '*' }
      const payload = { a: 'value', b: 'value2' }
      const result = wrapper.vm.filtrarCamposPermitidos(payload, 'persona')
      expect(result.a).toBe('value')
    })

    it('should filtrarCamposPermitidos filter fields based on permisos', async () => {
      // Use Entrenador role which has limited permissions for persona
      mockAuthStore.activeRole = 'Entrenador'
      await wrapper.setProps({ datos: mockDatos })
      await wrapper.vm.$nextTick()
      
      // Entrenador has persona: ['telefono', 'correo_electronico', 'direccion']
      const payload = { telefono: '3001234567', primer_nombre: 'Juan', b: 'value2' }
      const result = wrapper.vm.filtrarCamposPermitidos(payload, 'persona')
      expect(result.telefono).toBe('3001234567')
      // primer_nombre and b should not be in the result since they're not in permisos
      expect(result.primer_nombre).toBeUndefined()
      expect(result.b).toBeUndefined()
      // Reset to original role
      mockAuthStore.activeRole = 'Administrador'
    })
  })

  describe('Watchers', () => {
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
      await new Promise(resolve => setTimeout(resolve, 100))
      
      // Set catalogos
      wrapper.vm.catalogos.tiposEnfermedad = [{ id_tipo_enfermedad: 1, id: 1 }]
      wrapper.vm.catalogos.diagnosticos = [{ id_diagnostico: 1, id_tipo_enfermedad: 1, id: 1 }]
    })

    it('should watch participa_escuela and clear id_escuela when false', async () => {
      wrapper.vm.formData.participa_escuela = true
      wrapper.vm.formData.id_escuela = 1
      await wrapper.vm.$nextTick()

      wrapper.vm.formData.participa_escuela = false
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.formData.id_escuela).toBeNull()
    })

    it('should watch recomendacion_medica and set default tipo_enfermedad when true', async () => {
      wrapper.vm.formData.recomendacion_medica = false
      wrapper.vm.formData.id_tipo_enfermedad = null
      await wrapper.vm.$nextTick()

      wrapper.vm.formData.recomendacion_medica = true
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.formData.id_tipo_enfermedad).toBeDefined()
    })

    it('should watch id_tipo_enfermedad and filter diagnosticos', async () => {
      wrapper.vm.catalogos.diagnosticos = [
        { id_diagnostico: 1, id_tipo_enfermedad: 1, id: 1 },
        { id_diagnostico: 999, id_tipo_enfermedad: 2, id: 999 }
      ]
      wrapper.vm.formData.id_tipo_enfermedad = null
      wrapper.vm.formData.diagnosticos = [1, 999] // 999 should be filtered out
      await wrapper.vm.$nextTick()
      
      // Now set id_tipo_enfermedad to 1, which should trigger the watcher
      wrapper.vm.formData.id_tipo_enfermedad = 1
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 50)) // Give watcher time to run
      
      const diagnosticos = wrapper.vm.formData.diagnosticos
      // 999 should be filtered out because it doesn't match tipo 1
      expect(diagnosticos).not.toContain(999)
    })

    it('should watch id_tipo_enfermedad and clear diagnosticos when null', async () => {
      wrapper.vm.formData.id_tipo_enfermedad = 1
      wrapper.vm.formData.diagnosticos = [1]
      await wrapper.vm.$nextTick()

      wrapper.vm.formData.id_tipo_enfermedad = null
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.formData.diagnosticos).toEqual([])
    })
  })

  describe('Catalog Loading', () => {
    let wrapper

    beforeEach(() => {
      globalThis.fetch.mockClear()
    })

    it('should cargarCatalogos successfully', async () => {
      globalThis.fetch.mockImplementation((url) => {
        return Promise.resolve({
          ok: true,
          json: async () => ({ success: true, data: [] })
        })
      })

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
      await new Promise(resolve => setTimeout(resolve, 500))

      expect(wrapper.vm.catalogosCargados).toBe(true)
    })

    it('should handle catalog loading errors', async () => {
      globalThis.fetch.mockImplementation(() => {
        return Promise.reject(new Error('Network error'))
      })

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
      await new Promise(resolve => setTimeout(resolve, 500))

      // Should still mark as loaded even on error
      expect(wrapper.vm.catalogosCargados).toBe(true)
    })
  })

  describe('Conditional Rendering', () => {
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
      wrapper.vm.catalogosCargados = true
    })

    it('should show edit mode buttons when not editing', async () => {
      await wrapper.setProps({ modoEdicion: false })
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.isEditing).toBe(false)
    })

    it('should show save buttons when editing', async () => {
      await wrapper.setProps({ modoEdicion: true })
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.isEditing).toBe(true)
    })

    it('should render loading message when catalogos not loaded', async () => {
      wrapper.vm.catalogosCargados = false
      await wrapper.vm.$nextTick()
      const html = wrapper.html()
      expect(html).toContain('Cargando cat')
    })

    it('should render loading message when datos not provided', async () => {
      wrapper = mount(PerfilDeportistaVista, {
        props: {
          datos: null
        },
        global: {
          stubs: {
            'i': true
          }
        }
      })
      wrapper.vm.catalogosCargados = true
      await wrapper.vm.$nextTick()
      
      const html = wrapper.html()
      expect(html).toContain('Cargando informaci')
    })
  })

  describe('Save Changes', () => {
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

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      
      wrapper.vm.formDataInicial = {
        primer_nombre: 'JUAN',
        documento: '12345678',
        correo_electronico: 'juan@example.com',
        telefono: '3001234567',
        id_tipo_enfermedad: null,
        diagnosticos: []
      }
    })

    it('should guardarCambios show info message when no changes', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

      // Set formData same as initial
      wrapper.vm.formData.primer_nombre = 'JUAN'
      
      await wrapper.vm.guardarCambios()

      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should guardarCambios save successfully', async () => {
      const deportistasService = await import('@/services/deportistasService')
      const personasService = await import('@/services/personasService')
      
      deportistasService.default.actualizarDeportista = vi.fn().mockResolvedValue({ success: true })
      personasService.default.actualizarPersona = vi.fn().mockResolvedValue({ success: true })

      wrapper.vm.formData.primer_nombre = 'JUAN UPDATED'
      
      await wrapper.vm.guardarCambios()

      expect(deportistasService.default.actualizarDeportista).toHaveBeenCalled()
    })

    it('should guardarCambios handle API errors', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn()
        .mockResolvedValueOnce({ isConfirmed: true }) // Confirmation
        .mockResolvedValueOnce({ isConfirmed: true }) // Error dialog

      const deportistasService = await import('@/services/deportistasService')
      deportistasService.default.actualizarDeportista = vi.fn().mockRejectedValue(new Error('API Error'))

      wrapper.vm.formData.primer_nombre = 'JUAN UPDATED'
      
      await wrapper.vm.guardarCambios()

      expect(Swal.default.fire).toHaveBeenCalled()
    })
  })

  describe('Cancel Edit', () => {
    let wrapper

    beforeEach(async () => {
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

      await wrapper.vm.$nextTick()
    })

    it('should cancelarEdicion without confirmation when no changes', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn()

      // Set up formData and formDataInicial to be the same
      const estadoInicial = wrapper.vm.crearEstadoInicial(mockDatos)
      wrapper.vm.formDataInicial = JSON.parse(JSON.stringify(estadoInicial))
      wrapper.vm.formData = JSON.parse(JSON.stringify(estadoInicial))

      await wrapper.vm.cancelarEdicion()

      // Should not show confirmation when no changes
      expect(Swal.default.fire).not.toHaveBeenCalled()
    })

    it('should cancelarEdicion with confirmation when there are changes', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

      wrapper.vm.formDataInicial = { primer_nombre: 'JUAN' }
      wrapper.vm.formData.primer_nombre = 'JUAN UPDATED'

      await wrapper.vm.cancelarEdicion()

      expect(Swal.default.fire).toHaveBeenCalled()
    })

    it('should cancelarEdicion not cancel when user declines', async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: false })

      wrapper.vm.formDataInicial = { primer_nombre: 'JUAN' }
      wrapper.vm.formData.primer_nombre = 'JUAN UPDATED'

      await wrapper.vm.cancelarEdicion()

      expect(Swal.default.fire).toHaveBeenCalled()
    })
  })

  describe('Verify Changes', () => {
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

    it('should verificarCambios return false when no initial state', () => {
      wrapper.vm.formDataInicial = null
      const result = wrapper.vm.verificarCambios()
      expect(result).toBe(false)
    })

    it('should verificarCambios return false when no changes', () => {
      // Create initial state with all fields
      const estadoInicial = {
        primer_nombre: 'JUAN',
        segundo_nombre: '',
        primer_apellido: 'PEREZ',
        segundo_apellido: '',
        documento: '12345678',
        correo_electronico: 'test@example.com',
        telefono: '3001234567',
        direccion: '',
        fecha_nacimiento: '',
        peso: '',
        altura: '',
        practica_otro_deporte: false,
        participa_escuela: false,
        recomendacion_medica: false,
        descripcion_recomendacion: '',
        id_tipo_sanguineo: null,
        id_ciudad_recidencia: null,
        id_eps: null,
        id_deporte: null,
        id_escuela: null,
        id_institucion_registro: null,
        id_categoria: null,
        id_tipo_enfermedad: null,
        diagnosticos: []
      }
      
      wrapper.vm.formDataInicial = estadoInicial
      wrapper.vm.formData = JSON.parse(JSON.stringify(estadoInicial))
      
      const result = wrapper.vm.verificarCambios()
      expect(result).toBe(false)
    })

    it('should verificarCambios return true when there are changes', () => {
      wrapper.vm.formDataInicial = { primer_nombre: 'JUAN' }
      wrapper.vm.formData.primer_nombre = 'JUAN UPDATED'
      const result = wrapper.vm.verificarCambios()
      expect(result).toBe(true)
    })

    it('should verificarCambios detect changes in diagnosticos array', () => {
      wrapper.vm.formDataInicial = { diagnosticos: [1] }
      wrapper.vm.formData.diagnosticos = [1, 2]
      const result = wrapper.vm.verificarCambios()
      expect(result).toBe(true)
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

    it('should rolesUsuario return array of role names', () => {
      const roles = wrapper.vm.rolesUsuario
      expect(Array.isArray(roles)).toBe(true)
    })

    it('should rolActivo return active role', () => {
      mockAuthStore.activeRole = 'Entrenador'
      const rol = wrapper.vm.rolActivo
      expect(rol).toBe('Entrenador')
    })

    it('should rolActivo fallback to first role', () => {
      mockAuthStore.activeRole = null
      mockAuthStore.user.roles = [{ nombre_rol: 'Entrenador' }]
      const rol = wrapper.vm.rolActivo
      expect(rol).toBeTruthy()
    })

    it('should puedeEditarMedidas return true for Administrador', () => {
      mockAuthStore.activeRole = 'Administrador'
      const puede = wrapper.vm.puedeEditarMedidas
      expect(puede).toBe(true)
    })

    it('should puedeEditarMedidas return false for Deportista', () => {
      mockAuthStore.activeRole = 'Deportista'
      const puede = wrapper.vm.puedeEditarMedidas
      expect(puede).toBe(false)
    })

    it('should diagnosticosDisponibles return all when no tipo selected', () => {
      wrapper.vm.catalogos.diagnosticos = [
        { id_diagnostico: 1, id_tipo_enfermedad: 1 },
        { id_diagnostico: 2, id_tipo_enfermedad: 2 }
      ]
      wrapper.vm.formData.id_tipo_enfermedad = null
      
      const diagnosticos = wrapper.vm.diagnosticosDisponibles
      expect(diagnosticos.length).toBe(2)
    })

    it('should diagnosticosDisponibles filter by tipo', () => {
      wrapper.vm.catalogos.diagnosticos = [
        { id_diagnostico: 1, id_tipo_enfermedad: 1 },
        { id_diagnostico: 2, id_tipo_enfermedad: 2 }
      ]
      wrapper.vm.formData.id_tipo_enfermedad = 1
      
      const diagnosticos = wrapper.vm.diagnosticosDisponibles
      expect(diagnosticos.length).toBe(1)
      expect(diagnosticos[0].id_diagnostico).toBe(1)
    })
  })

  describe('obtenerNombreCompleto Edge Cases', () => {
    let wrapper

    it('should obtenerNombreCompleto use nombre_completo from persona', async () => {
      wrapper = mount(PerfilDeportistaVista, {
        props: {
          datos: {
            persona: {
              nombre_completo: 'Juan Carlos Pérez García'
            }
          }
        },
        global: {
          stubs: {
            'i': true
          }
        }
      })
      await wrapper.vm.$nextTick()
      const nombre = wrapper.vm.obtenerNombreCompleto()
      expect(nombre).toBe('Juan Carlos Pérez García')
    })

    it('should obtenerNombreCompleto construct from persona parts', async () => {
      wrapper = mount(PerfilDeportistaVista, {
        props: {
          datos: {
            persona: {
              primer_nombre: 'Juan',
              segundo_nombre: 'Carlos',
              primer_apellido: 'Pérez',
              segundo_apellido: 'García'
            }
          }
        },
        global: {
          stubs: {
            'i': true
          }
        }
      })
      await wrapper.vm.$nextTick()
      const nombre = wrapper.vm.obtenerNombreCompleto()
      expect(nombre).toContain('Juan')
      expect(nombre).toContain('Pérez')
    })

    it('should obtenerNombreCompleto use nombre from datos', async () => {
      wrapper = mount(PerfilDeportistaVista, {
        props: {
          datos: {
            nombre: 'Juan Pérez'
          }
        },
        global: {
          stubs: {
            'i': true
          }
        }
      })
      await wrapper.vm.$nextTick()
      const nombre = wrapper.vm.obtenerNombreCompleto()
      expect(nombre).toBe('Juan Pérez')
    })

    it('should obtenerNombreCompleto construct from datos nombre1/apellido1', async () => {
      wrapper = mount(PerfilDeportistaVista, {
        props: {
          datos: {
            nombre1: 'Juan',
            nombre2: 'Carlos',
            apellido1: 'Pérez',
            apellido2: 'García'
          }
        },
        global: {
          stubs: {
            'i': true
          }
        }
      })
      await wrapper.vm.$nextTick()
      const nombre = wrapper.vm.obtenerNombreCompleto()
      expect(nombre).toContain('Juan')
      expect(nombre).toContain('Pérez')
      // Should construct full name
      expect(nombre).toBe('Juan Carlos Pérez García')
    })

    it('should obtenerNombreCompleto return null when no data', async () => {
      wrapper = mount(PerfilDeportistaVista, {
        props: {
          datos: null
        },
        global: {
          stubs: {
            'i': true
          }
        }
      })
      await wrapper.vm.$nextTick()
      const nombre = wrapper.vm.obtenerNombreCompleto()
      expect(nombre).toBeNull()
    })

    it('should obtenerNombreCompleto return null when datos has no relevant fields', async () => {
      wrapper = mount(PerfilDeportistaVista, {
        props: {
          datos: {}
        },
        global: {
          stubs: {
            'i': true
          }
        }
      })
      await wrapper.vm.$nextTick()
      const nombre = wrapper.vm.obtenerNombreCompleto()
      expect(nombre).toBeNull()
    })
  })

  describe('Input Handlers Edge Cases', () => {
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

    it('should manejarEntradaNombre handle null event', () => {
      wrapper.vm.manejarEntradaNombre('primer_nombre', null)
      expect(wrapper.vm.formData.primer_nombre).toBeDefined()
    })

    it('should manejarEntradaNombre handle null event.target', () => {
      wrapper.vm.manejarEntradaNombre('primer_nombre', { target: null })
      expect(wrapper.vm.formData.primer_nombre).toBeDefined()
    })

    it('should manejarDocumento handle null event', () => {
      wrapper.vm.manejarDocumento(null)
      expect(wrapper.vm.formData.documento).toBeDefined()
    })

    it('should manejarTelefono handle null event', () => {
      wrapper.vm.manejarTelefono(null)
      expect(wrapper.vm.formData.telefono).toBeDefined()
    })

    it('should manejarCorreo handle null event', () => {
      wrapper.vm.manejarCorreo(null)
      expect(wrapper.vm.formData.correo_electronico).toBeDefined()
    })

    it('should manejarEntradaDireccion handle null event', () => {
      wrapper.vm.manejarEntradaDireccion(null)
      expect(wrapper.vm.formData.direccion).toBeDefined()
    })
  })

  describe('validarIdentificadores', () => {
    let wrapper

    beforeEach(async () => {
      const Swal = await import('sweetalert2')
      Swal.default.fire = vi.fn().mockResolvedValue({ isConfirmed: true })

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

    it('should validarIdentificadores return true when both IDs exist', async () => {
      const result = await wrapper.vm.validarIdentificadores()
      expect(result).toBe(true)
    })

    it('should validarIdentificadores return false when idPersona is missing', async () => {
      await wrapper.setProps({
        datos: {
          ...mockDatos,
          persona: null
        }
      })
      await wrapper.vm.$nextTick()

      const result = await wrapper.vm.validarIdentificadores()
      expect(result).toBe(false)
    })

    it('should validarIdentificadores return false when idDeportista is missing', async () => {
      await wrapper.setProps({
        datos: {
          ...mockDatos,
          id_deportista: null
        }
      })
      await wrapper.vm.$nextTick()

      const result = await wrapper.vm.validarIdentificadores()
      expect(result).toBe(false)
    })
  })
})

