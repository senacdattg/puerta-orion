import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import AcudienteDashboard from '@/views/AcudienteDashboard.vue'

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

describe('AcudienteDashboard', () => {
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
    return mount(AcudienteDashboard, {
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
      expect(wrapper.find('.acudiente-dashboard-page').exists()).toBe(true)
    })

    it('should render Encabezado component', () => {
      wrapper = createWrapper()
      expect(wrapper.findComponent({ name: 'Encabezado' }).exists()).toBe(true)
    })

    it('should render TituloClub component', () => {
      wrapper = createWrapper()
      expect(wrapper.findComponent({ name: 'TituloClub' }).exists()).toBe(true)
    })

    it('should render FooterEnhanced component', () => {
      wrapper = createWrapper()
      expect(wrapper.findComponent({ name: 'FooterEnhanced' }).exists()).toBe(true)
    })

    it('should display dashboard title', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Panel del Acudiente')
    })

    it('should display dashboard subtitle', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Gestiona la información de tus acudidos')
    })
  })

  describe('Dashboard cards', () => {
    it('should render all dashboard cards', () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      expect(cards.length).toBe(5)
    })

    it('should render Mis Acudidos card', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Mis Acudidos')
      expect(wrapper.text()).toContain('Consulta y gestiona los deportistas asociados')
    })

    it('should render Mensualidades card', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Mensualidades')
      expect(wrapper.text()).toContain('Consulta el estado de pagos')
    })

    it('should render Eventos card', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Eventos')
      expect(wrapper.text()).toContain('Participa en los próximos eventos')
    })

    it('should render Calendario card', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Calendario')
      expect(wrapper.text()).toContain('Consulta el calendario completo')
    })

    it('should render Galería card', () => {
      wrapper = createWrapper()
      expect(wrapper.text()).toContain('Galería')
      expect(wrapper.text()).toContain('Explora las últimas imágenes')
    })
  })

  describe('Navegación', () => {
    it('should navigate to ver-acudidos when Mis Acudidos card is clicked', async () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      await cards[0].trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/acudiente/ver-acudidos')
    })

    it('should navigate to mensualidades when Mensualidades card is clicked', async () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      await cards[1].trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/mensualidades')
    })

    it('should navigate to eventos when Eventos card is clicked', async () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      await cards[2].trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/eventos')
    })

    it('should navigate to calendario when Calendario card is clicked', async () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      await cards[3].trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/calendario')
    })

    it('should navigate to galeria when Galería card is clicked', async () => {
      wrapper = createWrapper()
      const cards = wrapper.findAll('.dashboard-card')
      await cards[4].trigger('click')
      expect(mockRouter.push).toHaveBeenCalledWith('/galeria')
    })
  })

  describe('Lifecycle', () => {
    it('should log on mount', () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      wrapper = createWrapper()
      expect(consoleSpy).toHaveBeenCalledWith('✅ AcudienteDashboard montado')
      consoleSpy.mockRestore()
    })
  })
})

