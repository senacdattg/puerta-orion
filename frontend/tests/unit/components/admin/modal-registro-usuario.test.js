import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ModalRegistroUsuario from '@/components/admin/modal-registro-usuario.vue'
import FormularioGeneral from '@/components/formularios/formulario-general.vue'
import Swal from 'sweetalert2'
import { useModalScrollLock } from '@/composables/useModalScrollLock'
import { useAuthStore } from '@/stores/auth'

// Mock services
vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(() => Promise.resolve({ isConfirmed: true })),
    close: vi.fn(),
    showLoading: vi.fn()
  }
}))

vi.mock('@/composables/useModalScrollLock', () => ({
  useModalScrollLock: vi.fn()
}))

// Mock auth store
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

// Mock FormularioGeneral
vi.mock('@/components/formularios/formulario-general.vue', () => ({
  default: {
    name: 'FormularioGeneral',
    props: ['modo', 'mostrarBotonLogin', 'textoBotonRegistrar'],
    emits: ['submit', 'cancel'],
    template: '<div class="formulario-general"><button @click="$emit(\'submit\', {})">Submit</button></div>'
  }
}))

describe('ModalRegistroUsuario', () => {
  let pinia
  let wrapper
  let mockAuthStore

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    mockAuthStore = {
      register: vi.fn().mockResolvedValue({ success: true })
    }

    useAuthStore.mockReturnValue(mockAuthStore)
    useModalScrollLock.mockReturnValue(undefined)
    vi.clearAllMocks()
  })

  const createWrapper = (props = {}) => {
    return mount(ModalRegistroUsuario, {
      props: {
        mostrar: false,
        ...props
      },
      global: {
        plugins: [pinia]
      }
    })
  }

  describe('Rendering', () => {
    it('should not render when mostrar is false', () => {
      wrapper = createWrapper({ mostrar: false })
      expect(wrapper.find('.modal-overlay').exists()).toBe(false)
    })

    it('should render when mostrar is true', () => {
      wrapper = createWrapper({ mostrar: true })
      expect(wrapper.find('.modal-overlay').exists()).toBe(true)
      expect(wrapper.find('.modal-content').exists()).toBe(true)
    })

    it('should render modal title', () => {
      wrapper = createWrapper({ mostrar: true })
      expect(wrapper.find('.modal-title').text()).toContain('Registro de Nuevo Usuario')
    })

    it('should render FormularioGeneral component', () => {
      wrapper = createWrapper({ mostrar: true })
      const formulario = wrapper.findComponent(FormularioGeneral)
      expect(formulario.exists()).toBe(true)
      expect(formulario.props('modo')).toBe('registrar')
      expect(formulario.props('mostrarBotonLogin')).toBe(false)
    })
  })

  describe('Modal Interaction', () => {
    beforeEach(() => {
      wrapper = createWrapper({ mostrar: true })
    })

    it('should emit cerrar when close button is clicked and confirmed', async () => {
      Swal.fire.mockResolvedValue({ isConfirmed: true })
      
      const closeButton = wrapper.find('.btn-cerrar')
      await closeButton.trigger('click')

      expect(Swal.fire).toHaveBeenCalled()
      expect(wrapper.emitted('cerrar')).toBeTruthy()
    })

    it('should not emit cerrar when close is cancelled', async () => {
      Swal.fire.mockResolvedValue({ isConfirmed: false })
      
      const closeButton = wrapper.find('.btn-cerrar')
      await closeButton.trigger('click')

      expect(Swal.fire).toHaveBeenCalled()
      expect(wrapper.emitted('cerrar')).toBeFalsy()
    })

    it('should emit cerrar when overlay is clicked and confirmed', async () => {
      Swal.fire.mockResolvedValue({ isConfirmed: true })
      
      const overlay = wrapper.find('.modal-overlay')
      await overlay.trigger('click')

      expect(Swal.fire).toHaveBeenCalled()
      expect(wrapper.emitted('cerrar')).toBeTruthy()
    })

    it('should not close when clicking inside modal content', async () => {
      const modalContent = wrapper.find('.modal-content')
      await modalContent.trigger('click')

      expect(wrapper.emitted('cerrar')).toBeFalsy()
    })
  })

  describe('Registration', () => {
    beforeEach(() => {
      wrapper = createWrapper({ mostrar: true })
    })

    it('should handle registration successfully', async () => {
      const datosFormulario = {
        nombre1: 'Juan',
        nombre2: 'Carlos',
        apellido1: 'Pérez',
        apellido2: 'García',
        numeroDocumento: '1234567890',
        correo: 'juan@example.com',
        direccion: 'Calle 123',
        telefono: '3001234567',
        idTipoDocumento: '1',
        idSexo: '1',
        usuario: 'juanperez',
        contrasena: 'password123'
      }

      Swal.fire
        .mockResolvedValueOnce({ isConfirmed: true }) // Confirmación inicial
        .mockResolvedValueOnce({}) // Success message

      mockAuthStore.register.mockResolvedValue({ success: true })

      await wrapper.vm.manejarRegistro(datosFormulario)
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalled()
      expect(mockAuthStore.register).toHaveBeenCalled()
      expect(wrapper.emitted('usuario-registrado')).toBeTruthy()
      expect(wrapper.emitted('cerrar')).toBeTruthy()
    })

    it('should not register if confirmation is cancelled', async () => {
      const datosFormulario = {
        nombre1: 'Juan',
        apellido1: 'Pérez',
        numeroDocumento: '1234567890',
        correo: 'juan@example.com',
        idTipoDocumento: '1',
        idSexo: '1',
        usuario: 'juanperez',
        contrasena: 'password123'
      }

      Swal.fire.mockResolvedValue({ isConfirmed: false })

      await wrapper.vm.manejarRegistro(datosFormulario)

      expect(mockAuthStore.register).not.toHaveBeenCalled()
      expect(wrapper.emitted('usuario-registrado')).toBeFalsy()
    })

    it('should handle registration error', async () => {
      const datosFormulario = {
        nombre1: 'Juan',
        apellido1: 'Pérez',
        numeroDocumento: '1234567890',
        correo: 'juan@example.com',
        idTipoDocumento: '1',
        idSexo: '1',
        usuario: 'juanperez',
        contrasena: 'password123'
      }

      Swal.fire
        .mockResolvedValueOnce({ isConfirmed: true })
        .mockResolvedValueOnce({}) // Error message

      mockAuthStore.register.mockResolvedValue({
        success: false,
        error: 'Usuario ya existe'
      })

      await wrapper.vm.manejarRegistro(datosFormulario)
      await wrapper.vm.$nextTick()

      expect(mockAuthStore.register).toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalled()
      const errorCall = Swal.fire.mock.calls.find(call => call[0].icon === 'error')
      expect(errorCall).toBeTruthy()
    })

    it('should handle registration exception', async () => {
      const datosFormulario = {
        nombre1: 'Juan',
        apellido1: 'Pérez',
        numeroDocumento: '1234567890',
        correo: 'juan@example.com',
        idTipoDocumento: '1',
        idSexo: '1',
        usuario: 'juanperez',
        contrasena: 'password123'
      }

      Swal.fire
        .mockResolvedValueOnce({ isConfirmed: true })
        .mockResolvedValueOnce({}) // Error message

      mockAuthStore.register.mockRejectedValue(new Error('Network error'))

      await wrapper.vm.manejarRegistro(datosFormulario)
      await wrapper.vm.$nextTick()

      expect(Swal.close).toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalled()
      const errorCall = Swal.fire.mock.calls.find(call => call[0].icon === 'error')
      expect(errorCall).toBeTruthy()
    })

    it('should show loading during registration', async () => {
      const datosFormulario = {
        nombre1: 'Juan',
        apellido1: 'Pérez',
        numeroDocumento: '1234567890',
        correo: 'juan@example.com',
        idTipoDocumento: '1',
        idSexo: '1',
        usuario: 'juanperez',
        contrasena: 'password123'
      }

      Swal.fire.mockResolvedValue({ isConfirmed: true })
      mockAuthStore.register.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({ success: true }), 100)))

      wrapper.vm.manejarRegistro(datosFormulario)
      await wrapper.vm.$nextTick()

      // Check that loading was shown
      const loadingCall = Swal.fire.mock.calls.find(call => call[0].title === 'Registrando usuario...')
      expect(loadingCall).toBeTruthy()
    })
  })

  describe('Cancel Registration', () => {
    beforeEach(() => {
      wrapper = createWrapper({ mostrar: true })
    })

    it('should close modal when cancel is confirmed', async () => {
      Swal.fire
        .mockResolvedValueOnce({ isConfirmed: true }) // Cancel confirmation
        .mockResolvedValueOnce({ isConfirmed: true }) // Close confirmation

      const formulario = wrapper.findComponent(FormularioGeneral)
      await formulario.vm.$emit('cancel')
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalled()
      expect(wrapper.emitted('cerrar')).toBeTruthy()
    })

    it('should not close modal when cancel is not confirmed', async () => {
      Swal.fire.mockResolvedValue({ isConfirmed: false })

      const formulario = wrapper.findComponent(FormularioGeneral)
      await formulario.vm.$emit('cancel')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('cerrar')).toBeFalsy()
    })
  })

  describe('Error Message Extraction', () => {
    beforeEach(() => {
      wrapper = createWrapper({ mostrar: true })
    })

    it('should extract error message from string', () => {
      const error = 'Error message'
      const message = wrapper.vm.extraerMensajeError(error)
      expect(message).toBe('Error message')
    })

    it('should extract error message from object with message', () => {
      const error = { message: 'Error message' }
      const message = wrapper.vm.extraerMensajeError(error)
      expect(message).toBe('Error message')
    })

    it('should extract error message from object with error', () => {
      const error = { error: 'Error message' }
      const message = wrapper.vm.extraerMensajeError(error)
      expect(message).toBe('Error message')
    })

    it('should extract error message from object with details', () => {
      const error = { details: 'Error details' }
      const message = wrapper.vm.extraerMensajeError(error)
      expect(message).toBe('Error details')
    })

    it('should return default message for null error', () => {
      const message = wrapper.vm.extraerMensajeError(null)
      expect(message).toContain('No se pudo completar el registro')
    })

    it('should handle large JSON error objects', () => {
      const largeError = { data: 'x'.repeat(300) }
      const message = wrapper.vm.extraerMensajeError(largeError)
      expect(message).toContain('Error al procesar la solicitud')
    })

    it('should handle non-stringifiable error objects', () => {
      const circularError = {}
      circularError.self = circularError
      const message = wrapper.vm.extraerMensajeError(circularError)
      expect(message).toContain('Error desconocido')
    })
  })

  describe('Data Formatting', () => {
    beforeEach(() => {
      wrapper = createWrapper({ mostrar: true })
    })

    it('should format registration data correctly', async () => {
      const datosFormulario = {
        nombre1: 'Juan',
        nombre2: 'Carlos',
        apellido1: 'Pérez',
        apellido2: 'García',
        numeroDocumento: '1234567890',
        correo: 'juan@example.com',
        direccion: 'Calle 123',
        telefono: '3001234567',
        idTipoDocumento: '1',
        idSexo: '2',
        usuario: 'juanperez',
        contrasena: 'password123'
      }

      Swal.fire.mockResolvedValue({ isConfirmed: true })
      mockAuthStore.register.mockResolvedValue({ success: true })

      await wrapper.vm.manejarRegistro(datosFormulario)

      expect(mockAuthStore.register).toHaveBeenCalledWith({
        persona: {
          primer_nombre: 'Juan',
          segundo_nombre: 'Carlos',
          primer_apellido: 'Pérez',
          segundo_apellido: 'García',
          documento: '1234567890',
          correo_electronico: 'juan@example.com',
          direccion: 'Calle 123',
          telefono: '3001234567',
          id_tipo_documento: 1,
          id_sexo: 2
        },
        usuario: {
          usuario: 'juanperez',
          password: 'password123'
        }
      })
    })

    it('should handle missing optional fields', async () => {
      const datosFormulario = {
        nombre1: 'Juan',
        apellido1: 'Pérez',
        numeroDocumento: '1234567890',
        correo: 'juan@example.com',
        idTipoDocumento: '1',
        idSexo: '1',
        usuario: 'juanperez',
        contrasena: 'password123'
      }

      Swal.fire.mockResolvedValue({ isConfirmed: true })
      mockAuthStore.register.mockResolvedValue({ success: true })

      await wrapper.vm.manejarRegistro(datosFormulario)

      const callArgs = mockAuthStore.register.mock.calls[0][0]
      expect(callArgs.persona.segundo_nombre).toBe(null)
      expect(callArgs.persona.segundo_apellido).toBe(null)
    })
  })

  describe('Modal Scroll Lock', () => {
    it('should use modal scroll lock when modal is shown', () => {
      wrapper = createWrapper({ mostrar: true })
      expect(useModalScrollLock).toHaveBeenCalled()
    })
  })
})

