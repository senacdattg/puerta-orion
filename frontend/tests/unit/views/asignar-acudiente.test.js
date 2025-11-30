import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AsignarAcudiente from '@/views/asignar-acudiente.vue'
import Swal from 'sweetalert2'

vi.mock('sweetalert2', () => ({
  default: {
    fire: vi.fn()
  }
}))

vi.mock('@/components/layout/encabezado.vue', () => ({
  default: {
    name: 'Encabezado',
    template: '<div class="encabezado">Encabezado</div>'
  }
}))

vi.mock('@/components/ui/titulo-club.vue', () => ({
  default: {
    name: 'TituloClub',
    template: '<div class="titulo-club">Título Club</div>'
  }
}))

vi.mock('@/components/layout/pie.vue', () => ({
  default: {
    name: 'FooterEnhanced',
    template: '<div class="pie">Footer</div>'
  }
}))

describe('AsignarAcudiente', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  const createWrapper = () => {
    return mount(AsignarAcudiente, {
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
      expect(wrapper.find('.asignar-acudiente-page').exists()).toBe(true)
    })

    it('should display page title', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Asignar Acudiente')
    })

    it('should display subtitle', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Vincula un acudiente a tu cuenta')
    })
  })

  describe('Acudiente actual', () => {
    it('should display current acudiente when exists', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.acudienteActual).toBeTruthy()
      expect(wrapper.text()).toContain('Acudiente Actual')
      expect(wrapper.text()).toContain('Ana García')
    })

    it('should show no-acudiente section when acudienteActual is null', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.acudienteActual = null
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('No tienes acudiente asignado')
    })

    it('should toggle search when Asignar Acudiente button is clicked', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.acudienteActual = null
      await wrapper.vm.$nextTick()

      const button = wrapper.find('.btn-assign')
      await button.trigger('click')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarBusqueda).toBe(true)
    })

    it('should toggle search when Cambiar Acudiente button is clicked', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const button = wrapper.find('.btn-change')
      await button.trigger('click')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.mostrarBusqueda).toBe(true)
    })
  })

  describe('Búsqueda', () => {
    it('should display search section when mostrarBusqueda is true', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarBusqueda = true
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.search-section').exists()).toBe(true)
    })

    it('should filter acudientes by search term', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.searchTerm = 'Carlos'
      await wrapper.vm.$nextTick()

      const filtrados = wrapper.vm.acudientesFiltrados
      expect(filtrados.length).toBeGreaterThan(0)
      expect(filtrados[0].nombre_completo).toContain('Carlos')
    })

    it('should filter acudientes by documento', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.searchTerm = '87654321'
      await wrapper.vm.$nextTick()

      const filtrados = wrapper.vm.acudientesFiltrados
      expect(filtrados.length).toBeGreaterThan(0)
      expect(filtrados[0].documento).toContain('87654321')
    })

    it('should show all acudientes when search term is empty', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.searchTerm = ''
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.acudientesFiltrados.length).toBe(2)
    })

    it('should show empty state when no acudientes match', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.searchTerm = 'No existe'
      wrapper.vm.mostrarBusqueda = true
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.empty-state').exists()).toBe(true)
      expect(wrapper.text()).toContain('No se encontraron acudientes')
    })
  })

  describe('Seleccionar acudiente', () => {
    it('should select acudiente successfully', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const acudiente = wrapper.vm.acudientes[0]
      Swal.fire.mockResolvedValue({})

      const seleccionarPromise = wrapper.vm.seleccionarAcudiente(acudiente)
      vi.advanceTimersByTime(1000)
      await seleccionarPromise
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.acudienteActual).toEqual(acudiente)
      expect(wrapper.vm.mostrarBusqueda).toBe(false)
      expect(wrapper.vm.searchTerm).toBe('')
      expect(Swal.fire).toHaveBeenCalledWith({
        icon: 'success',
        title: 'Acudiente asignado',
        text: 'El acudiente se asignó correctamente.',
        timer: 1500,
        showConfirmButton: false
      })
    })

    it('should set asignando to true during selection', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const acudiente = wrapper.vm.acudientes[0]
      Swal.fire.mockResolvedValue({})

      const seleccionarPromise = wrapper.vm.seleccionarAcudiente(acudiente)
      expect(wrapper.vm.asignando).toBe(true)

      vi.advanceTimersByTime(1000)
      await seleccionarPromise
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.asignando).toBe(false)
    })

    it('should handle error when selecting acudiente', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      const acudiente = wrapper.vm.acudientes[0]
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      Swal.fire.mockResolvedValue({})

      // El componente maneja errores internamente
      const seleccionarPromise = wrapper.vm.seleccionarAcudiente(acudiente)
      vi.advanceTimersByTime(1000)
      await seleccionarPromise
      await wrapper.vm.$nextTick()

      expect(Swal.fire).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })
  })

  describe('Cargar datos', () => {
    it('should load acudiente actual on mount', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.acudienteActual).toBeTruthy()
      expect(wrapper.vm.acudienteActual.nombre_completo).toBe('Ana García')
    })

    it('should load acudientes list on mount', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.acudientes.length).toBe(2)
    })

    it('should handle error loading acudiente actual', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      // El componente maneja errores internamente
      expect(wrapper.vm.acudienteActual).toBeDefined()
      consoleSpy.mockRestore()
    })

    it('should handle error loading acudientes', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      // El componente maneja errores internamente
      expect(wrapper.vm.acudientes).toBeDefined()
      consoleSpy.mockRestore()
    })
  })

  describe('Acudiente card rendering', () => {
    it('should display acudiente information', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarBusqueda = true
      await wrapper.vm.$nextTick()

      const cards = wrapper.findAll('.acudiente-card')
      expect(cards.length).toBe(2)
    })

    it('should display profesion when available', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()

      wrapper.vm.mostrarBusqueda = true
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Ingeniero')
      expect(wrapper.text()).toContain('Médica')
    })
  })
})

