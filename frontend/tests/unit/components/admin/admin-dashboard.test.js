import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import AdminDashboard from '@/components/admin/admin-dashboard.vue'

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

describe('AdminDashboard', () => {
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
    return mount(AdminDashboard, {
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
      expect(wrapper.find('.admin-dashboard').exists()).toBe(true)
    })

    it('should display dashboard title', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Panel de Administración')
    })

    it('should display dashboard subtitle', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Gestiona el club deportivo')
    })
  })

  describe('Dashboard cards', () => {
    it('should render all dashboard cards', () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      expect(cards.length).toBe(2)
    })

    it('should render Gestionar Deportistas card', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Gestionar Deportistas')
      expect(wrapper.text()).toContain('Administra la información de deportistas')
    })

    it('should render Calendario card', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Calendario')
      expect(wrapper.text()).toContain('Gestiona eventos y actividades del club')
    })
  })

  describe('Navegación', () => {
    it('should navigate to deportistas when Gestionar Deportistas card is clicked', async () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      await cards[0].trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/deportistas')
    })

    it('should navigate to calendario when Calendario card is clicked', async () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      await cards[1].trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/calendario')
    })
  })
})

