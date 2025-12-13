import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ListaDeportistas from '@/components/deportistas/lista-deportistas.vue'
import TarjetaDeportista from '@/components/deportistas/tarjeta-deportista.vue'
import catalogosService from '@/services/catalogosService'

// Mock catalogosService
vi.mock('@/services/catalogosService', () => ({
  default: {
    getCategorias: vi.fn()
  }
}))

// Mock TarjetaDeportista
vi.mock('@/components/deportistas/tarjeta-deportista.vue', () => ({
  default: {
    name: 'TarjetaDeportista',
    props: ['deportista'],
    emits: ['editar', 'eliminar', 'ver', 'cambiar-estado'],
    template: '<div class="tarjeta-deportista">{{ deportista.nombre }}</div>'
  }
}))

describe('ListaDeportistas', () => {
  let pinia
  let wrapper

  const mockDeportistas = [
    {
      id: 1,
      nombre: 'Juan Pérez',
      estado: 'activo',
      categoria: 'pre-benjamin',
      categoria_info: { nombre_categoria: 'Pre-Benjamin' }
    },
    {
      id: 2,
      nombre: 'María García',
      estado: 'activo',
      categoria: 'benjamin',
      categoria_info: { nombre_categoria: 'Benjamin' }
    },
    {
      id: 3,
      nombre: 'Carlos López',
      estado: 'inactivo',
      categoria: 'pre-benjamin',
      categoria_info: { nombre_categoria: 'Pre-Benjamin' }
    }
  ]

  const mockCategorias = [
    { id_categoria: 1, nombre_categoria: 'Pre-Benjamin' },
    { id_categoria: 2, nombre_categoria: 'Benjamin' },
    { id_categoria: 3, nombre_categoria: 'Alevín' }
  ]

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    catalogosService.getCategorias.mockResolvedValue(mockCategorias)
    vi.clearAllMocks()
  })

  const createWrapper = (props = {}) => {
    return mount(ListaDeportistas, {
      props: {
        deportistas: mockDeportistas,
        ...props
      },
      global: {
        plugins: [pinia]
      }
    })
  }

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.lista-deportistas').exists()).toBe(true)
    })

    it('should render search input', () => {
      wrapper = createWrapper()
      const searchInput = wrapper.find('.entrada-busqueda')
      expect(searchInput.exists()).toBe(true)
      expect(searchInput.attributes('placeholder')).toBe('Buscar deportistas...')
    })

    it('should render filter selects', () => {
      wrapper = createWrapper()
      const categoriaSelect = wrapper.find('.filtro-select')
      expect(categoriaSelect.exists()).toBe(true)
    })

    it('should render statistics cards', () => {
      wrapper = createWrapper()
      expect(wrapper.find('.stat-total').exists()).toBe(true)
      expect(wrapper.find('.stat-activos').exists()).toBe(true)
      expect(wrapper.find('.stat-inactivos').exists()).toBe(true)
    })
  })

  describe('Data Loading', () => {
    it('should load categorias on mount', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(catalogosService.getCategorias).toHaveBeenCalled()
      expect(wrapper.vm.categorias.length).toBeGreaterThan(0)
    })

    it('should handle error when loading categorias fails', async () => {
      catalogosService.getCategorias.mockRejectedValue(new Error('Network error'))
      
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(catalogosService.getCategorias).toHaveBeenCalled()
      expect(wrapper.vm.categorias).toEqual([])
      expect(wrapper.vm.cargandoCategorias).toBe(false)
    })

    it('should filter invalid categorias', async () => {
      const invalidCategorias = [
        { id_categoria: 1, nombre_categoria: 'Valid' },
        { id_categoria: 2 }, // Missing nombre_categoria
        { id_categoria: 3, nombre_categoria: 'Also Valid' }
      ]
      
      catalogosService.getCategorias.mockResolvedValue(invalidCategorias)
      
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.vm.categorias.length).toBe(2)
    })
  })

  describe('Filtering', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should filter by search term', async () => {
      wrapper.vm.busqueda = 'Juan'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.deportistasFiltrados.length).toBe(1)
      expect(wrapper.vm.deportistasFiltrados[0].nombre).toBe('Juan Pérez')
    })

    it('should filter by categoria', async () => {
      wrapper.vm.filtroCategoria = 'pre-benjamin'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.deportistasFiltrados.length).toBe(2)
    })

    it('should filter by estado', async () => {
      wrapper.vm.filtroEstado = 'activo'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.deportistasFiltrados.length).toBe(2)
      expect(wrapper.vm.deportistasFiltrados.every(d => d.estado === 'activo')).toBe(true)
    })

    it('should combine multiple filters', async () => {
      wrapper.vm.busqueda = 'Juan'
      wrapper.vm.filtroEstado = 'activo'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.deportistasFiltrados.length).toBe(1)
      expect(wrapper.vm.deportistasFiltrados[0].nombre).toBe('Juan Pérez')
    })

    it('should show empty state when no results', async () => {
      wrapper.vm.busqueda = 'No existe'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.deportistasFiltrados.length).toBe(0)
      expect(wrapper.find('.sin-resultados').exists()).toBe(true)
    })
  })

  describe('Statistics', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should calculate total deportistas', () => {
      expect(wrapper.vm.deportistasFiltrados.length).toBe(3)
      expect(wrapper.find('.stat-total .stat-numero').text()).toBe('3')
    })

    it('should calculate active deportistas', () => {
      expect(wrapper.vm.deportistasActivos).toBe(2)
      expect(wrapper.find('.stat-activos .stat-numero').text()).toBe('2')
    })

    it('should calculate inactive deportistas', () => {
      expect(wrapper.vm.deportistasInactivos).toBe(1)
      expect(wrapper.find('.stat-inactivos .stat-numero').text()).toBe('1')
    })
  })

  describe('Helper Functions', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should normalizarCategoria correctly', () => {
      expect(wrapper.vm.normalizarCategoria('Pre-Benjamin')).toBe('pre-benjamin')
      expect(wrapper.vm.normalizarCategoria('  BENJAMIN  ')).toBe('benjamin')
      expect(wrapper.vm.normalizarCategoria(null)).toBe('')
      expect(wrapper.vm.normalizarCategoria('')).toBe('')
    })
  })

  describe('Event Emissions', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should emit editar event', () => {
      const deportista = mockDeportistas[0]
      wrapper.vm.editarDeportista(deportista)

      expect(wrapper.emitted('editar')).toBeTruthy()
      expect(wrapper.emitted('editar')[0][0]).toEqual(deportista)
    })

    it('should emit eliminar event', () => {
      const deportista = mockDeportistas[0]
      wrapper.vm.eliminarDeportista(deportista)

      expect(wrapper.emitted('eliminar')).toBeTruthy()
      expect(wrapper.emitted('eliminar')[0][0]).toEqual(deportista)
    })

    it('should emit ver event', () => {
      const deportista = mockDeportistas[0]
      wrapper.vm.verDeportista(deportista)

      expect(wrapper.emitted('ver')).toBeTruthy()
      expect(wrapper.emitted('ver')[0][0]).toEqual(deportista)
    })

    it('should emit cambiar-estado event', () => {
      const deportista = mockDeportistas[0]
      wrapper.vm.cambiarEstadoDeportista(deportista)

      expect(wrapper.emitted('cambiar-estado')).toBeTruthy()
      expect(wrapper.emitted('cambiar-estado')[0][0]).toEqual(deportista)
    })
  })

  describe('Clear Filters', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('should clear all filters', () => {
      wrapper.vm.busqueda = 'test'
      wrapper.vm.filtroCategoria = 'benjamin'
      wrapper.vm.filtroEstado = 'activo'

      wrapper.vm.limpiarFiltros()

      expect(wrapper.vm.busqueda).toBe('')
      expect(wrapper.vm.filtroCategoria).toBe('')
      expect(wrapper.vm.filtroEstado).toBe('')
    })

    it('should show clear filters button when no results', async () => {
      wrapper.vm.busqueda = 'No existe'
      await wrapper.vm.$nextTick()

      const clearButton = wrapper.find('.btn-primary')
      expect(clearButton.exists()).toBe(true)
      expect(clearButton.text()).toBe('Limpiar filtros')
    })

    it('should clear filters when button is clicked', async () => {
      wrapper.vm.busqueda = 'No existe'
      wrapper.vm.filtroCategoria = 'benjamin'
      wrapper.vm.filtroEstado = 'activo'
      await wrapper.vm.$nextTick()

      const clearButton = wrapper.find('.btn-primary')
      await clearButton.trigger('click')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.busqueda).toBe('')
      expect(wrapper.vm.filtroCategoria).toBe('')
      expect(wrapper.vm.filtroEstado).toBe('')
    })
  })

  describe('Category Filtering', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('should use categoria_info.nombre_categoria when available', async () => {
      wrapper.vm.filtroCategoria = 'pre-benjamin'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.deportistasFiltrados.length).toBe(2)
    })

    it('should fallback to categoria when categoria_info is not available', async () => {
      const deportistasSinInfo = [
        { id: 1, nombre: 'Test', estado: 'activo', categoria: 'benjamin' }
      ]
      
      wrapper = createWrapper({ deportistas: deportistasSinInfo })
      await wrapper.vm.$nextTick()
      
      wrapper.vm.filtroCategoria = 'benjamin'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.deportistasFiltrados.length).toBe(1)
    })
  })

  describe('Component Props', () => {
    it('should use provided deportistas', () => {
      const customDeportistas = [{ id: 1, nombre: 'Custom', estado: 'activo' }]
      wrapper = createWrapper({ deportistas: customDeportistas })

      expect(wrapper.vm.deportistasFiltrados.length).toBe(1)
      expect(wrapper.vm.deportistasFiltrados[0].nombre).toBe('Custom')
    })

    it('should handle empty deportistas array', () => {
      wrapper = createWrapper({ deportistas: [] })

      expect(wrapper.vm.deportistasFiltrados.length).toBe(0)
      expect(wrapper.vm.deportistasActivos).toBe(0)
      expect(wrapper.vm.deportistasInactivos).toBe(0)
    })
  })

  describe('TarjetaDeportista Integration', () => {
    it('should render TarjetaDeportista for each deportista', () => {
      wrapper = createWrapper()
      const tarjetas = wrapper.findAllComponents(TarjetaDeportista)
      
      expect(tarjetas.length).toBe(3)
    })

    it('should pass deportista prop to TarjetaDeportista', () => {
      wrapper = createWrapper()
      const primeraTarjeta = wrapper.findAllComponents(TarjetaDeportista)[0]
      
      expect(primeraTarjeta.props('deportista')).toEqual(mockDeportistas[0])
    })

    it('should handle events from TarjetaDeportista', async () => {
      wrapper = createWrapper()
      const primeraTarjeta = wrapper.findAllComponents(TarjetaDeportista)[0]
      
      await primeraTarjeta.vm.$emit('editar', mockDeportistas[0])
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('editar')).toBeTruthy()
    })
  })
})

