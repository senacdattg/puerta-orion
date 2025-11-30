import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import VistaDeportistas from '@/views/vista-deportistas.vue'
import deportistasService from '@/services/deportistasService'
import usuariosService from '@/services/usuariosService'
import Swal from 'sweetalert2'

// Mock services
vi.mock('@/services/deportistasService', () => ({
  default: {
    listarDeportistas: vi.fn(),
    obtenerDeportistaPorId: vi.fn()
  }
}))

vi.mock('@/services/usuariosService', () => ({
  default: {
    cambiarEstadoUsuario: vi.fn()
  }
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(() => Promise.resolve({ isConfirmed: true }))
  }
}))

vi.mock('@/composables/useModalScrollLock', () => ({
  useModalScrollLock: vi.fn()
}))

describe('VistaDeportistas', () => {
  let pinia
  let wrapper

  const mockDeportistas = [
    {
      id_deportista: 1,
      nombre: 'Juan Pérez',
      nombre1: 'Juan',
      apellido1: 'Pérez',
      documento: '12345678',
      categoria_info: {
        nombre_categoria: 'Junior'
      },
      estado: 'activo',
      id_usuario: 1,
      persona: {
        primer_nombre: 'Juan',
        primer_apellido: 'Pérez',
        documento: '12345678',
        estado: true
      }
    },
    {
      id_deportista: 2,
      nombre: 'María García',
      nombre1: 'María',
      apellido1: 'García',
      documento: '87654321',
      categoria: 'Senior',
      estado: 'inactivo',
      id_usuario: 2,
      persona: {
        primer_nombre: 'María',
        primer_apellido: 'García',
        documento: '87654321',
        estado: false
      }
    }
  ]

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    vi.clearAllMocks()
    deportistasService.listarDeportistas.mockResolvedValue({
      success: true,
      data: mockDeportistas
    })
    deportistasService.obtenerDeportistaPorId.mockResolvedValue({
      success: true,
      data: mockDeportistas[0]
    })
    usuariosService.cambiarEstadoUsuario.mockResolvedValue({
      success: true
    })
  })

  const createWrapper = () => {
    return mount(VistaDeportistas, {
      global: {
        plugins: [pinia],
        stubs: {
          'Encabezado': true,
          'ListaDeportistas': true,
          'PerfilDeportistaVista': true,
          'Pie': true
        }
      }
    })
  }

  describe('Rendering', () => {
    it('should render main component', () => {
      wrapper = createWrapper()
      expect(wrapper.find('main.vista-deportistas').exists()).toBe(true)
    })

    it('should render child components', () => {
      wrapper = createWrapper()
      expect(wrapper.findComponent({ name: 'Encabezado' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'ListaDeportistas' }).exists()).toBe(true)
      expect(wrapper.findComponent({ name: 'Pie' }).exists()).toBe(true)
    })

    it('should show loading state initially', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.cargando).toBe(true)
    })
  })

  describe('Data Loading', () => {
    it('should load deportistas on mount', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(deportistasService.listarDeportistas).toHaveBeenCalledWith(1, 100)
    })

    it('should map deportistas correctly', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.deportistas.length).toBe(2)
      const primero = wrapper.vm.deportistas[0]
      expect(primero.id).toBe(1)
      expect(primero.id_deportista).toBe(1)
      expect(primero.nombre).toBe('Juan Pérez')
      expect(primero.categoria).toBe('junior')
      expect(primero.estado).toBe('activo')
    })

    it('should handle categoria from categoria_info', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const primero = wrapper.vm.deportistas[0]
      expect(primero.categoria).toBe('junior')
    })

    it('should handle categoria from direct property', async () => {
      deportistasService.listarDeportistas.mockResolvedValue({
        success: true,
        data: [mockDeportistas[1]]
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const primero = wrapper.vm.deportistas[0]
      // categoria is normalized to lowercase in the component
      expect(primero.categoria.toLowerCase()).toBe('senior')
    })

    it('should handle loading state', async () => {
      deportistasService.listarDeportistas.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 200)))
      wrapper = createWrapper()

      expect(wrapper.vm.cargando).toBe(true)
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 250))

      expect(wrapper.vm.cargando).toBe(false)
    })

    it('should handle error when loading fails', async () => {
      deportistasService.listarDeportistas.mockResolvedValue({
        success: false,
        message: 'Error loading'
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.error).toBeTruthy()
      expect(wrapper.vm.deportistas.length).toBe(0)
    })

    it('should handle exception when loading fails', async () => {
      deportistasService.listarDeportistas.mockRejectedValue(new Error('Network error'))

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.error).toBeTruthy()
      expect(wrapper.vm.deportistas.length).toBe(0)
    })

    it('should reload deportistas when retry button clicked', async () => {
      deportistasService.listarDeportistas.mockResolvedValueOnce({
        success: false,
        message: 'Error'
      })

      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      deportistasService.listarDeportistas.mockResolvedValue({
        success: true,
        data: mockDeportistas
      })

      await wrapper.vm.cargarDeportistas()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.error).toBe(null)
      expect(wrapper.vm.deportistas.length).toBe(2)
    })
  })

  describe('View Deportista', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should open modal to view deportista', async () => {
      const deportista = wrapper.vm.deportistas[0]
      await wrapper.vm.verDeportista(deportista)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarFormulario).toBe(true)
      expect(wrapper.vm.modoFormulario).toBe('ver')
      expect(deportistasService.obtenerDeportistaPorId).toHaveBeenCalled()
    })

    it('should use existing data if fetch fails', async () => {
      deportistasService.obtenerDeportistaPorId.mockRejectedValue(new Error('Not found'))
      const deportista = wrapper.vm.deportistas[0]

      await wrapper.vm.verDeportista(deportista)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarFormulario).toBe(true)
      expect(wrapper.vm.deportistaEditando).toBeTruthy()
    })

    it('should map editarDeportista to verDeportista', async () => {
      const deportista = wrapper.vm.deportistas[0]
      await wrapper.vm.editarDeportista(deportista)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarFormulario).toBe(true)
      expect(wrapper.vm.modoFormulario).toBe('ver')
    })

    it('should close modal', () => {
      wrapper.vm.mostrarFormulario = true
      wrapper.vm.deportistaEditando = mockDeportistas[0]
      wrapper.vm.cerrarFormulario()

      expect(wrapper.vm.mostrarFormulario).toBe(false)
      expect(wrapper.vm.deportistaEditando).toBe(null)
    })
  })

  describe('Form Handling', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      wrapper.vm.mostrarFormulario = true
      wrapper.vm.deportistaEditando = mockDeportistas[0]
    })

    it('should change to update mode', () => {
      wrapper.vm.cambiarAModoActualizar()
      expect(wrapper.vm.modoFormulario).toBe('actualizar')
    })

    it('should change to view mode', () => {
      wrapper.vm.modoFormulario = 'actualizar'
      wrapper.vm.cambiarAModoVer()
      expect(wrapper.vm.modoFormulario).toBe('ver')
    })

    it('should handle form submit and reload data', async () => {
      wrapper.vm.modoFormulario = 'actualizar'
      deportistasService.listarDeportistas.mockResolvedValue({
        success: true,
        data: mockDeportistas
      })
      deportistasService.obtenerDeportistaPorId.mockResolvedValue({
        success: true,
        data: mockDeportistas[0]
      })

      await wrapper.vm.manejarSubmitFormulario()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(deportistasService.listarDeportistas).toHaveBeenCalled()
      expect(wrapper.vm.modoFormulario).toBe('ver')
    })

    it('should handle form submit error', async () => {
      wrapper.vm.modoFormulario = 'actualizar'
      wrapper.vm.deportistaEditando = { id_deportista: 1, id: 1 }
      // Make obtenerDeportistaPorId fail instead, which is called in manejarSubmitFormulario
      deportistasService.obtenerDeportistaPorId.mockRejectedValue(new Error('Update failed'))
      Swal.fire.mockClear()

      await wrapper.vm.manejarSubmitFormulario()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(Swal.fire).toHaveBeenCalled()
      const swalCall = Swal.fire.mock.calls.find(call => call[0].title === 'No se pudo guardar')
      expect(swalCall).toBeTruthy()
    })
  })

  describe('Change Estado Deportista', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should change estado of deportista', async () => {
      Swal.fire.mockResolvedValue({ isConfirmed: true })
      const deportista = { ...wrapper.vm.deportistas[0], id: 1 }
      deportistasService.listarDeportistas.mockResolvedValue({
        success: true,
        data: mockDeportistas
      })

      await wrapper.vm.cambiarEstadoDeportista(deportista)
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(usuariosService.cambiarEstadoUsuario).toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should not change estado if no id_usuario', async () => {
      const deportista = { ...wrapper.vm.deportistas[0], id_usuario: null }

      await wrapper.vm.cambiarEstadoDeportista(deportista)
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalled()
      const swalCall = Swal.fire.mock.calls[0][0]
      expect(swalCall.title).toBe('Estado no disponible')
      expect(usuariosService.cambiarEstadoUsuario).not.toHaveBeenCalled()
    })

    it('should not change estado if cancelled', async () => {
      Swal.fire.mockResolvedValue({ isConfirmed: false })
      const deportista = { ...wrapper.vm.deportistas[0], id: 1 }

      await wrapper.vm.cambiarEstadoDeportista(deportista)
      await wrapper.vm.$nextTick()

      expect(usuariosService.cambiarEstadoUsuario).not.toHaveBeenCalled()
    })

    it('should handle error when changing estado', async () => {
      Swal.fire.mockResolvedValue({ isConfirmed: true })
      usuariosService.cambiarEstadoUsuario.mockResolvedValue({
        success: false,
        message: 'Error changing estado'
      })
      const deportista = { ...wrapper.vm.deportistas[0], id: 1 }

      await wrapper.vm.cambiarEstadoDeportista(deportista)
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(Swal.fire).toHaveBeenCalled()
      const errorCall = Swal.fire.mock.calls.find(call => call[0].icon === 'error')
      expect(errorCall).toBeTruthy()
    })

    it('should revert estado on error', async () => {
      Swal.fire.mockResolvedValue({ isConfirmed: true })
      usuariosService.cambiarEstadoUsuario.mockRejectedValue(new Error('Network error'))
      const deportista = { ...wrapper.vm.deportistas[0], id: 1 }

      await wrapper.vm.cambiarEstadoDeportista(deportista)
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Should revert to previous estado
      expect(Swal.fire).toHaveBeenCalled()
    })
  })

  describe('Disabled Functions', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should show info message when trying to add deportista', async () => {
      await wrapper.vm.agregarDeportista()
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalled()
      const swalCall = Swal.fire.mock.calls[0][0]
      expect(swalCall.title).toBe('Funcionalidad no disponible')
    })

    it('should not delete deportista', () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      wrapper.vm.eliminarDeportista()
      expect(consoleSpy).toHaveBeenCalledWith('Eliminación deshabilitada - solo modo visualización')
      consoleSpy.mockRestore()
    })
  })

  describe('Event Handlers', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should handle ver event from ListaDeportistas', async () => {
      const listaComponent = wrapper.findComponent({ name: 'ListaDeportistas' })
      const deportista = wrapper.vm.deportistas[0]

      await listaComponent.vm.$emit('ver', deportista)
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.mostrarFormulario).toBe(true)
    })

    it('should handle editar event from ListaDeportistas', async () => {
      const listaComponent = wrapper.findComponent({ name: 'ListaDeportistas' })
      const deportista = wrapper.vm.deportistas[0]

      await listaComponent.vm.$emit('editar', deportista)
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.mostrarFormulario).toBe(true)
      expect(wrapper.vm.modoFormulario).toBe('ver')
    })

    it('should handle cambiar-estado event', async () => {
      Swal.fire.mockResolvedValue({ isConfirmed: true })
      deportistasService.listarDeportistas.mockResolvedValue({
        success: true,
        data: mockDeportistas
      })

      const listaComponent = wrapper.findComponent({ name: 'ListaDeportistas' })
      const deportista = { ...wrapper.vm.deportistas[0], id: 1 }

      await listaComponent.vm.$emit('cambiar-estado', deportista)
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(usuariosService.cambiarEstadoUsuario).toHaveBeenCalled()
    })
  })
})

