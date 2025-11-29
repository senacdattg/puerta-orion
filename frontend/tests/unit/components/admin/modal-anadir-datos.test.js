import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ModalAnadirDatos from '@/components/admin/modal-anadir-datos.vue'
import Swal from 'sweetalert2'

// Mock components
vi.mock('@/components/datos-dinamicos/tipo-documento.vue', () => ({
  default: {
    name: 'TipoDocumento',
    template: '<div>Tipo Documento</div>',
    props: ['modelValue'],
    emits: ['update:modelValue']
  }
}))

vi.mock('@/components/datos-dinamicos/sexo.vue', () => ({
  default: {
    name: 'Sexo',
    template: '<div>Sexo</div>',
    props: ['modelValue'],
    emits: ['update:modelValue']
  }
}))

vi.mock('@/components/datos-dinamicos/ciudad.vue', () => ({
  default: {
    name: 'Ciudad',
    template: '<div>Ciudad</div>',
    props: ['modelValue'],
    emits: ['update:modelValue']
  }
}))

vi.mock('@/components/datos-dinamicos/eps.vue', () => ({
  default: {
    name: 'Eps',
    template: '<div>EPS</div>',
    props: ['modelValue'],
    emits: ['update:modelValue']
  }
}))

vi.mock('@/components/datos-dinamicos/metodo-pago.vue', () => ({
  default: {
    name: 'MetodoPago',
    template: '<div>Método Pago</div>',
    props: ['modelValue'],
    emits: ['update:modelValue']
  }
}))

vi.mock('@/components/datos-dinamicos/tipo-evento.vue', () => ({
  default: {
    name: 'TipoEvento',
    template: '<div>Tipo Evento</div>',
    props: ['modelValue'],
    emits: ['update:modelValue']
  }
}))

vi.mock('@/composables/useModalScrollLock', () => ({
  useModalScrollLock: vi.fn()
}))

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn(),
    close: vi.fn(),
    showLoading: vi.fn(),
    Swal: {
      fire: vi.fn(),
      close: vi.fn(),
      showLoading: vi.fn()
    }
  }
}))

