import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PerfilModal from '@/components/deportistas/PerfilModal.vue'
import Swal from 'sweetalert2'

const mockUseAuthStore = vi.fn()
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockUseAuthStore()
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn()
  }
}))

describe('PerfilModal', () => {
  let wrapper
  let mockAuthStore

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    mockAuthStore = {
      user: {
        persona: {
          nombre_completo: 'Juan Pérez',
          documento: '12345678',
          correo_electronico: 'juan@test.com',
          telefono: '3001234567',
          direccion: 'Calle 123',
          fecha_nacimiento: '2010-06-14',
          tipo_sanguineo: {
            nombre: 'O+'
          },
          ciudad: {
            nombre: 'Bogotá'
          }
        }
      },
      updateUser: vi.fn()
    }

    mockUseAuthStore.mockReturnValue(mockAuthStore)
  })

  const createWrapper = (props = {}) => {
    return mount(PerfilModal, {
      props: {
        visible: props.visible !== undefined ? props.visible : true
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })
  }

  describe('Renderizado básico', () => {
    it('should render component when visible is true', () => {
      wrapper = createWrapper({ visible: true })
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.perfil-modal-overlay').exists()).toBe(true)
    })

    it('should not render when visible is false', () => {
      wrapper = createWrapper({ visible: false })
      expect(wrapper.find('.perfil-modal-overlay').exists()).toBe(false)
    })

    it('should display modal title', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Mi Perfil')
    })
  })

  describe('Información del perfil', () => {
    it('should display nombre completo', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Juan Pérez')
    })

    it('should display documento', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('12345678')
    })

    it('should display correo electrónico', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('juan@test.com')
    })

    it('should display teléfono', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('3001234567')
    })

    it('should display tipo sanguíneo', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('O+')
    })

    it('should display ciudad', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Bogotá')
    })

    it('should display "No disponible" when data is missing', () => {
      mockAuthStore.user = { persona: {} }
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('No disponible')
    })

    it('should format fecha de nacimiento', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatearFecha('2010-06-14')).toBeTruthy()
    })

    it('should return null when fecha is null', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.formatearFecha(null)).toBeNull()
    })

    it('should return original value when fecha format is invalid', () => {
      wrapper = createWrapper()
      const result = wrapper.vm.formatearFecha('invalid-date')
      expect(result).toBe('invalid-date')
    })

    it('should not display diagnostico section when diagnostico is null', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.diagnostico).toBeNull()
    })
  })

  describe('Computed properties', () => {
    it('should compute tipoSangre correctly', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.tipoSangre).toBe('O+')
    })

    it('should return null when tipoSangre is missing', () => {
      mockAuthStore.user.persona.tipo_sanguineo = null
      wrapper = createWrapper()
      expect(wrapper.vm.tipoSangre).toBeNull()
    })

    it('should compute ciudad correctly', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.ciudad).toBe('Bogotá')
    })

    it('should return null when ciudad is missing', () => {
      mockAuthStore.user.persona.ciudad = null
      wrapper = createWrapper()
      expect(wrapper.vm.ciudad).toBeNull()
    })
  })

  describe('Edición', () => {
    it('should show edit form when iniciarEdicion is called', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.iniciarEdicion()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.editando).toBe(true)
      expect(wrapper.find('.perfil-editar').exists()).toBe(true)
    })

    it('should initialize formData with user data', () => {
      wrapper = createWrapper()
      wrapper.vm.iniciarEdicion()

      expect(wrapper.vm.formData.correo_electronico).toBe('juan@test.com')
      expect(wrapper.vm.formData.telefono).toBe('3001234567')
      expect(wrapper.vm.formData.direccion).toBe('Calle 123')
    })

    it('should initialize formData with empty strings when user data is missing', () => {
      mockAuthStore.user = { persona: {} }
      wrapper = createWrapper()
      wrapper.vm.iniciarEdicion()

      expect(wrapper.vm.formData.correo_electronico).toBe('')
      expect(wrapper.vm.formData.telefono).toBe('')
      expect(wrapper.vm.formData.direccion).toBe('')
    })

    it('should cancel edicion', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.iniciarEdicion()
      wrapper.vm.cancelarEdicion()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.editando).toBe(false)
    })

    it('should show edit button when not editing', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.modal-footer').exists()).toBe(true)
      expect(wrapper.text()).toContain('Editar información')
    })

    it('should not show edit button when editing', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.editando = true
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.modal-footer').exists()).toBe(false)
    })
  })

  describe('Guardar cambios', () => {
    it('should save changes successfully', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.iniciarEdicion()
      wrapper.vm.formData.correo_electronico = 'nuevo@test.com'
      
      Swal.fire.mockResolvedValue({})
      
      await wrapper.vm.guardarCambios()
      await wrapper.vm.$nextTick()

      expect(mockAuthStore.updateUser).toHaveBeenCalled()
      expect(wrapper.vm.editando).toBe(false)
      expect(wrapper.emitted('update')).toBeTruthy()
      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'success',
        title: 'Información actualizada',
        text: 'Perfil guardado correctamente.',
        timer: 1500,
        showConfirmButton: false
      })
    })

    it('should set guardando to true during save', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.iniciarEdicion()
      Swal.fire.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({}), 100)))

      const savePromise = wrapper.vm.guardarCambios()
      expect(wrapper.vm.guardando).toBe(true)

      await savePromise
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.guardando).toBe(false)
    })

    it('should handle error when saving changes', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      mockAuthStore.updateUser.mockImplementation(() => {
        throw new Error('Update failed')
      })

      wrapper.vm.iniciarEdicion()
      Swal.fire.mockResolvedValue({})

      await wrapper.vm.guardarCambios()
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'error',
        title: 'No se pudo guardar',
        text: 'Inténtalo de nuevo.'
      })
      expect(consoleSpy).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })

    it('should disable submit button when guardando', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.iniciarEdicion()
      wrapper.vm.guardando = true
      await wrapper.vm.$nextTick()

      const submitButton = wrapper.find('button[type="submit"]')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })
  })

  describe('Cerrar modal', () => {
    it('should emit close event when cerrarModal is called', () => {
      wrapper = createWrapper()
      wrapper.vm.cerrarModal()

      expect(wrapper.emitted('close')).toBeTruthy()
      expect(wrapper.vm.editando).toBe(false)
    })

    it('should close modal when overlay is clicked', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const overlay = wrapper.find('.perfil-modal-overlay')
      await overlay.trigger('click')

      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('should close modal when close button is clicked', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const closeButton = wrapper.find('.modal-close')
      await closeButton.trigger('click')

      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('should not close modal when modal content is clicked', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const modal = wrapper.find('.perfil-modal')
      await modal.trigger('click')

      // No debería emitir close porque el click no fue en el overlay
      expect(wrapper.emitted('close')).toBeFalsy()
    })
  })

  describe('Watch visible prop', () => {
    it('should reset editando when visible becomes false', async () => {
      wrapper = createWrapper({ visible: true })
      await wrapper.vm.$nextTick()

      wrapper.vm.editando = true
      await wrapper.setProps({ visible: false })
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.editando).toBe(false)
    })
  })

  describe('Form validation', () => {
    it('should require email field', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.iniciarEdicion()
      await wrapper.vm.$nextTick()

      const emailInput = wrapper.find('#correo-electronico-modal')
      expect(emailInput.attributes('required')).toBeDefined()
    })
  })
})

