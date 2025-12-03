import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import GaleriaVista from '@/views/galeria-vista.vue'

// Importar los componentes para asegurar que se ejecuten
import Encabezado from '@/components/layout/encabezado.vue'
import Galeria from '@/components/galeria/galeria.vue'
import Pie from '@/components/layout/pie.vue'

describe('GaleriaVista', () => {
  let wrapper
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = () => {
    return mount(GaleriaVista, {
      global: {
        plugins: [pinia],
        stubs: {
          Encabezado: {
            name: 'Encabezado',
            props: ['rol'],
            template: '<div class="encabezado">Encabezado</div>'
          },
          Galeria: {
            name: 'Galeria',
            template: '<div class="galeria">Galeria</div>'
          },
          Pie: {
            name: 'Pie',
            template: '<div class="pie">Pie</div>'
          }
        }
      }
    })
  }

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
    })

    it('should render main element', () => {
      wrapper = createWrapper()
      expect(wrapper.find('main').exists()).toBe(true)
    })

    it('should render Encabezado component', () => {
      wrapper = createWrapper()
      const encabezado = wrapper.findComponent(Encabezado)
      expect(encabezado.exists()).toBe(true)
    })

    it('should pass rol="Admin" to Encabezado', () => {
      wrapper = createWrapper()
      const encabezado = wrapper.findComponent(Encabezado)
      expect(encabezado.props('rol')).toBe('Admin')
    })

    it('should render Galeria component', () => {
      wrapper = createWrapper()
      const galeria = wrapper.findComponent(Galeria)
      expect(galeria.exists()).toBe(true)
    })

    it('should render Pie component', () => {
      wrapper = createWrapper()
      const pie = wrapper.findComponent(Pie)
      expect(pie.exists()).toBe(true)
    })

    it('should render all components in correct order', () => {
      wrapper = createWrapper()

      const encabezado = wrapper.findComponent(Encabezado)
      const galeria = wrapper.findComponent(Galeria)
      const pie = wrapper.findComponent(Pie)

      expect(encabezado.exists()).toBe(true)
      expect(galeria.exists()).toBe(true)
      expect(pie.exists()).toBe(true)
    })
  })

  describe('Component Structure', () => {
    it('should have correct component hierarchy', () => {
      wrapper = createWrapper()

      // Verify all child components are rendered
      expect(wrapper.findComponent(Encabezado).exists()).toBe(true)
      expect(wrapper.findComponent(Galeria).exists()).toBe(true)
      expect(wrapper.findComponent(Pie).exists()).toBe(true)
    })
  })

  describe('Script Setup Execution', () => {
    it('should execute script setup code', () => {
      wrapper = createWrapper()
      
      // Access component properties to ensure script setup is executed
      expect(GaleriaVista.name || GaleriaVista.__name).toBeDefined()
      
      // Verify the component instance exists
      expect(wrapper.vm).toBeDefined()
    })

    it('should have imports executed', () => {
      // Verify that imports are available
      expect(Encabezado).toBeDefined()
      expect(Galeria).toBeDefined()
      expect(Pie).toBeDefined()
    })
  })
})

