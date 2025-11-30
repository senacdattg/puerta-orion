import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PanelAdminComponente from '@/components/admin/panel-admin-componente.vue'
import Swal from 'sweetalert2'

// Mock components
vi.mock('@/components/admin/modal-registro-usuario.vue', () => ({
  default: {
    name: 'ModalRegistroUsuario',
    template: '<div class="modal-registro-usuario">Modal Registro</div>',
    props: ['mostrar'],
    emits: ['cerrar', 'usuario-registrado']
  }
}))

vi.mock('@/components/admin/modal-anadir-datos.vue', () => ({
  default: {
    name: 'ModalAnadirDatos',
    template: '<div class="modal-anadir-datos">Modal Añadir</div>',
    props: ['mostrar', 'tema-inicial'],
    emits: ['cerrar', 'guardar-dato']
  }
}))

vi.mock('@/components/admin/modal-editar-dato.vue', () => ({
  default: {
    name: 'ModalEditarDato',
    template: '<div class="modal-editar-dato">Modal Editar</div>',
    props: ['mostrar', 'tema', 'dato'],
    emits: ['cerrar', 'guardado']
  }
}))

vi.mock('@/components/admin/tabla-usuarios.vue', () => ({
  default: {
    name: 'TablaUsuarios',
    template: '<div class="tabla-usuarios">Tabla Usuarios</div>',
    props: ['search-term', 'role-filter'],
    emits: ['usuarios-cargados', 'usuario-actualizado']
  }
}))

vi.mock('@/components/admin/tabla-datos-dinamicos.vue', () => ({
  default: {
    name: 'TablaDatosDinamicos',
    template: '<div class="tabla-datos-dinamicos">Tabla Datos</div>',
    props: ['recargar'],
    emits: ['editar-dato', 'crear-nuevo', 'dato-eliminado']
  }
}))

vi.mock('@/services/usuariosService', () => ({
  default: {
    listarRoles: vi.fn()
  }
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(),
    close: vi.fn(),
    showLoading: vi.fn()
  }
}))

vi.mock('@/config/environment', () => ({
  API_CONFIG: {
    baseURL: 'http://localhost:5000'
  }
}))

// Mock fetch and localStorage
globalThis.fetch = vi.fn()
globalThis.localStorage = {
  getItem: vi.fn(() => 'test-token'),
  setItem: vi.fn(),
  removeItem: vi.fn()
}

