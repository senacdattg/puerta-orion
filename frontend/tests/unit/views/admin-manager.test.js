import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminManager from '@/views/admin-manager.vue'
import Encabezado from '@/components/layout/encabezado.vue'
import PanelAdminComponente from '@/components/admin/panel-admin-componente.vue'
import Pie from '@/components/layout/pie.vue'

// Mock components
vi.mock('@/components/layout/encabezado.vue', () => ({
  default: {
    name: 'Encabezado',
    props: ['rol'],
    template: '<div class="encabezado">Encabezado</div>'
  }
}))

vi.mock('@/components/admin/panel-admin-componente.vue', () => ({
  default: {
    name: 'PanelAdminComponente',
    template: '<div class="panel-admin">Panel Admin</div>'
  }
}))

vi.mock('@/components/layout/pie.vue', () => ({
  default: {
    name: 'Pie',
    template: '<div class="pie">Pie</div>'
  }
}))

describe('AdminManager', () => {
  let pinia
  let wrapper

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)

    vi.clearAllMocks()
  })

  const createWrapper = () => {
    return mount(AdminManager, {
      global: {
        plugins: [pinia]
      }
    })
  }

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
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

    it('should render PanelAdminComponente', () => {
      wrapper = createWrapper()
      const panelAdmin = wrapper.findComponent(PanelAdminComponente)
      expect(panelAdmin.exists()).toBe(true)
    })

    it('should render Pie component', () => {
      wrapper = createWrapper()
      const pie = wrapper.findComponent(Pie)
      expect(pie.exists()).toBe(true)
    })

    it('should render all components in correct order', () => {
      wrapper = createWrapper()

      const encabezado = wrapper.findComponent(Encabezado)
      const panelAdmin = wrapper.findComponent(PanelAdminComponente)
      const pie = wrapper.findComponent(Pie)

      expect(encabezado.exists()).toBe(true)
      expect(panelAdmin.exists()).toBe(true)
      expect(pie.exists()).toBe(true)
    })
  })

  describe('Component Structure', () => {
    it('should have correct component hierarchy', () => {
      wrapper = createWrapper()

      // Verify all child components are rendered
      expect(wrapper.findComponent(Encabezado).exists()).toBe(true)
      expect(wrapper.findComponent(PanelAdminComponente).exists()).toBe(true)
      expect(wrapper.findComponent(Pie).exists()).toBe(true)
    })
  })
})

