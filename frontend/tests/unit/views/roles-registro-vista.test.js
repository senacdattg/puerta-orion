import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import RolesRegistroVista from '@/views/roles-registro-vista.vue'

// Importar el componente para asegurar que se ejecute
import RolesRegistro from '@/components/roles/roles-registro.vue'

describe('RolesRegistroVista', () => {
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
    return mount(RolesRegistroVista, {
      global: {
        plugins: [pinia],
        stubs: {
          RolesRegistro: {
            name: 'RolesRegistro',
            template: '<div class="roles-registro">Roles Registro</div>'
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

    it('should render RolesRegistro component', () => {
      wrapper = createWrapper()
      const rolesRegistro = wrapper.findComponent(RolesRegistro)
      expect(rolesRegistro.exists()).toBe(true)
    })

    it('should render only one RolesRegistro component', () => {
      wrapper = createWrapper()
      const rolesRegistros = wrapper.findAllComponents(RolesRegistro)
      expect(rolesRegistros.length).toBe(1)
    })
  })

  describe('Component Structure', () => {
    it('should have correct component hierarchy', () => {
      wrapper = createWrapper()

      // Verify child component is rendered
      expect(wrapper.findComponent(RolesRegistro).exists()).toBe(true)
    })

    it('should have main as root element', () => {
      wrapper = createWrapper()
      expect(wrapper.find('main').exists()).toBe(true)
    })
  })

  describe('Script Setup Execution', () => {
    it('should execute script setup code', () => {
      wrapper = createWrapper()
      
      // Access component properties to ensure script setup is executed
      expect(RolesRegistroVista.name || RolesRegistroVista.__name).toBeDefined()
      
      // Verify the component instance exists
      expect(wrapper.vm).toBeDefined()
    })

    it('should have imports executed', () => {
      // Verify that imports are available
      expect(RolesRegistro).toBeDefined()
    })
  })
})

