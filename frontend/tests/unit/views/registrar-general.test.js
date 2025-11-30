import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import RegistrarGeneral from '@/views/registrar-general.vue'
import FormularioGeneral from '@/components/formularios/formulario-general.vue'
import Swal from 'sweetalert2'
import { useAuthStore } from '@/stores/auth'

// Mock services
vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(() => Promise.resolve({ isConfirmed: true })),
    close: vi.fn(),
    showLoading: vi.fn()
  }
}))

// Mock auth store
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn()
}))

// Mock vue-router
const mockRouter = {
  push: vi.fn()
}

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return {
    ...actual,
    useRouter: () => mockRouter
  }
})

// Mock FormularioGeneral
vi.mock('@/components/formularios/formulario-general.vue', () => ({
  default: {
    name: 'FormularioGeneral',
    props: ['modo'],
    emits: ['submit', 'cancel'],
    template: '<div class="formulario-general"><button @click="$emit(\'submit\', {})">Submit</button><button @click="$emit(\'cancel\')">Cancel</button></div>'
  }
}))

describe('RegistrarGeneral', () => {
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
    vi.clearAllMocks()
    mockRouter.push.mockClear()
  })

  const createWrapper = () => {
    return mount(RegistrarGeneral, {
      global: {
        plugins: [pinia]
      }
    })
  }

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = createWrapper()
      expect(wrapper.find('main').exists()).toBe(true)
    })

    it('should render FormularioGeneral component', () => {
      wrapper = createWrapper()
      const formulario = wrapper.findComponent(FormularioGeneral)
      expect(formulario.exists()).toBe(true)
      expect(formulario.props('modo')).toBe('registrar')
    })
  })

  describe('Registration', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should handle successful registration', async () => {
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

      Swal.fire.mockResolvedValue({}) // Success message
      mockAuthStore.register.mockResolvedValue({ success: true })

      await wrapper.vm.manejarRegistro(datosFormulario)
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalled()
      expect(mockAuthStore.register).toHaveBeenCalled()
      expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })

    it('should format registration data correctly', async () => {
      const datosFormulario = {
        nombre1: '  Juan  ',
        nombre2: '  Carlos  ',
        apellido1: '  Pérez  ',
        apellido2: '  García  ',
        numeroDocumento: '1234567890',
        correo: '  JUAN@EXAMPLE.COM  ',
        direccion: '  Calle 123  ',
        telefono: '3001234567',
        idTipoDocumento: '1',
        idSexo: '2',
        usuario: 'juanperez',
        contrasena: 'password123'
      }

      Swal.fire.mockResolvedValue({})
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

      Swal.fire.mockResolvedValue({})
      mockAuthStore.register.mockResolvedValue({ success: true })

      await wrapper.vm.manejarRegistro(datosFormulario)

      const callArgs = mockAuthStore.register.mock.calls[0][0]
      expect(callArgs.persona.segundo_nombre).toBe(null)
      expect(callArgs.persona.segundo_apellido).toBe(null)
      expect(callArgs.persona.direccion).toBe(null)
      expect(callArgs.persona.telefono).toBe(null)
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

      Swal.fire.mockResolvedValue({})
      mockAuthStore.register.mockResolvedValue({
        success: false,
        error: 'Usuario ya existe'
      })

      await wrapper.vm.manejarRegistro(datosFormulario)
      await wrapper.vm.$nextTick()

      expect(mockAuthStore.register).toHaveBeenCalled()
      expect(Swal.close).toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalled()
      const errorCall = Swal.fire.mock.calls.find(call => call[0].icon === 'error')
      expect(errorCall).toBeTruthy()
      expect(mockRouter.push).not.toHaveBeenCalled()
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

      Swal.fire.mockResolvedValue({})
      mockAuthStore.register.mockRejectedValue(new Error('Network error'))

      await wrapper.vm.manejarRegistro(datosFormulario)
      await wrapper.vm.$nextTick()

      expect(Swal.close).toHaveBeenCalled()
      expect(Swal.fire).toHaveBeenCalled()
      const errorCall = Swal.fire.mock.calls.find(call => call[0].icon === 'error')
      expect(errorCall).toBeTruthy()
      expect(mockRouter.push).not.toHaveBeenCalled()
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

      Swal.fire.mockResolvedValue({})
      mockAuthStore.register.mockResolvedValue({ success: true })

      await wrapper.vm.manejarRegistro(datosFormulario)

      const loadingCall = Swal.fire.mock.calls.find(call => call[0].title === 'Registrando usuario...')
      expect(loadingCall).toBeTruthy()
      expect(loadingCall[0].allowOutsideClick).toBe(false)
      expect(loadingCall[0].allowEscapeKey).toBe(false)
    })

    it('should close loading after registration', async () => {
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

      Swal.fire.mockResolvedValue({})
      mockAuthStore.register.mockResolvedValue({ success: true })

      await wrapper.vm.manejarRegistro(datosFormulario)

      expect(Swal.close).toHaveBeenCalled()
    })
  })

  describe('Cancellation', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should handle cancellation when confirmed', async () => {
      Swal.fire.mockResolvedValue({ isConfirmed: true })

      await wrapper.vm.manejarCancelacion()

      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'question',
        title: '¿Cancelar registro?',
        text: 'Los datos ingresados se perderán.',
        showCancelButton: true,
        confirmButtonText: 'Sí, cancelar',
        cancelButtonText: 'Continuar llenando'
      })
    })

    it('should handle cancellation when not confirmed', async () => {
      Swal.fire.mockResolvedValue({ isConfirmed: false })

      await wrapper.vm.manejarCancelacion()

      expect(Swal.fire).toHaveBeenCalled()
    })
  })

  describe('Form Integration', () => {
    it('should handle form submit event', async () => {
      wrapper = createWrapper()
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

      Swal.fire.mockResolvedValue({})
      mockAuthStore.register.mockResolvedValue({ success: true })

      const formulario = wrapper.findComponent(FormularioGeneral)
      await formulario.vm.$emit('submit', datosFormulario)
      await wrapper.vm.$nextTick()

      expect(mockAuthStore.register).toHaveBeenCalled()
    })

    it('should handle form cancel event', async () => {
      wrapper = createWrapper()
      Swal.fire.mockResolvedValue({ isConfirmed: true })

      const formulario = wrapper.findComponent(FormularioGeneral)
      await formulario.vm.$emit('cancel')
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalled()
    })
  })

  describe('Data Formatting', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should trim all string fields', async () => {
      const datosFormulario = {
        nombre1: '  Juan  ',
        apellido1: '  Pérez  ',
        numeroDocumento: '  1234567890  ',
        correo: '  juan@example.com  ',
        idTipoDocumento: '1',
        idSexo: '1',
        usuario: 'juanperez',
        contrasena: 'password123'
      }

      Swal.fire.mockResolvedValue({})
      mockAuthStore.register.mockResolvedValue({ success: true })

      await wrapper.vm.manejarRegistro(datosFormulario)

      const callArgs = mockAuthStore.register.mock.calls[0][0]
      expect(callArgs.persona.primer_nombre).toBe('Juan')
      expect(callArgs.persona.primer_apellido).toBe('Pérez')
      expect(callArgs.persona.documento).toBe('1234567890')
    })

    it('should convert email to lowercase', async () => {
      const datosFormulario = {
        nombre1: 'Juan',
        apellido1: 'Pérez',
        numeroDocumento: '1234567890',
        correo: 'JUAN@EXAMPLE.COM',
        idTipoDocumento: '1',
        idSexo: '1',
        usuario: 'juanperez',
        contrasena: 'password123'
      }

      Swal.fire.mockResolvedValue({})
      mockAuthStore.register.mockResolvedValue({ success: true })

      await wrapper.vm.manejarRegistro(datosFormulario)

      const callArgs = mockAuthStore.register.mock.calls[0][0]
      expect(callArgs.persona.correo_electronico).toBe('juan@example.com')
    })

    it('should parse idTipoDocumento and idSexo as integers', async () => {
      const datosFormulario = {
        nombre1: 'Juan',
        apellido1: 'Pérez',
        numeroDocumento: '1234567890',
        correo: 'juan@example.com',
        idTipoDocumento: '5',
        idSexo: '3',
        usuario: 'juanperez',
        contrasena: 'password123'
      }

      Swal.fire.mockResolvedValue({})
      mockAuthStore.register.mockResolvedValue({ success: true })

      await wrapper.vm.manejarRegistro(datosFormulario)

      const callArgs = mockAuthStore.register.mock.calls[0][0]
      expect(callArgs.persona.id_tipo_documento).toBe(5)
      expect(callArgs.persona.id_sexo).toBe(3)
    })

    it('should convert telefono to string', async () => {
      const datosFormulario = {
        nombre1: 'Juan',
        apellido1: 'Pérez',
        numeroDocumento: '1234567890',
        correo: 'juan@example.com',
        telefono: 3001234567, // Number
        idTipoDocumento: '1',
        idSexo: '1',
        usuario: 'juanperez',
        contrasena: 'password123'
      }

      Swal.fire.mockResolvedValue({})
      mockAuthStore.register.mockResolvedValue({ success: true })

      await wrapper.vm.manejarRegistro(datosFormulario)

      const callArgs = mockAuthStore.register.mock.calls[0][0]
      expect(typeof callArgs.persona.telefono).toBe('string')
      expect(callArgs.persona.telefono).toBe('3001234567')
    })
  })

  describe('Success Flow', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should show success message before redirecting', async () => {
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

      Swal.fire.mockResolvedValue({})
      mockAuthStore.register.mockResolvedValue({ success: true })

      await wrapper.vm.manejarRegistro(datosFormulario)

      const successCall = Swal.fire.mock.calls.find(call => call[0].icon === 'success')
      expect(successCall).toBeTruthy()
      expect(successCall[0].title).toBe('Registro exitoso')
    })

    it('should redirect to login after success', async () => {
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

      Swal.fire.mockResolvedValue({})
      mockAuthStore.register.mockResolvedValue({ success: true })

      await wrapper.vm.manejarRegistro(datosFormulario)
      await wrapper.vm.$nextTick()

      expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })
  })
})

