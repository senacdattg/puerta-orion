import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import RegistrarDeportista from '@/views/registrar-deportista.vue'
import Swal from 'sweetalert2'

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn()
  }
}))

vi.mock('@/components/formularios/formulario-deportista.vue', () => ({
  default: {
    name: 'FormularioDeportista',
    template: '<div class="formulario-deportista">Formulario</div>',
    props: ['modo'],
    emits: ['submit', 'cancel']
  }
}))

describe('RegistrarDeportista', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  const createWrapper = () => {
    return mount(RegistrarDeportista, {
      global: {
        stubs: {}
      }
    })
  }

  describe('Renderizado básico', () => {
    it('should render component', () => {
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('main').exists()).toBe(true)
    })

    it('should render FormularioDeportista component', () => {
      wrapper = createWrapper()
      expect(wrapper.findComponent({ name: 'FormularioDeportista' }).exists()).toBe(true)
    })

    it('should pass modo prop to FormularioDeportista', () => {
      wrapper = createWrapper()
      const formulario = wrapper.findComponent({ name: 'FormularioDeportista' })
      expect(formulario.props('modo')).toBe('registrar')
    })
  })

  describe('Manejar registro', () => {
    it('should handle registro successfully', async () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      wrapper = createWrapper()
      const formulario = wrapper.findComponent({ name: 'FormularioDeportista' })
      const datos = { nombre: 'Juan', apellido: 'Pérez' }

      Swal.fire.mockResolvedValue({})

      await formulario.vm.$emit('submit', datos)
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(consoleSpy).toHaveBeenCalledWith('Datos del nuevo deportista:', datos)
      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'success',
        title: 'Registro exitoso',
        text: 'El deportista se registró correctamente.',
        timer: 1500,
        showConfirmButton: false
      })

      consoleSpy.mockRestore()
    })
  })

  describe('Manejar cancelación', () => {
    it('should handle cancelación when confirmed', async () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      wrapper = createWrapper()
      const formulario = wrapper.findComponent({ name: 'FormularioDeportista' })

      Swal.fire.mockResolvedValue({ isConfirmed: true })

      await formulario.vm.$emit('cancel')
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'question',
        title: '¿Cancelar registro?',
        text: 'Los datos ingresados se perderán.',
        showCancelButton: true,
        confirmButtonText: 'Sí, cancelar',
        cancelButtonText: 'Continuar llenando'
      })
      expect(consoleSpy).toHaveBeenCalledWith('Registro cancelado')

      consoleSpy.mockRestore()
    })

    it('should not log cancellation when not confirmed', async () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      wrapper = createWrapper()
      const formulario = wrapper.findComponent({ name: 'FormularioDeportista' })

      Swal.fire.mockResolvedValue({ isConfirmed: false })

      await formulario.vm.$emit('cancel')
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(Swal.fire).toHaveBeenCalled()
      expect(consoleSpy).not.toHaveBeenCalledWith('Registro cancelado')

      consoleSpy.mockRestore()
    })
  })
})