describe('PanelAdminComponente', () => {
  let wrapper
  let mockUsuariosService

  beforeEach(async () => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    mockUsuariosService = await import('@/services/usuariosService')
    mockUsuariosService.default.listarRoles.mockResolvedValue({
      success: true,
      data: [
        { nombre_rol: 'Administrador' },
        { nombre_rol: 'Deportista' }
      ]
    })

    globalThis.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({ success: true, data: {} }),
      status: 200
    })
  })

  const createWrapper = () => {
    return mount(PanelAdminComponente, {
      global: {
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
      expect(wrapper.find('.admin-page').exists()).toBe(true)
    })

    it('should display page title', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Panel de Administración')
    })

    it('should display stats section', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.stats-section').exists()).toBe(true)
    })
  })

  describe('Modal management', () => {
    it('should open registro modal', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.abrirModalRegistro()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarModalRegistro).toBe(true)
    })

    it('should close registro modal', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarModalRegistro = true
      wrapper.vm.cerrarModalRegistro()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarModalRegistro).toBe(false)
    })

    it('should open datos modal', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.abrirModalDatos()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarModalDatos).toBe(true)
    })

    it('should open edicion modal with tema and dato', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const tema = 'eps'
      const dato = { id: 1, nombre: 'Test' }
      wrapper.vm.abrirModalEdicion({ tema, dato })
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarModalEdicion).toBe(true)
      expect(wrapper.vm.temaEdicion).toBe(tema)
      expect(wrapper.vm.datoEdicion).toEqual(dato)
    })

    it('should close edicion modal', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarModalEdicion = true
      wrapper.vm.cerrarModalEdicion()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarModalEdicion).toBe(false)
      expect(wrapper.vm.temaEdicion).toBe('')
      expect(wrapper.vm.datoEdicion).toEqual({})
    })
  })

  describe('User management', () => {
    it('should handle usuario registrado', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      const datosUsuario = { id: 1, nombre: 'Test User' }
      await wrapper.vm.manejarUsuarioRegistrado(datosUsuario)

      expect(wrapper.vm.mostrarModalRegistro).toBe(false)
      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should set usuarios from tabla', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const usuarios = [
        { id: 1, nombre: 'User 1', roles: [{ nombre_rol: 'Administrador' }] },
        { id: 2, nombre: 'User 2', roles: [{ nombre_rol: 'Deportista' }] }
      ]

      wrapper.vm.setUsuarios(usuarios)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.usuariosPanel.length).toBe(2)
    })

    it('should update usuario', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.usuariosPanel = [
        { id_usuario: 1, nombre: 'User 1' },
        { id_usuario: 2, nombre: 'User 2' }
      ]

      const usuarioActualizado = { id_usuario: 1, nombre: 'User Updated' }
      wrapper.vm.actualizarUsuario(usuarioActualizado)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.usuariosPanel[0].nombre).toBe('User Updated')
    })
  })

  describe('Statistics', () => {
    it('should calculate total usuarios', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.usuariosPanel = [
        { id: 1 },
        { id: 2 },
        { id: 3 }
      ]

      expect(wrapper.vm.totalUsuarios).toBe(3)
    })

    it('should calculate conteos por rol', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.usuariosPanel = [
        { id: 1, roles: [{ nombre_rol: 'Administrador' }] },
        { id: 2, roles: [{ nombre_rol: 'Administrador' }, { nombre_rol: 'Deportista' }] },
        { id: 3, roles: [{ nombre_rol: 'Deportista' }] }
      ]

      const conteos = wrapper.vm.conteosPorRol
      expect(conteos['Administrador']).toBe(2)
      expect(conteos['Deportista']).toBe(2)
    })

    it('should generate stat cards', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.usuariosPanel = [
        { id: 1, roles: [{ nombre_rol: 'Administrador' }] },
        { id: 2, roles: [{ nombre_rol: 'Deportista' }] }
      ]

      const tarjetas = wrapper.vm.tarjetasStats
      expect(tarjetas.length).toBeGreaterThan(0)
      expect(tarjetas[0].key).toBe('total')
      expect(tarjetas[0].count).toBe(2)
    })
  })

  describe('Dynamic data management', () => {
    it('should handle guardar dato successfully', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      globalThis.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      })

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })
      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      const payload = {
        entidad: 'tipo_documento',
        nombre: 'Cédula'
      }

      await wrapper.vm.onGuardarDato(payload)
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalled()
      expect(wrapper.vm.mostrarModalDatos).toBe(false)
    })

    it('should handle guardar dato error', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ success: false, error: 'Error test' })
      })

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })
      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      const payload = {
        entidad: 'tipo_documento',
        nombre: 'Cédula'
      }

      await wrapper.vm.onGuardarDato(payload)

      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should handle dato guardado', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const initialValue = wrapper.vm.recargarTablaDatos
      wrapper.vm.onDatoGuardado()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.recargarTablaDatos).toBe(!initialValue)
      expect(wrapper.vm.mostrarModalEdicion).toBe(false)
    })

    it('should handle dato eliminado', () => {
      wrapper = createWrapper()
      // No debería lanzar error
      expect(() => wrapper.vm.onDatoEliminado()).not.toThrow()
    })
  })

  describe('Helper functions', () => {
    it('should map tema backend correctly', () => {
      wrapper = createWrapper()

      expect(wrapper.vm.obtenerTemaBackend('tipo_documento')).toBe('tipo-documento')
      expect(wrapper.vm.obtenerTemaBackend('ciudad')).toBe('ciudad-residencia')
      expect(wrapper.vm.obtenerTemaBackend('metodo_pago')).toBe('metodo-pago')
    })

    it('should get legible entity name', () => {
      wrapper = createWrapper()

      expect(wrapper.vm.obtenerNombreEntidadLegible('tipo_documento')).toBe('tipo de documento')
      expect(wrapper.vm.obtenerNombreEntidadLegible('eps')).toBe('EPS')
      expect(wrapper.vm.obtenerNombreEntidadLegible('unknown')).toBe('dato')
    })

    it('should extract error message correctly', () => {
      wrapper = createWrapper()

      expect(wrapper.vm.extraerMensajeErrorDato('Simple error')).toBe('Simple error')
      expect(wrapper.vm.extraerMensajeErrorDato({ message: 'Error message' })).toBe('Error message')
      expect(wrapper.vm.extraerMensajeErrorDato({ error: 'Error field' })).toBe('Error field')
    })

    it('should prepare datos for metodo pago', () => {
      wrapper = createWrapper()

      const datos = wrapper.vm.prepararDatosMetodoPago('Efectivo', { estado: true })
      expect(datos.nombre_metodo).toBe('Efectivo')
      expect(datos.estado).toBe(true)
    })

    it('should prepare datos for EPS', () => {
      wrapper = createWrapper()

      const datos = wrapper.vm.prepararDatosEPS('EPS Test', 'EPS001', { estado: true })
      expect(datos.nombre_eps).toBe('EPS Test')
      expect(datos.codigo_eps).toBe('EPS001')
      expect(datos.estado).toBe(true)
    })

    it('should prepare datos for tipo evento', () => {
      wrapper = createWrapper()

      const datos = wrapper.vm.prepararDatosTipoEvento('Competencia', { descripcion: 'Desc test' })
      expect(datos.nombre).toBe('Competencia')
      expect(datos.descripcion).toBe('Desc test')
    })

    it('should prepare datos por entidad', () => {
      wrapper = createWrapper()

      const datos1 = wrapper.vm.prepararDatosPorEntidad('tipo_documento', 'Cédula', '', {})
      expect(datos1.nombre_documento).toBe('Cédula')

      const datos2 = wrapper.vm.prepararDatosPorEntidad('sexo', 'Masculino', '', {})
      expect(datos2.nombre).toBe('Masculino')
    })
  })

  describe('Filters', () => {
    it('should toggle filtros', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarFiltros).toBe(false)
      // Simular click en botón (esto se haría con wrapper.find().trigger())
      wrapper.vm.mostrarFiltros = true
      expect(wrapper.vm.mostrarFiltros).toBe(true)
    })

    it('should toggle busqueda', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarBusqueda).toBe(false)
      wrapper.vm.mostrarBusqueda = true
      expect(wrapper.vm.mostrarBusqueda).toBe(true)
    })
  })

  describe('Roles loading', () => {
    it('should load roles on mount', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockUsuariosService.default.listarRoles).toHaveBeenCalled()
      expect(wrapper.vm.rolesOptions.length).toBeGreaterThan(1) // Debe tener 'Todos' + roles
    })

    it('should handle error loading roles', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      mockUsuariosService.default.listarRoles.mockRejectedValueOnce(new Error('Network error'))

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(consoleSpy).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })

    it('should handle roles response without success', async () => {
      mockUsuariosService.default.listarRoles.mockResolvedValueOnce({
        success: false,
        data: null
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // rolesOptions should still have 'Todos'
      expect(wrapper.vm.rolesOptions.length).toBeGreaterThanOrEqual(1)
    })

    it('should handle roles response with non-array data', async () => {
      mockUsuariosService.default.listarRoles.mockResolvedValueOnce({
        success: true,
        data: null
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.rolesOptions.length).toBeGreaterThanOrEqual(1)
    })
  })

  describe('Modal datos con tema', () => {
    it('should open datos modal with tema', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.abrirModalDatosConTema('eps')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarModalDatos).toBe(true)
      expect(wrapper.vm.temaParaCrear).toBe('eps')
    })

    it('should close datos modal and clear tema', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarModalDatos = true
      wrapper.vm.temaParaCrear = 'eps'
      wrapper.vm.cerrarModalDatos()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarModalDatos).toBe(false)
      expect(wrapper.vm.temaParaCrear).toBe('')
    })
  })

  describe('Statistics edge cases', () => {
    it('should handle usuarios without roles', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.usuariosPanel = [
        { id: 1, roles: null },
        { id: 2, roles: [] },
        { id: 3 }
      ]

      const tarjetas = wrapper.vm.tarjetasStats
      const pendientesCard = tarjetas.find(t => t.key === 'pendientes')
      expect(pendientesCard).toBeDefined()
      expect(pendientesCard.count).toBe(3)
    })

    it('should generate stat cards for all roles', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.usuariosPanel = [
        { id: 1, roles: [{ nombre_rol: 'SuperAdmin' }] },
        { id: 2, roles: [{ nombre_rol: 'Administrador' }] },
        { id: 3, roles: [{ nombre_rol: 'Entrenador' }] },
        { id: 4, roles: [{ nombre_rol: 'Deportista' }] },
        { id: 5, roles: [{ nombre_rol: 'Acudiente' }] },
        { id: 6, roles: [{ nombre_rol: 'Usuario' }] }
      ]

      const tarjetas = wrapper.vm.tarjetasStats
      expect(tarjetas.length).toBeGreaterThan(6)
    })

    it('should handle usuarios with multiple roles', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.usuariosPanel = [
        { id: 1, roles: [{ nombre_rol: 'Administrador' }, { nombre_rol: 'Deportista' }] }
      ]

      const conteos = wrapper.vm.conteosPorRol
      expect(conteos['Administrador']).toBe(1)
      expect(conteos['Deportista']).toBe(1)
    })
  })

  describe('onGuardarDato edge cases', () => {
    it('should handle error response from API', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      globalThis.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ error: 'Server error' })
      })

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      const payload = {
        entidad: 'tipo_documento',
        nombre: 'Cédula'
      }

      await wrapper.vm.onGuardarDato(payload)
      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should handle mostrarErrorEntidadNoDisponible', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.mostrarErrorEntidadNoDisponible('test_entidad')

      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'warning',
        title: 'Función no disponible',
        text: 'La creación de "test_entidad" aún no está disponible desde esta interfaz.'
      })
    })

    it('should prepare datos for tipo-evento with descripcion', () => {
      wrapper = createWrapper()

      const datos = wrapper.vm.prepararDatosTipoEvento('Competencia', { descripcion: 'Descripción test' })
      expect(datos.nombre).toBe('Competencia')
      expect(datos.descripcion).toBe('Descripción test')
    })

    it('should prepare datos for EPS without codigo', () => {
      wrapper = createWrapper()

      const datos = wrapper.vm.prepararDatosEPS('EPS Test', null, { estado: false })
      expect(datos.nombre_eps).toBe('EPS Test')
      expect(datos.codigo_eps).toBeUndefined()
      expect(datos.estado).toBe(false)
    })

    it('should prepare datos for metodo pago without estado', () => {
      wrapper = createWrapper()

      const datos = wrapper.vm.prepararDatosMetodoPago('Efectivo', {})
      expect(datos.nombre_metodo).toBe('Efectivo')
      expect(datos.estado).toBe(true) // Default
    })
  })

  describe('Extraer mensaje error casos adicionales', () => {
    it('should handle error with details object', () => {
      wrapper = createWrapper()

      const error = { details: { message: 'Nested error' } }
      const result = wrapper.vm.extraerMensajeErrorDato(error)
      expect(result).toContain('Nested error')
    })

    it('should handle large error object', () => {
      wrapper = createWrapper()

      const largeError = { data: 'x'.repeat(300) }
      const result = wrapper.vm.extraerMensajeErrorDato(largeError)
      expect(result).toContain('Error al procesar')
    })

    it('should handle null error', () => {
      wrapper = createWrapper()

      const result = wrapper.vm.extraerMensajeErrorDato(null)
      expect(result).toContain('No se pudo completar')
    })
  })

  describe('Event handlers from child components', () => {
    it('should handle crear-nuevo event from TablaDatosDinamicos', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const tabla = wrapper.findComponent({ name: 'TablaDatosDinamicos' })
      await tabla.vm.$emit('crear-nuevo', 'eps')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarModalDatos).toBe(true)
      expect(wrapper.vm.temaParaCrear).toBe('eps')
    })

    it('should handle editar-dato event from TablaDatosDinamicos', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const tema = 'eps'
      const dato = { id_eps: 1, nombre_eps: 'EPS Test' }
      const tabla = wrapper.findComponent({ name: 'TablaDatosDinamicos' })
      await tabla.vm.$emit('editar-dato', { tema, dato })
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarModalEdicion).toBe(true)
      expect(wrapper.vm.temaEdicion).toBe(tema)
    })
  })

  describe('obtenerNombreEntidadLegible all cases', () => {
    it('should return correct names for all entities', () => {
      wrapper = createWrapper()

      expect(wrapper.vm.obtenerNombreEntidadLegible('tipo_documento')).toBe('tipo de documento')
      expect(wrapper.vm.obtenerNombreEntidadLegible('sexo')).toBe('sexo')
      expect(wrapper.vm.obtenerNombreEntidadLegible('ciudad')).toBe('ciudad')
      expect(wrapper.vm.obtenerNombreEntidadLegible('eps')).toBe('EPS')
      expect(wrapper.vm.obtenerNombreEntidadLegible('metodo_pago')).toBe('método de pago')
      expect(wrapper.vm.obtenerNombreEntidadLegible('tipo-evento')).toBe('tipo de evento')
    })
  })
})