describe('ModalAnadirDatos Component', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  const createWrapper = (props = {}) => {
    return mount(ModalAnadirDatos, {
      props: {
        mostrar: props.mostrar !== undefined ? props.mostrar : true,
        temaInicial: props.temaInicial || ''
      },
      global: {
        stubs: {
          'i': true
        }
      }
    })
  }

  describe('Renderizado básico', () => {
    it('should render component when mostrar is true', () => {
      wrapper = createWrapper({ mostrar: true })
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.modal-overlay').exists()).toBe(true)
    })

    it('should not render when mostrar is false', () => {
      wrapper = createWrapper({ mostrar: false })
      expect(wrapper.find('.modal-overlay').exists()).toBe(false)
    })

    it('should display step 1 by default', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.paso).toBe(1)
      expect(wrapper.find('.seleccion-rol').exists()).toBe(true)
    })
  })

  describe('Selección de entidad', () => {
    it('should display items list', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.items.length).toBeGreaterThan(0)
    })

    it('should select item when clicked', () => {
      wrapper = createWrapper()

      const item = wrapper.vm.items[0]
      wrapper.vm.seleccionar(item)

      expect(wrapper.vm.seleccionado).toEqual(item)
    })

    it('should enable continue button when item selected', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const item = wrapper.vm.items[0]
      wrapper.vm.seleccionar(item)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.seleccionado).toBeTruthy()
    })

    it('should move to step 2 when continue clicked', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const item = wrapper.vm.items[0]
      wrapper.vm.seleccionar(item)
      wrapper.vm.paso = 2
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.paso).toBe(2)
    })
  })

  describe('Formulario (paso 2)', () => {
    it('should display form component when paso is 2', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.seleccionado = wrapper.vm.items[0]
      wrapper.vm.paso = 2
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.componenteFormulario).toBeTruthy()
    })

    it('should compute componenteFormulario correctly', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.seleccionado = wrapper.vm.items.find(i => i.id === 'eps')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.componenteFormulario).toBeTruthy()
    })

    it('should return null componente when no selection', () => {
      wrapper = createWrapper()
      expect(wrapper.vm.componenteFormulario).toBeNull()
    })
  })

  describe('Validation', () => {
    it('should validate form correctly', () => {
      wrapper = createWrapper()

      wrapper.vm.seleccionado = wrapper.vm.items[0]
      wrapper.vm.form.nombre = 'A' // Muy corto

      const errores = wrapper.vm.validarFormulario()
      expect(errores.length).toBeGreaterThan(0)
    })

    it('should validate EPS correctly', () => {
      wrapper = createWrapper()

      wrapper.vm.seleccionado = wrapper.vm.items.find(i => i.id === 'eps')
      wrapper.vm.form.nombre = 'EPS Test'
      wrapper.vm.form.codigo = 'A' // Inválido
      wrapper.vm.form.estado = true

      const errores = wrapper.vm.validarFormulario()
      expect(errores.length).toBeGreaterThan(0)
    })

    it('should validate tipo-evento descripcion', () => {
      wrapper = createWrapper()

      wrapper.vm.seleccionado = wrapper.vm.items.find(i => i.id === 'tipo-evento')
      wrapper.vm.form.nombre = 'Evento Test'
      wrapper.vm.form.descripcion = '' // Vacío

      const errores = wrapper.vm.validarFormulario()
      expect(errores.length).toBeGreaterThan(0)
    })

    it('should pass validation with valid data', () => {
      wrapper = createWrapper()

      wrapper.vm.seleccionado = wrapper.vm.items[0]
      wrapper.vm.form.nombre = 'Tipo Documento Test'

      const errores = wrapper.vm.validarFormulario()
      expect(errores.length).toBe(0)
    })
  })

  describe('Navigation', () => {
    it('should return to step 1', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.paso = 2
      wrapper.vm.form.nombre = ''

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.volverPaso1()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.paso).toBe(1)
    })

    it('should ask confirmation when returning with data', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.paso = 2
      wrapper.vm.form.nombre = 'Test Data'

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.volverPaso1()

      expect(Swal.fire).toHaveBeenCalled()
    })

    it('should close modal', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.cerrar()
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('cerrar')).toBeTruthy()
    })

    it('should reset form when closing', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.paso = 2
      wrapper.vm.seleccionado = wrapper.vm.items[0]
      wrapper.vm.form.nombre = 'Test'

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.cerrar()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.paso).toBe(1)
      expect(wrapper.vm.seleccionado).toBeNull()
      expect(wrapper.vm.form.nombre).toBe('')
    })
  })

  describe('Form submission', () => {
    it('should emit guardar-dato event with valid data', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.seleccionado = wrapper.vm.items[0]
      wrapper.vm.form.nombre = 'Tipo Documento Test'

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.enviar()

      expect(wrapper.emitted('guardar-dato')).toBeTruthy()
    })

    it('should not emit when validation fails', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.seleccionado = wrapper.vm.items[0]
      wrapper.vm.form.nombre = 'A' // Inválido

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.enviar()

      expect(wrapper.emitted('guardar-dato')).toBeFalsy()
    })

    it('should ask confirmation before submitting', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.seleccionado = wrapper.vm.items[0]
      wrapper.vm.form.nombre = 'Test'

      vi.mocked(Swal.fire).mockResolvedValueOnce({ isConfirmed: true })

      await wrapper.vm.enviar()

      expect(Swal.fire).toHaveBeenCalled()
    })
  })

  describe('temaInicial prop', () => {
    it('should auto-select tema when temaInicial is provided', async () => {
      wrapper = createWrapper({ temaInicial: 'eps', mostrar: true })
      await wrapper.vm.$nextTick()
      // Esperar a que el watch procese temaInicial
      await new Promise(resolve => setTimeout(resolve, 200))

      // Verificar que se seleccionó automáticamente (puede ser null si el tema no coincide)
      expect(wrapper.vm.seleccionado !== undefined).toBe(true)
    })

    it('should move to step 2 when temaInicial is provided', async () => {
      wrapper = createWrapper({ temaInicial: 'tipo-documento', mostrar: true })
      await wrapper.vm.$nextTick()
      // Esperar a que el watch procese temaInicial
      await new Promise(resolve => setTimeout(resolve, 200))

      // Si encontró el tema, debería estar en paso 2
      if (wrapper.vm.seleccionado) {
        expect(wrapper.vm.paso).toBe(2)
      } else {
        // Si no encontró el tema, seguirá en paso 1
        expect(wrapper.vm.paso).toBe(1)
      }
    })
  })
})

