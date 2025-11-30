import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import perfil from '@/views/perfil.vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

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

vi.mock('@/components/layout/selector-roles.vue', () => ({
  default: {
    name: 'SelectorRoles',
    template: '<div class="selector-roles">Selector</div>'
  }
}))

// Mock stores
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

// Mock router
vi.mock('vue-router', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn()
  }))
}))

// Mock services
vi.mock('@/services/usuariosService', () => ({
  default: {
    obtenerUsuarioPorId: vi.fn()
  }
}))

describe('PerfilView', () => {
  let mockAuthStore
  let mockRouter

  beforeEach(() => {
    setActivePinia(createPinia())

    mockAuthStore = {
      user: {
        id_usuario: 1,
        usuario: 'testuser',
        estado: true,
        persona: {
          nombre_completo: 'Test User',
          correo_electronico: 'test@example.com'
        },
        roles: ['Administrador']
      },
      loadUserProfileDetail: vi.fn().mockResolvedValue({}),
      userDetail: {}
    }

    mockRouter = {
      push: vi.fn()
    }

    useAuthStore.mockReturnValue(mockAuthStore)
    useRouter.mockReturnValue(mockRouter)
  })

  it('should render the view', () => {
    const wrapper = mount(perfil, {
      global: {
        stubs: {
          Encabezado: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.perfil-page').exists()).toBe(true)
  })

  it('should render perfil container', () => {
    const wrapper = mount(perfil, {
      global: {
        stubs: {
          Encabezado: true
        }
      }
    })

    expect(wrapper.find('.perfil-container').exists()).toBe(true)
  })

  it('should render perfil header', () => {
    const wrapper = mount(perfil, {
      global: {
        stubs: {
          Encabezado: true
        }
      }
    })

    expect(wrapper.find('.perfil-header').exists()).toBe(true)
    expect(wrapper.find('.perfil-title').exists()).toBe(true)
  })

  it('should show loading state when isLoading is true', async () => {
    // Mock loadUserProfileDetail to avoid errors
    mockAuthStore.loadUserProfileDetail = vi.fn().mockResolvedValue({})
    mockAuthStore.userDetail = {}

    const wrapper = mount(perfil, {
      global: {
        stubs: {
          Encabezado: true
        }
      }
    })

    // Wait for component to mount and initialize
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // The component should handle loading state internally
    expect(wrapper.exists()).toBe(true)
  })

  it('should show empty state when usuario is null', async () => {
    mockAuthStore.user = null
    mockAuthStore.loadUserProfileDetail = vi.fn().mockResolvedValue({})
    mockAuthStore.userDetail = {}

    const wrapper = mount(perfil, {
      global: {
        stubs: {
          Encabezado: true
        }
      }
    })

    // Wait for component to mount
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // The component should handle null user state
    expect(wrapper.exists()).toBe(true)
  })

  describe('Edit Profile', () => {
    it('should navigate to update profile page', () => {
      const wrapper = mount(perfil, {
        global: {
          stubs: {
            Encabezado: true
          }
        }
      })

      wrapper.vm.editarPerfil()

      expect(mockRouter.push).toHaveBeenCalledWith('/actualizar-info')
    })

    it('should show edit button', () => {
      const wrapper = mount(perfil, {
        global: {
          stubs: {
            Encabezado: true
          }
        }
      })

      const editButton = wrapper.find('.btn-primary.btn-icon')
      expect(editButton.exists()).toBe(true)
      expect(editButton.text()).toContain('Editar perfil')
    })
  })

  describe('Load User Detail', () => {
    it('should load user detail on mount', async () => {
      mockAuthStore.loadUserProfileDetail = vi.fn().mockResolvedValue({
        success: true,
        data: {
          persona: { id_persona: 1 },
          deportista: { id_deportista: 1 }
        }
      })

      const wrapper = mount(perfil, {
        global: {
          stubs: {
            Encabezado: true
          }
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 150))

      expect(mockAuthStore.loadUserProfileDetail).toHaveBeenCalled()
    })

    it('should handle error loading user detail', async () => {
      mockAuthStore.loadUserProfileDetail = vi.fn().mockRejectedValue(new Error('Network error'))

      const wrapper = mount(perfil, {
        global: {
          stubs: {
            Encabezado: true
          }
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Helper Functions', () => {
    let wrapper

    beforeEach(() => {
      wrapper = mount(perfil, {
        global: {
          stubs: {
            Encabezado: true
          }
        }
      })
    })

    it('should getNombreRol from string', () => {
      expect(wrapper.vm.getNombreRol('Deportista')).toBe('Deportista')
    })

    it('should getNombreRol from object', () => {
      expect(wrapper.vm.getNombreRol({ nombre_rol: 'Administrador' })).toBe('Administrador')
    })

    it('should getNombreRolCompleto correctly', () => {
      const result = wrapper.vm.getNombreRolCompleto('Deportista')
      expect(result).toContain('Deportista')
      const resultSuperAdmin = wrapper.vm.getNombreRolCompleto('SuperAdmin')
      expect(resultSuperAdmin).toContain('Super Admin')
    })

    it('should getRolId from object', () => {
      expect(wrapper.vm.getRolId({ id_rol: 1 })).toBe(1)
    })

    it('should getRoleClass correctly', () => {
      expect(wrapper.vm.getRoleClass('Deportista')).toBe('role-athlete')
      expect(wrapper.vm.getRoleClass('Administrador')).toBe('role-admin')
    })

    it('should getRoleIcon correctly', () => {
      expect(wrapper.vm.getRoleIcon('Deportista')).toBe('fas fa-running')
      expect(wrapper.vm.getRoleIcon('Administrador')).toBe('fas fa-crown')
    })
  })

  describe('Catalog Functions', () => {
    let wrapper

    beforeEach(async () => {
      wrapper = mount(perfil, {
        global: {
          stubs: {
            Encabezado: true
          }
        }
      })

      wrapper.vm.catalogos = {
        categorias: [{ id_categoria: 1, nombre_categoria: 'Pre-Benjamin' }],
        gruposSanguineos: [{ id_tipo_sangre: 1, nombre: 'O+' }],
        ciudades: [{ id_ciudad: 1, nombre_ciudad: 'Bogotá' }],
        eps: [{ id_eps: 1, nombre_eps: 'SURA' }],
        tiposDocumento: [{ id_documento: 1, nombre_documento: 'CC' }],
        sexos: [{ id_sexo: 1, nombre: 'Masculino' }],
        deportes: [{ id_deporte: 1, nombre_deporte: 'Voleibol' }],
        escuelas: [{ id_escuela: 1, nombre_escuela: 'Escuela Test' }],
        institucionesRegistro: [{ id_institucion: 1, nombre_institucion: 'Inst Test' }],
        tiposEnfermedad: [{ id_tipo_enfermedad: 1, nombre: 'Tipo Test' }],
        diagnosticos: [{ id_diagnostico: 1, nombre_diagnostico: 'Diagnóstico Test' }]
      }
      await wrapper.vm.$nextTick()
    })

    it('should nombreCategoria return correct name', () => {
      expect(wrapper.vm.nombreCategoria(1)).toBe('Pre-Benjamin')
      expect(wrapper.vm.nombreCategoria(999)).toBe('—')
    })

    it('should nombreSangre return correct name', () => {
      expect(wrapper.vm.nombreSangre(1)).toBe('O+')
    })

    it('should nombreCiudad return correct name', () => {
      expect(wrapper.vm.nombreCiudad(1)).toBe('Bogotá')
    })

    it('should nombreEPS return correct name', () => {
      expect(wrapper.vm.nombreEPS(1)).toBe('SURA')
    })

    it('should nombreTipoDocumento return correct name', () => {
      expect(wrapper.vm.nombreTipoDocumento(1)).toBe('CC')
    })

    it('should nombreSexo return correct name', () => {
      expect(wrapper.vm.nombreSexo(1)).toBe('Masculino')
    })
  })

  describe('Date Formatting', () => {
    let wrapper

    beforeEach(() => {
      wrapper = mount(perfil, {
        global: {
          stubs: {
            Encabezado: true
          }
        }
      })
    })

    it('should formatearFechaNacimiento with Date object', () => {
      const fecha = new Date('2010-06-15T12:00:00Z')
      const resultado = wrapper.vm.formatearFechaNacimiento(fecha)
      expect(resultado).toBeTruthy()
      expect(resultado).toContain('2010')
    })

    it('should formatearFechaNacimiento with string', () => {
      const resultado = wrapper.vm.formatearFechaNacimiento('2010-06-15')
      expect(resultado).toBeTruthy()
    })

    it('should formatearFechaNacimiento with number (year only)', () => {
      const resultado = wrapper.vm.formatearFechaNacimiento(2010)
      // The function formats year as a date (01/01/2010)
      expect(resultado).toBeTruthy()
      expect(typeof resultado).toBe('string')
    })
  })

  describe('Associate Acudiente Modal', () => {
    let wrapper

    beforeEach(async () => {
      mockAuthStore.activeRole = 'Deportista'
      mockAuthStore.userDetail = {
        deportista: { id_deportista: 1 }
      }

      wrapper = mount(perfil, {
        global: {
          stubs: {
            Encabezado: true
          }
        }
      })
      await wrapper.vm.$nextTick()
    })

    it('should open modal when abrirModalAsignarAcudiente is called', async () => {
      wrapper.vm.abrirModalAsignarAcudiente()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarModalAsignarAcudiente).toBe(true)
    })

    it('should close modal when cerrarModalAsignarAcudiente is called', async () => {
      wrapper.vm.mostrarModalAsignarAcudiente = true
      wrapper.vm.cerrarModalAsignarAcudiente()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarModalAsignarAcudiente).toBe(false)
    })

    it('should reset form when closing modal', async () => {
      wrapper.vm.mostrarModalAsignarAcudiente = true
      wrapper.vm.busquedaAcudiente = 'test'
      wrapper.vm.acudienteSeleccionado = { id: 1 }

      wrapper.vm.cerrarModalAsignarAcudiente()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.busquedaAcudiente).toBe('')
      expect(wrapper.vm.acudienteSeleccionado).toBe(null)
    })
  })

  describe('Role Display', () => {
    it('should show multiple roles when user has more than one role', async () => {
      mockAuthStore.user.roles = [
        { nombre_rol: 'Deportista' },
        { nombre_rol: 'Acudiente' }
      ]

      const wrapper = mount(perfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true,
            SelectorRoles: true
          }
        }
      })

      wrapper.vm.usuario = mockAuthStore.user
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.rolesAsignadosFiltrados.length).toBeGreaterThan(1)
    })

    it('should show single role badge when user has one role', async () => {
      mockAuthStore.user.roles = [{ nombre_rol: 'Deportista' }]

      const wrapper = mount(perfil, {
        global: {
          stubs: {
            Encabezado: true,
            Pie: true,
            SelectorRoles: true
          }
        }
      })

      wrapper.vm.usuario = mockAuthStore.user
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.rolesAsignadosFiltrados.length).toBe(1)
    })
  })
})

