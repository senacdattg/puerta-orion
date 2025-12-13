import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import BasicDashboard from '@/components/ui/basic-dashboard.vue'

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

describe('BasicDashboard', () => {
  let wrapper
  let router

  beforeEach(() => {
    vi.clearAllMocks()
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } }
      ]
    })
  })

  const createWrapper = () => {
    return mount(BasicDashboard, {
      global: {
        plugins: [router],
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
      expect(wrapper.find('.basic-dashboard').exists()).toBe(true)
    })

    it('should display dashboard title', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Bienvenido')
    })

    it('should display dashboard subtitle', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Accede a las funcionalidades básicas')
    })
  })

  describe('Dashboard cards', () => {
    it('should render all dashboard cards', () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      expect(cards.length).toBe(2)
    })

    it('should render Calendario card', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Calendario')
      expect(wrapper.text()).toContain('Consulta las actividades del club')
    })

    it('should render Galería card', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Galería')
      expect(wrapper.text()).toContain('Ve las fotos de eventos')
    })
  })

  describe('Navegación', () => {
    it('should navigate to calendario when Calendario card is clicked', async () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      await cards[0].trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/calendario')
    })

    it('should navigate to galeria when Galería card is clicked', async () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      await cards[1].trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/galeria')
    })
  })
})

